#!/bin/bash

# Automator Workflow: OpenCode to Obsidian Auto-Sync
# This script is called by the Automator application

SCRIPT_DIR="$HOME/k2-hardware-training/scripts"
PID_FILE="/tmp/opencode_obsidian_sync.pid"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Sync daemon is already running (PID: $PID)"
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# Start the sync daemon
cd "$SCRIPT_DIR"
./start_sync.sh

echo "Obsidian sync daemon started!"
