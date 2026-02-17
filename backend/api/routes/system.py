import platform
import sys
from datetime import datetime, timezone

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/system/status")
async def system_status(request: Request):
    room_manager = request.app.state.room_manager
    rooms = list(room_manager.rooms.keys())
    device_statuses = {
        did: drv.state.status.value
        for did, drv in room_manager.devices.items()
    }
    return {
        "version": "0.1.0",
        "python": sys.version,
        "platform": platform.system(),
        "rooms": rooms,
        "devices": device_statuses,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
