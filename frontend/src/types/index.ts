export type DeviceStatus = "online" | "offline" | "error" | "unknown";

export interface DeviceState {
  status: DeviceStatus;
  power: boolean | null;
  extra: Record<string, unknown>;
}

export interface Device {
  id: string;
  name: string;
  type: string;
  driver: string;
  state: DeviceState | null;
}

export interface Room {
  id: string;
  name: string;
  description: string;
  devices: Device[];
  scenes: string[];
}

export type WsMessage =
  | { type: "snapshot"; states: Record<string, DeviceState> }
  | { type: "device_state_update"; device_id: string; state: DeviceState; timestamp: string }
  | { type: "command_result"; device_id: string; result: string }
  | { type: "scene_result"; scene: string; results: Array<{ device: string; ok: boolean; error?: string }> }
  | { type: "error"; message: string };
