#!/usr/bin/env python3
import argparse, asyncio, hashlib, logging, random, string
logging.basicConfig(level=logging.INFO, format="%(asctime)s [pjlink-sim] %(message)s")
logger = logging.getLogger(__name__)
POWER_OFF, POWER_ON, POWER_WARMING, POWER_COOLING = "0", "1", "2", "3"

class PJLinkSimulator:
    def __init__(self, name="Sim Projector", password=""):
        self.name = name; self.password = password; self.manufacturer = "Nomy"
        self.model = "VirtualDisplay"; self.power = POWER_OFF; self.input = "31"
        self.avmt = "30"; self.lamp_hours = 1250
    def _random_token(self, length=8):
        return "".join(random.choices(string.hexdigits[:16], k=length))
    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info("peername")
        logger.info(f"Connection from {addr}")
        try:
            if self.password:
                token = self._random_token(); greeting = f"PJLINK 1 {token}\r"
            else:
                token = ""; greeting = "PJLINK 0\r"
            writer.write(greeting.encode("ascii")); await writer.drain()
            raw = await asyncio.wait_for(reader.readline(), timeout=10.0)
            line = raw.decode("ascii", errors="ignore").strip()
            if not line: return
            if self.password and token:
                exp = hashlib.md5((token + self.password).encode()).hexdigest()
                if len(line) >= 32:
                    if line[:32] != exp:
                        writer.write(b"PJLINK ERRA\r"); await writer.drain(); return
                    line = line[32:]
            response = self._process_command(line)
            logger.info(f"  CMD: {line!r}  ->  {response!r}")
            writer.write((response + "\r").encode("ascii")); await writer.drain()
        except asyncio.TimeoutError: pass
        except Exception as e: logger.error(f"Handler error: {e}")
        finally:
            writer.close()
            try: await writer.wait_closed()
            except Exception: pass
    def _process_command(self, line):
        if not line.startswith("%1"): return "%1ERR2"
        parts = line[2:].split(" ", 1)
        if len(parts) != 2: return "%1ERR2"
        cmd, param = parts[0].upper(), parts[1].strip()
        if cmd == "POWR": return self._cmd_power(param)
        elif cmd == "INPT": return self._cmd_input(param)
        elif cmd == "AVMT": return self._cmd_avmt(param)
        elif cmd == "NAME": return f"%1NAME={self.name}" if param == "?" else "%1NAME=ERR2"
        elif cmd == "INF1": return f"%1INFQ={self.manufacturer}" if param == "?" else "%1INF1=ERR2"
        elif cmd == "INF2": return f"%1INF2={self.model}" if param == "?" else "%1INF2=ERR2"
        elif cmd == "LAMP": return f"%1LAMP={self.lamp_hours} 1" if param == "?" else "%1LAMP=ERR2"
        else: return "%1ERR3"
    def _cmd_power(self, param):
        if param == "?": return f"%1POWR={self.power}"
        elif param == "1":
            if self.power == POWER_ON: return "%1POWR=OK"
            self.power = POWER_WARMING; asyncio.create_task(self._power_on_sequence()); return "%1POWR=OK"
        elif param == "0":
            if self.power == POWER_OFF: return "%1POWR=OK"
            self.power = POWER_COOLING; asyncio.create_task(self._power_off_sequence()); return "%1POWR=OK"
        return "%1POWR=ERR2"
    def _cmd_input(self, param):
        if param == "?": return f"%1INPT={self.input}"
        elif self.power != POWER_ON: return "%1INPT=ERR3"
        else: self.input = param; return "%1INPT=OK"
    def _cmd_avmt(self, param):
        if param == "?": return f"%1AVMT={self.avmt}"
        elif param in ("10", "11", "20", "21", "30", "31"): self.avmt = param; return "%1AVMT=OK"
        return "%1AVMT=ERR2"
    async def _power_on_sequence(self):
        logger.info("Power: warming up (3s)..."); await asyncio.sleep(3)
        self.power = POWER_ON; logger.info("Power: ON")
    async def _power_off_sequence(self):
        logger.info("Power: cooling down (5s)..."); await asyncio.sleep(5)
        self.power = POWER_OFF; logger.info("Power: OFF")

async def main():
    parser = argparse.ArgumentParser(description="PJLink Display Simulator")
    parser.add_argument("--port", type=int, default=4352)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--name", default="Sim Projector")
    parser.add_argument("--password", default="")
    args = parser.parse_args()
    sim = PJLinkSimulator(name=args.name, password=args.password)
    server = await asyncio.start_server(sim.handle_client, args.host, args.port)
    logger.info(f"PJLink simulator listening on {args.host}:{args.port} (name={args.name!r})")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
