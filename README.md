# Nomy

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

**Nomy** is an open source AV conference room controller. It provides a unified API and real-time web interface for managing projectors, displays, video switchers, cameras, audio DSPs, and lighting from a single pane of glass.

## Features

- Real-time device control via WebSocket
- PJLink Class 1 projector/display support (TCP, async, authenticated)
- Scene-based automation (one-click meeting presets)
- REST API with OpenAPI docs
- YAML-based room and device configuration
- Pluggable driver architecture
- Built-in PJLink simulator for development
- React + Tailwind frontend with live status indicators
- Scheduled polling with APScheduler

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Simulator (no real hardware needed)

```bash
python simulators/pjlink_sim.py --port 4352 --name "Test Projector"
```

Then open http://localhost:5173 to see the room controller UI.

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
                         | TCP
+----------------------------------------------------------+
|            Physical / Simulated Devices                  |
|        Projectors, Switchers, DSPs, Cameras              |
+----------------------------------------------------------+
```

## Configuration

Rooms are defined in `config/rooms/*.yaml`. See `config/rooms/example-room.yaml` for a complete example with devices and scenes.

## Docs

See [docs/](docs/) for protocol documentation and driver development guide.

## License

MIT - see [LICENSE](LICENSE)
