#!/bin/bash

# OpenCode to Obsidian Auto-Sync Starter
# This script starts the sync daemon in the background

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/obsidian_sync.py"
PID_FILE="/tmp/opencode_obsidian_sync.pid"
LOG_FILE="/tmp/opencode_obsidian_sync.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Sync daemon is already running (PID: $PID)"
        echo "To stop it: ./stop_sync.sh"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: Python sync script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Check if watchdog is installed
if ! python3 -c "import watchdog" 2>/dev/null; then
    echo "Installing watchdog package..."
    pip3 install watchdog
fi

# Start the sync daemon
echo "Starting OpenCode → Obsidian sync daemon..."
python3 "$PYTHON_SCRIPT" > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"

echo "Sync daemon started (PID: $PID)"
echo "Log file: $LOG_FILE"
echo "To stop: ./stop_sync.sh"
