import asyncio
import hashlib
import logging
from typing import Any, Optional

from devices.base import DeviceDriver, DeviceState, DeviceStatus

logger = logging.getLogger(__name__)

PJLINK_PORT = 4352
PJLINK_TIMEOUT = 5.0


class PJLinkDriver(DeviceDriver):
    """PJLink Class 1 display/projector driver (TCP, async)."""

    POWER_STATES = {
        "0": False,   # off
        "1": True,    # on
        "2": None,    # warming
        "3": None,    # cooling
    }

    def __init__(self, device_id: str, config: dict):
        super().__init__(device_id, config)
        self.host: str = config.get("host", "127.0.0.1")
        self.port: int = int(config.get("port", PJLINK_PORT))
        self.password: str = config.get("password", "")
        self._lock = asyncio.Lock()

    async def connect(self) -> bool:
        try:
            await self._send_raw("%1NAME ?")
            self._state.status = DeviceStatus.ONLINE
            logger.info(f"PJLink {self.device_id} connected at {self.host}:{self.port}")
            return True
        except Exception as e:
            self._state.status = DeviceStatus.OFFLINE
            logger.warning(f"PJLink {self.device_id} connect failed: {e}")
            return False

    async def disconnect(self) -> None:
        pass  # PJLink is connectionless (new TCP conn per command)

    async def get_state(self) -> DeviceState:
        try:
            power_resp = await self._command("POWR", "?")
            power_str = power_resp.strip()
            power = self.POWER_STATES.get(power_str)

            extra: dict[str, Any] = {"raw_power": power_str}

            if power is True:
                try:
                    inp = await self._command("INPT", "?")
                    extra["input"] = inp.strip()
                except Exception:
                    pass
                try:
                    lamp = await self._command("LAMP", "?")
                    parts = lamp.strip().split()
                    if parts:
                        extra["lamp_hours"] = int(parts[0])
                except Exception:
                    pass

            return DeviceState(
                status=DeviceStatus.ONLINE,
                power=power,
                extra=extra,
            )
        except Exception as e:
            logger.debug(f"PJLink get_state failed for {self.device_id}: {e}")
            return DeviceState(status=DeviceStatus.OFFLINE)

    async def send_command(self, command: str, **kwargs) -> Any:
        cmd = command.lower()
        if cmd == "power_on":
            return await self._command("POWR", "1")
        elif cmd == "power_off":
            return await self._command("POWR", "0")
        elif cmd == "input":
            inp = str(kwargs.get("input", "31"))
            return await self._command("INPT", inp)
        elif cmd == "mute_on":
            return await self._command("AVMT", "31")
        elif cmd == "mute_off":
            return await self._command("AVMT", "30")
        elif cmd == "query_power":
            return await self._command("POWR", "?")
        else:
            raise ValueError(f"Unknown command: {command!r}")

    async def _command(self, cmd: str, param: str) -> str:
        raw = await self._send_raw(f"%1{cmd} {param}")
        prefix = f"%1{cmd}="
        if raw.startswith(prefix):
            return raw[len(prefix):]
        return raw

    async def _send_raw(self, message: str) -> str:
        async with self._lock:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=PJLINK_TIMEOUT,
            )
            try:
                greeting = await asyncio.wait_for(reader.readline(), timeout=PJLINK_TIMEOUT)
                greeting = greeting.decode("ascii", errors="ignore").strip()

                auth_prefix = ""
                if greeting.startswith("PJLINK 1"):
                    token = greeting.split()[-1] if len(greeting.split()) > 2 else ""
                    if token and self.password:
                        md5 = hashlib.md5((token + self.password).encode()).hexdigest()
                        auth_prefix = md5
                    elif token and not self.password:
                        auth_prefix = ""

                payload = f"{auth_prefix}{message}" + chr(13) + chr(10)
                writer.write(payload.encode("ascii"))
                await writer.drain()

                response = await asyncio.wait_for(reader.readline(), timeout=PJLINK_TIMEOUT)
                return response.decode("ascii", errors="ignore").strip()
            finally:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass
