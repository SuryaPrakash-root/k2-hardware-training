#!/bin/bash

echo "=================================="
echo "  K2 Training Platform"
echo "=================================="
echo ""

# Start backend on host (needs Apple Silicon GPU)
echo "Starting backend server on http://localhost:8000 ..."
source venv/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

sleep 2

# Start frontend in Apple Container
echo "Starting frontend on http://localhost:3000 ..."
container run -d --name k2-frontend -p 3000:80 k2-hardware-training-frontend:latest

# Start Obsidian sync daemon
echo "Starting Obsidian sync daemon..."
chmod +x scripts/start_sync.sh scripts/stop_sync.sh
./scripts/start_sync.sh

echo ""
echo "=================================="
echo "  Backend:     http://localhost:8000"
echo "  Frontend:    http://localhost:3000"
echo "  Obsidian:    Auto-syncing to AI Memory"
echo "=================================="
echo ""
echo "Press Ctrl+C to stop"

trap "kill $BACKEND_PID 2>/dev/null; container stop k2-frontend 2>/dev/null; container delete k2-frontend 2>/dev/null; ./scripts/stop_sync.sh 2>/dev/null; exit" INT TERM
wait
