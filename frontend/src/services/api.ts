import type { Room } from '../types';

const BASE = '/api/v1';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? res.statusText);
  }
  return res.json();
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  listRooms: () => request<Array<{ id: string; name: string; device_count: number }>>('/rooms'),
  getRoom: (roomId: string) => request<Room>(`/rooms/${roomId}`),
  activateScene: (roomId: string, scene: string) =>
    request(`/rooms/${roomId}/scene/${encodeURIComponent(scene)}`, { method: 'POST' }),
  sendCommand: (roomId: string, deviceId: string, command: string, params = {}) =>
    request(`/rooms/${roomId}/devices/${deviceId}/command`, {
      method: 'POST',
      body: JSON.stringify({ command, params }),
    }),
};
