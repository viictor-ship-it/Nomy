from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Any

router = APIRouter()


class CommandRequest(BaseModel):
    command: str
    params: dict[str, Any] = {}


@router.get("/rooms/{room_id}/devices")
async def list_devices(room_id: str, request: Request):
    rm = request.app.state.room_manager
    room_data = rm.get_room(room_id)
    if not room_data:
        raise HTTPException(status_code=404, detail=f"Room {room_id!r} not found")

    results = []
    for dev_conf in room_data.get("devices", []):
        did = dev_conf["id"]
        drv = rm.get_device(did)
        results.append({
            "id": did,
            "name": dev_conf.get("name", did),
            "type": dev_conf.get("type"),
            "driver": dev_conf.get("driver"),
            "state": drv.state.model_dump() if drv else None,
        })
    return results


@router.get("/rooms/{room_id}/devices/{device_id}")
async def get_device(room_id: str, device_id: str, request: Request):
    rm = request.app.state.room_manager
    room_data = rm.get_room(room_id)
    if not room_data:
        raise HTTPException(status_code=404, detail=f"Room {room_id!r} not found")

    drv = rm.get_device(device_id)
    if not drv:
        raise HTTPException(status_code=404, detail=f"Device {device_id!r} not found")

    dev_conf = next(
        (d for d in room_data.get("devices", []) if d["id"] == device_id), {}
    )
    return {
        "id": device_id,
        "name": dev_conf.get("name", device_id),
        "type": dev_conf.get("type"),
        "driver": dev_conf.get("driver"),
        "state": drv.state.model_dump(),
    }


@router.post("/rooms/{room_id}/devices/{device_id}/command")
async def send_command(room_id: str, device_id: str, body: CommandRequest, request: Request):
    rm = request.app.state.room_manager
    drv = rm.get_device(device_id)
    if not drv:
        raise HTTPException(status_code=404, detail=f"Device {device_id!r} not found")

    try:
        result = await drv.send_command(body.command, **body.params)
        return {"ok": True, "result": str(result) if result is not None else None}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Device error: {e}")
