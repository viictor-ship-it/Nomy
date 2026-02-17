#!/bin/bash
# Start all Nomy dev services
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[nomy] Starting PJLink simulator..."
python "$SCRIPT_DIR/simulators/pjlink_sim.py" --port 4352 &

echo "[nomy] Starting backend..."
(cd "$SCRIPT_DIR/backend" && source .venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000) &

echo "[nomy] Starting frontend..."
(cd "$SCRIPT_DIR/frontend" && npm run dev) &

echo "[nomy] All services started. Press Ctrl+C to stop all."
wait
