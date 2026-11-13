#!/bin/bash

# Install OpenCode Obsidian Sync as Launch Agent
# This will auto-start the sync daemon on login

PLIST_FILE="$HOME/Library/LaunchAgents/com.surya.opencode-obsidian-sync.plist"
PLIST_SOURCE="$HOME/k2-hardware-training/scripts/com.surya.opencode-obsidian-sync.plist"

echo "Installing OpenCode Obsidian Sync Launch Agent..."

# Copy plist file
cp "$PLIST_SOURCE" "$PLIST_FILE"

# Load the Launch Agent
launchctl load "$PLIST_FILE"

echo ""
echo "=================================="
echo "  Launch Agent Installed!"
echo "=================================="
echo ""
echo "The sync daemon will now:"
echo "  - Start automatically on login"
echo "  - Restart if it crashes"
echo "  - Run in the background"
echo ""
echo "To uninstall:"
echo "  launchctl unload $PLIST_FILE"
echo "  rm $PLIST_FILE"
echo ""
