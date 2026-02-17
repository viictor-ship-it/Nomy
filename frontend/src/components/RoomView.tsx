import { useCallback, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { api } from "../services/api";
import { Device, DeviceState, Room, WsMessage } from "../types";
import { DeviceCard } from "./DeviceCard";
import { StatusBar } from "./StatusBar";
import { useRoomWebSocket } from "../hooks/useWebSocket";
import { Play } from "lucide-react";

interface Props {
  roomId: string;
}

export function RoomView({ roomId }: Props) {
  const [room, setRoom] = useState<Room | null>(null);
  const [deviceStates, setDeviceStates] = useState<Record<string, DeviceState>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getRoom(roomId).then((r) => {
      setRoom(r);
      const initial: Record<string, DeviceState> = {};
      r.devices.forEach((d) => { if (d.state) initial[d.id] = d.state; });
      setDeviceStates(initial);
      setLoading(false);
    }).catch(() => {
      toast.error("Failed to load room");
      setLoading(false);
    });
  }, [roomId]);

  const handleMessage = useCallback((msg: WsMessage) => {
    if (msg.type === "snapshot") {
      setDeviceStates(msg.states);
    } else if (msg.type === "device_state_update") {
      setDeviceStates((prev) => ({ ...prev, [msg.device_id]: msg.state }));
    } else if (msg.type === "error") {
      toast.error(msg.message);
    } else if (msg.type === "scene_result") {
      const failed = msg.results.filter((r) => !r.ok);
      if (failed.length === 0) toast.success(`Scene "${msg.scene}" activated`);
      else toast.error(`Scene "${msg.scene}": ${failed.length} error(s)`);
    }
  }, []);

  const { connected, send } = useRoomWebSocket(roomId, handleMessage);

  const handleCommand = useCallback((deviceId: string, command: string, params = {}) => {
    send({ type: "command", device_id: deviceId, command, params });
  }, [send]);

  const handleScene = useCallback((scene: string) => {
    send({ type: "scene", scene_name: scene });
    toast(`Activating "${scene}"...`, { icon: "▶" });
  }, [send]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-950 text-gray-400">
        Loading room...
      </div>
    );
  }

  if (!room) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-950 text-red-400">
        Room not found
      </div>
    );
  }

  const devicesWithState: Device[] = room.devices.map((d) => ({
    ...d,
    state: deviceStates[d.id] ?? d.state,
  }));

  return (
    <div className="min-h-screen bg-gray-950 flex flex-col">
      <StatusBar roomName={room.name} connected={connected} />

      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 p-6 overflow-y-auto">
          <h2 className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-4">Devices</h2>
          <div className="grid grid-cols-2 gap-4 max-w-2xl">
            {devicesWithState.map((device) => (
              <DeviceCard key={device.id} device={device} onCommand={handleCommand} />
            ))}
          </div>
        </div>

        <div className="w56 border-l border-gray-800 p-4 flex flex-col gap-2">
          <h2 className="text-gray-400 text-xs font-semibold uppercase tracking-wider mb-2">Scenes</h2>
          {room.scenes.map((scene) => (
            <button
              key={scene}
              onClick={() => handleScene(scene)}
              className="flex items-center gap-2 px-4 py-3 bg-gray-800 hover:bg-blue-700 rounded-lg text-white text-sm font-medium transition-colors text-left"
            >
              <Play size={14} />
              {scene}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
