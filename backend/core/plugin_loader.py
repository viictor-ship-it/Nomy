import importlib
import logging
from typing import TYPE_CHECKING

from devices.base import DeviceDriver

if TYPE_CHECKING:
    from core.event_bus import EventBus

logger = logging.getLogger(__name__)

DRIVER_MAP = {
    "pjlink": "devices.display.pjlink.PJLinkDriver",
    # Future drivers registered here
}


class PluginLoader:
    def __init__(self, config: dict, event_bus: "EventBus"):
        self.config = config
        self.event_bus = event_bus

    def load_driver(self, device_id: str, device_config: dict) -> DeviceDriver:
        driver_name = device_config.get("driver")
        if driver_name not in DRIVER_MAP:
            raise ValueError(f"Unknown driver: {driver_name!r}. Available: {list(DRIVER_MAP)}")

        module_path, class_name = DRIVER_MAP[driver_name].rsplit(".", 1)
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        logger.info(f"Loaded driver {driver_name!r} for device {device_id!r}")
        return cls(device_id=device_id, config=device_config.get("config", {}))
