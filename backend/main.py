from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import devices, rooms, system
from api.websocket import router as ws_router
from core.config import load_config
from core.event_bus import EventBus
from core.plugin_loader import PluginLoader
from core.state import RoomStateManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config()
    event_bus = EventBus()
    plugin_loader = PluginLoader(config, event_bus)
    room_manager = RoomStateManager(config, plugin_loader, event_bus)

    app.state.config = config
    app.state.event_bus = event_bus
    app.state.plugin_loader = plugin_loader
    app.state.room_manager = room_manager

    await room_manager.startup()
    yield
    await room_manager.shutdown()


app = FastAPI(
    title="Nomy AV Controller",
    description="Open source conference room AV control system",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router, prefix="/api/v1", tags=["system"])
app.include_router(rooms.router, prefix="/api/v1", tags=["rooms"])
app.include_router(devices.router, prefix="/api/v1", tags=["devices"])
app.include_router(ws_router, tags=["websocket"])
