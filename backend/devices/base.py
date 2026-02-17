from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    UNKNOWN = "unknown"


class DeviceState(BaseModel):
    status: DeviceStatus = DeviceStatus.UNKNOWN
    power: Optional[bool] = None
    extra: dict[str, Any] = {}


class DeviceDriver(ABC):
    def __init__(self, device_id: str, config: dict):
        self.device_id = device_id
        self.config = config
        self._state = DeviceState()

    @abstractmethod
    async def connect(self) -> bool: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def get_state(self) -> DeviceState: ...

    @abstractmethod
    async def send_command(self, command: str, **kwargs) -> Any: ...

    @property
    def state(self) -> DeviceState:
        return self._state

    async def poll(self) -> DeviceState:
        self._state = await self.get_state()
        return self._state
