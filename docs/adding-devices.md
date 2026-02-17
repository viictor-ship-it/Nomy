# Adding a New Device Driver

Nomy uses a plugin-based driver system. Any device controllable over a network or serial port can have a driver.

## 1. Create the driver file

Create a new Python file:

    backend/devices/<category>/<protocol_name>.py

Examples:
- backend/devices/display/pjlink.py  (reference implementation)
- backend/devices/switcher/ip_matrix.py
- backend/devices/camera/visca_ip.py

## 2. Implement DeviceDriver

Extend the abstract base class in backend/devices/base.py:

    from devices.base import DeviceDriver, DeviceState, DeviceStatus
    from typing import Any

    class MyDriver(DeviceDriver):
        def __init__(self, device_id: str, config: dict):
            super().__init__(device_id, config)
            self.host = config.get("host", "127.0.0.1")

        async def connect(self) -> bool: ...
        async def disconnect(self) -> None: ...
        async def get_state(self) -> DeviceState: ...
        async def send_command(self, command: str, **kwargs) -> Any: ...

## 3. Register in DRIVER_MAP

In backend/core/plugin_loader.py add:

    DRIVER_MAP = {
        "pjlink": "devices.display.pjlink.PJLinkDriver",
        "my_device": "devices.category.my_module.MyDriver",
    }

## 4. Add a simulator (recommended)

Create simulators/<protocol>_sim.py that speaks the real protocol.
See simulators/pjlink_sim.py as the reference.

## 5. Configure a room device

In config/rooms/<room>.yaml:

    devices:
      - id: my-device-1
        name: "My Device"
        type: display
        driver: my_device
        config:
          host: "192.168.1.50"
          port: 1234

## 6. Test on the dev machine (victor@10.0.0.150)

    # Terminal 1 - simulator
    python3 ~/nomy/simulators/my_device_sim.py --port 1234

    # Terminal 2 - backend
    cd ~/nomy/backend && source .venv/bin/activate
    uvicorn main:app --reload --port 8000

    # Test the API
    curl http://10.0.0.150:8000/api/v1/rooms/example-room/devices

## Standard command names

Use these names for portability with the frontend:

    power_on / power_off   -- Device power
    input                  -- Source switch (input=kwarg)
    mute_on / mute_off     -- AV mute
    preset                 -- Camera/scene preset (preset=kwarg)
    pan / tilt / zoom      -- Camera movement
