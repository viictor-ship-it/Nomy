import asyncio
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, room_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.setdefault(room_id, []).append(ws)
        logger.info(f"WS connected: room={room_id}, total={len(self._connections[room_id])}")

    def disconnect(self, room_id: str, ws: WebSocket) -> None:
        room_conns = self._connections.get(room_id, [])
        if ws in room_conns:
            room_conns.remove(ws)
        logger.info(f"WS disconnected: room={room_id}")

    async def broadcast(self, room_id: str, message: dict) -> None:
        conns = self._connections.get(room_id, [])
        dead = []
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(room_id, ws)


manager = ConnectionManager()


@router.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    app = websocket.app
    room_manager = app.state.room_manager
    event_bus = app.state.event_bus

    room = room_manager.get_room(room_id)
    if not room:
        await websocket.close(code=4004, reason=f"Room {room_id!r} not found")
        return

    await manager.connect(room_id, websocket)

    room_devices = set(room_manager.get_room_devices(room_id))

    async def on_device_update(data: dict):
        if data["device_id"] in room_devices:
            await manager.broadcast(room_id, {
                "type": "device_state_update",
                "device_id": data["device_id"],
                "state": data["state"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    event_bus.subscribe("device_state_update", on_device_update)

    # Send initial state snapshot
    snapshot = {}
    for did in room_devices:
        driver = room_manager.get_device(did)
        if driver:
            snapshot[did] = driver.state.model_dump()
    await websocket.send_json({"type": "snapshot", "states": snapshot})

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            await _handle_client_message(msg, room_id, room_manager, websocket)
    except WebSocketDisconnect:
        pass
    finally:
        event_bus.unsubscribe("device_state_update", on_device_update)
        manager.disconnect(room_id, websocket)


async def _handle_client_message(msg: dict, room_id: str, room_manager, websocket: WebSocket):
    msg_type = msg.get("type")

    if msg_type == "command":
        device_id = msg.get("device_id")
        command = msg.get("command")
        params = msg.get("params", {})
        driver = room_manager.get_device(device_id)
        if not driver:
            await websocket.send_json({"type": "error", "message": f"Device {device_id!r} not found"})
            return
        try:
            result = await driver.send_command(command, **params)
            await websocket.send_json({"type": "command_result", "device_id": device_id, "result": str(result)})
        except Exception as e:
            await websocket.send_json({"type": "error", "message": str(e)})

    elif msg_type == "scene":
        scene_name = msg.get("scene_name")
        room_data = room_manager.get_room(room_id)
        scenes = room_data.get("scenes", []) if room_data else []
        scene = next((s for s in scenes if s["name"] == scene_name), None)
        if not scene:
            await websocket.send_json({"type": "error", "message": f"Scene {scene_name!r} not found"})
            return
        results = []
        for action in scene.get("actions", []):
            did = action["device"]
            cmd = action["command"]
            params = action.get("params", {})
            driver = room_manager.get_device(did)
            if driver:
                try:
                    await driver.send_command(cmd, **params)
                    results.append({"device": did, "ok": True})
                except Exception as e:
                    results.append({"device": did, "ok": False, "error": str(e)})
        await websocket.send_json({"type": "scene_result", "scene": scene_name, "results": results})
