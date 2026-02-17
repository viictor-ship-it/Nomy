import os
from pathlib import Path
import yaml

# Support running from backend/ or project root
_THIS_DIR = Path(__file__).parent.parent.parent  # project root

CONFIG_PATH = Path(os.getenv("NOMY_CONFIG", str(_THIS_DIR / "config" / "nomy.yaml")))
ROOMS_DIR = Path(os.getenv("NOMY_ROOMS_DIR", str(_THIS_DIR / "config" / "rooms")))


def load_config() -> dict:
    """Load global config and all room configs."""
    config = {}

    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f) or {}

    config["rooms"] = {}
    if ROOMS_DIR.exists():
        for room_file in ROOMS_DIR.glob("*.yaml"):
            with open(room_file) as f:
                room_data = yaml.safe_load(f)
                if room_data and "room" in room_data:
                    room_id = room_data["room"]["id"]
                    config["rooms"][room_id] = room_data

    return config
