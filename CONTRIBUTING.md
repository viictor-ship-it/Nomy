# Contributing to Nomy

## Development Setup

The project runs on Ubuntu (ubuntuVM2, ). Clone and work there directly.

### Clone & Bootstrap

```bash
# SSH into the dev machine
ssh victor@10.0.0.150

# Clone the repo
git clone <your-fork> ~/nomy
cd ~/nomy

# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e '../[dev]'

# Simulators (in a separate terminal)
python3 ~/nomy/simulators/pjlink_sim.py --port 4352

# Start backend
uvicorn main:app --reload --port 8000

# Frontend (in a separate terminal)
cd ~/nomy/frontend
npm install
npm run dev
```

## Project Structure

See README.md for the full layout.

## Writing a Device Driver

See [docs/adding-devices.md](docs/adding-devices.md).

## Code Style

- Python: PEP 8, 100-char line length, type hints everywhere
- TypeScript: strict mode, functional components
- Run  before committing

## Submitting Changes

1. Fork the repo
2. Create a feature branch: 
3. Commit with clear messages: , , , 
4. Open a PR against 

## Reporting Issues

Open a GitHub Issue with:
- What you expected
- What happened
- Steps to reproduce
- Python/Node version
