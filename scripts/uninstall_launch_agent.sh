#!/bin/bash

# Uninstall OpenCode Obsidian Sync Launch Agent

PLIST_FILE="$HOME/Library/LaunchAgents/com.surya.opencode-obsidian-sync.plist"
PID_FILE="/tmp/opencode_obsidian_sync.pid"

echo "Uninstalling OpenCode Obsidian Sync Launch Agent..."

# Stop the running daemon
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping sync daemon..."
        kill "$PID"
        rm -f "$PID_FILE"
    fi
fi

# Unload the Launch Agent
if [ -f "$PLIST_FILE" ]; then
    launchctl unload "$PLIST_FILE" 2>/dev/null
    rm -f "$PLIST_FILE"
    echo "Launch Agent removed."
else
    echo "Launch Agent not found."
fi

echo ""
echo "OpenCode Obsidian Sync has been uninstalled."
