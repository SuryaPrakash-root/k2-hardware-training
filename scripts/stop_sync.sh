#!/bin/bash

# Stop OpenCode to Obsidian Auto-Sync Daemon

PID_FILE="/tmp/opencode_obsidian_sync.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping sync daemon (PID: $PID)..."
        kill "$PID"
        rm -f "$PID_FILE"
        echo "Sync daemon stopped."
    else
        echo "Sync daemon is not running."
        rm -f "$PID_FILE"
    fi
else
    echo "Sync daemon is not running."
fi
