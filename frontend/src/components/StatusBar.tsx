import { Wifi, WifiOff, Clock } from "lucide-react";

interface Props {
  roomName: string;
  connected: boolean;
}

export function StatusBar({ roomName, connected }: Props) {
  const now = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  return (
    <div className="flex items-center justify-between px-6 py-3 bg-gray-900 border-b border-gray-700 text-sm">
      <span className="text-white font-semibold text-lg">{roomName}</span>
      <div className="flex items-center gap-4 text-gray-400">
        <span className="flex items-center gap-1">
          <Clock size={14} />
          {now}
        </span>
        <span className={`flex items-center gap-1 ${connected ? "text-green-400" : "text-red-400"}`}>
          {connected ? <Wifi size={14} /> : <WifiOff size={14} />}
          {connected ? "Live" : "Reconnecting..."}
        </span>
      </div>
    </div>
  );
}
