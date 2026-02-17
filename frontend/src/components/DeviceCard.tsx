import { Power } from "lucide-react";
import { Device } from "../types";

interface Props {
  device: Device;
  onCommand: (deviceId: string, command: string, params?: Record<string, unknown>) => void;
}

const statusColors: Record<string, string> = {
  online: "bg-green-500",
  offline: "bg-red-500",
  error: "bg-amber-500",
  unknown: "bg-gray-500",
};

export function DeviceCard({ device, onCommand }: Props) {
  const status = device.state?.status ?? "unknown";
  const isPowered = device.state?.power === true;

  return (
    <div className="bg-gray-800 rounded-xl p-4 flex flex-col gap-3 border border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-white font-medium">{device.name}</div>
          <div className="text-gray-400 text-xs capitalize">{device.type} • {device.driver}</div>
        </div>
        <span className={`w2.5 h-2.5 rounded-full ${statusColors[status]}`} title={status} />
      </div>

      <button
        onClick={() => onCommand(device.id, isPowered ? "power_off" : "power_on")}
        disabled={status === "offline" || status === "unknown"}
        className={`flex items-center justify-center gap-2 py-3 rounded-lg font-medium transition-colors
          ${isPowered
            ? "bg-green-600 hover:bg-green-700 text-white"
            : "bg-gray-700 hover:bg-gray-600 text-gray-300"
          } disabled:opacity-40 disabled:cursor-not-allowed`}
      >
        <Power size={16} />
        {isPowered ? "On" : "Off"}
      </button>

      {device.state?.extra && Object.keys(device.state.extra).length > 0 && (
        <div className="text-xs text-gray-500 space-y-0.5">
          {Object.entries(device.state.extra).map(([k, v]) => (
            <div key={k} className="flex justify-between">
              <span>{k}</span>
              <span className="text-gray-400">{String(v)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
