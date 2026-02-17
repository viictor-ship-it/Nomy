# Nomy

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

**Nomy** is an open source AV conference room controller. It provides a unified API and real-time web interface for managing projectors, displays, video switchers, cameras, audio DSPs, and lighting from a single pane of glass.

## Features

- Real-time device control via WebSocket
- PJLink Class 1 projector/display support (TCP, async, authenticated)
- Scene-based automation (one-click meeting presets)
- REST API with OpenAPI docs at `/docs`
- YAML-based room and device configuration
- Pluggable driver architecture — add new devices via a simple Python class
- Built-in PJLink simulator for development (no real hardware needed)
- React + Tailwind frontend with live status indicators

## Development Environment

| Item | Value |
|------|-------|
| **Host** | `victor@10.0.0.150` (Ubuntu, ubuntuVM2) |
| **Project root** | `~/nomy` |
| **Python** | 3.13.7 |
| **Node** | 22.22.0 |
| **SSH key** | `~/.ssh/id_ed25519` |

> All development happens on the Ubuntu machine. From a Windows client:
> ```
> ssh -i C:/Users/Victor/.ssh/id_ed25519 victor@10.0.0.150
> ```

## Quick Start

### 1. Start the PJLink simulator (no real hardware needed)

```bash
cd ~/nomy
python3 simulators/pjlink_sim.py --port 4352 --name Test Projector
```

### 2. Start the backend

```bash
cd ~/nomy/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ../[dev]
uvicorn main:app --reload --port 8000
```

API docs available at: http://10.0.0.150:8000/docs

### 3. Start the frontend

```bash
cd ~/nomy/frontend
npm install
npm run dev
```

UI available at: http://10.0.0.150:5173

### 4. Or build the frontend

```bash
cd ~/nomy/frontend
npm run build
# Serve the dist/ folder via any static file server or the FastAPI backend
```

## Architecture

```
+----------------------------------------------------------+
|                    React Frontend                        |
|           (Vite + Tailwind + Zustand + WS)               |
+------------------------+---------------------------------+
                         | HTTP + WebSocket
+------------------------v---------------------------------+
|                   FastAPI Backend                        |
|  +-----------+  +------------+  +-------------------+   |
|  | REST API  |  | WebSocket  |  | APScheduler       |   |
|  | /api/v1   |  | /ws/rooms  |  | (device polling)  |   |
|  +-----+-----+  +-----+------+  +---------+---------+   |
|        +--------------+-----------------+               |
|                  +-----v------+                         |
|                  | Event Bus  |                         |
|                  +-----+------+                         |
|        +---------+-----+-----+---------+               |
|  +------v----+  +------v--+  +----v----+               |
|  | PJLink    |  | Future  |  | Future  |               |
|  | Driver    |  | Switcher|  | Audio   |               |
|  +-----------+  +---------+  +---------+               |
+----------------------------------------------------------+
                         | TCP/UDP
+----------------------------------------------------------+
|            Physical / Simulated Devices                  |
|        Projectors, Switchers, DSPs, Cameras              |
+----------------------------------------------------------+
```

## Project Structure

```
~/nomy/
├── backend/                    # FastAPI application
│   ├── main.py                 # Entry point — run with uvicorn
│   ├── api/routes/             # REST endpoints (devices, rooms, system)
│   ├── api/websocket.py        # WebSocket handler + connection manager
│   ├── core/                   # Config loader, event bus, plugin loader, state manager
│   └── devices/display/        # PJLink driver (more drivers added per phase)
├── simulators/
│   └── pjlink_sim.py           # PJLink TCP simulator — use for dev without hardware
├── config/
│   ├── nomy.yaml               # Global config (poll interval, log level)
│   └── rooms/example-room.yaml # Example room with devices and scenes
├── frontend/                   # React + Vite UI
│   └── src/
│       ├── components/         # RoomView, DeviceCard, StatusBar
│       ├── hooks/useWebSocket.ts
│       ├── services/api.ts
│       └── types/index.ts
└── docs/                       # Protocol docs, driver guide
```

## Configuration

Rooms are defined in `config/rooms/*.yaml`. Copy and edit `example-room.yaml`:

```yaml
room:
  id: my-room
  name: Conference Room A

devices:
  - id: projector-main
    name: Main Projector
    type: display
    driver: pjlink
    config:
      host: 192.168.1.100
      port: 4352
      password: 

scenes:
  - name: Presentation
    actions:
      - device: projector-main
        command: power_on
```

## Adding a Device Driver

See [docs/adding-devices.md](docs/adding-devices.md). In short:

1. Create a class in `backend/devices/<type>/<name>.py` that extends `DeviceDriver`
2. Implement `connect`, `disconnect`, `get_state`, `send_command`
3. Register the driver in `backend/core/plugin_loader.py` `DRIVER_MAP`

## API Reference

```
GET  /api/v1/health
GET  /api/v1/system/status
GET  /api/v1/rooms
GET  /api/v1/rooms/{room_id}
POST /api/v1/rooms/{room_id}/scene/{scene_name}
GET  /api/v1/rooms/{room_id}/devices
GET  /api/v1/rooms/{room_id}/devices/{device_id}
POST /api/v1/rooms/{room_id}/devices/{device_id}/command
WS   /ws/rooms/{room_id}
```

Full interactive docs: http://10.0.0.150:8000/docs

## Roadmap

- **Phase 1 (done):** FastAPI skeleton, PJLink driver + sim, WebSocket, React UI
- **Phase 2:** VISCA camera, matrix switcher, scene UI, source switching
- **Phase 3:** Zoom/Teams/Jitsi, Google/MS calendar, conference panel
- **Phase 4:** Tauri desktop app, kiosk mode, Docker/Proxmox deployment
- **Phase 5:** Mobile UI, Dante audio, DMX lighting, multi-room dashboard

## License

MIT — see [LICENSE](LICENSE)
