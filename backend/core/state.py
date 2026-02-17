import asyncio
import logging
from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler

if TYPE_CHECKING:
    from core.event_bus import EventBus
    from core.plugin_loader import PluginLoader
    from devices.base import DeviceDriver

logger = logging.getLogger(__name__)


class RoomStateManager:
    """Manages all rooms and their devices. Polls device state periodically."""

    def __init__(self, config: dict, plugin_loader: "PluginLoader", event_bus: "EventBus"):
        self.config = config
        self.plugin_loader = plugin_loader
        self.event_bus = event_bus
        self.rooms: dict[str, dict] = {}
        self.devices: dict[str, "DeviceDriver"] = {}
        self._scheduler = AsyncIOScheduler()
        self._poll_interval = config.get("poll_interval", 10)

    async def startup(self) -> None:
        """Initialize all rooms and connect to devices."""
        for room_id, room_data in self.config.get("rooms", {}).items():
            self.rooms[room_id] = room_data
            for device_conf in room_data.get("devices", []):
                device_id = device_conf["id"]
                try:
                    driver = self.plugin_loader.load_driver(device_id, device_conf)
                    self.devices[device_id] = driver
                    await driver.connect()
                    logger.info(f"Connected to device {device_id!r}")
                except Exception as e:
                    logger.warning(f"Failed to connect device {device_id!r}: {e}")

        self._scheduler.add_job(
            self._poll_all_devices,
            "interval",
            seconds=self._poll_interval,
            id="poll_devices",
        )
        self._scheduler.start()
        logger.info("RoomStateManager started")

    async def shutdown(self) -> None:
        """Disconnect all devices and stop scheduler."""
        self._scheduler.shutdown(wait=False)
        for device_id, driver in self.devices.items():
            try:
                await driver.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting {device_id}: {e}")
        logger.info("RoomStateManager stopped")

    async def _poll_all_devices(self) -> None:
        tasks = [self._poll_device(did, drv) for did, drv in self.devices.items()]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _poll_device(self, device_id: str, driver: "DeviceDriver") -> None:
        try:
            state = await driver.poll()
            await self.event_bus.publish("device_state_update", {
                "device_id": device_id,
                "state": state.model_dump(),
            })
        except Exception as e:
            logger.debug(f"Poll failed for {device_id}: {e}")

    def get_room(self, room_id: str) -> dict | None:
        return self.rooms.get(room_id)

    def get_device(self, device_id: str) -> "DeviceDriver | None":
        return self.devices.get(device_id)

    def get_room_devices(self, room_id: str) -> list[str]:
        room = self.rooms.get(room_id)
        if not room:
            return []
        return [d["id"] for d in room.get("devices", [])]
