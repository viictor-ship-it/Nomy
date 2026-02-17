from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("/rooms")
async def list_rooms(request: Request):
    rm = request.app.state.room_manager
    result = []
    for room_id, room_data in rm.rooms.items():
        room_info = room_data.get("room", {})
        device_ids = rm.get_room_devices(room_id)
        result.append({
            "id": room_id,
            "name": room_info.get("name", room_id),
            "description": room_info.get("description", ""),
            "device_count": len(device_ids),
        })
    return result


@router.get("/rooms/{room_id}")
async def get_room(room_id: str, request: Request):
    rm = request.app.state.room_manager
    room_data = rm.get_room(room_id)
    if not room_data:
        raise HTTPException(status_code=404, detail=f"Room {room_id!r} not found")

    room_info = room_data.get("room", {})
    device_ids = rm.get_room_devices(room_id)
    devices = []
    for did in device_ids:
        drv = rm.get_device(did)
        state = drv.state.model_dump() if drv else None
        dev_conf = next(
            (d for d in room_data.get("devices", []) if d["id"] == did), {}
        )
        devices.append({
            "id": did,
            "name": dev_conf.get("name", did),
            "type": dev_conf.get("type"),
            "driver": dev_conf.get("driver"),
            "state": state,
        })

    return {
        "id": room_id,
        "name": room_info.get("name", room_id),
        "description": room_info.get("description", ""),
        "devices": devices,
        "scenes": [s["name"] for s in room_data.get("scenes", [])],
    }


@router.post("/rooms/{room_id}/scene/{scene_name}")
async def activate_scene(room_id: str, scene_name: str, request: Request):
    rm = request.app.state.room_manager
    room_data = rm.get_room(room_id)
    if not room_data:
        raise HTTPException(status_code=404, detail=f"Room {room_id!r} not found")

    scenes = room_data.get("scenes", [])
    scene = next((s for s in scenes if s["name"] == scene_name), None)
    if not scene:
        raise HTTPException(status_code=404, detail=f"Scene {scene_name!r} not found")

    results = []
    for action in scene.get("actions", []):
        did = action["device"]
        cmd = action["command"]
        params = action.get("params", {})
        drv = rm.get_device(did)
        if drv:
            try:
                await drv.send_command(cmd, **params)
                results.append({"device": did, "ok": True})
            except Exception as e:
                results.append({"device": did, "ok": False, "error": str(e)})

    return {"scene": scene_name, "results": results}
