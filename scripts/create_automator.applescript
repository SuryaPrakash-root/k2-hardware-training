#!/usr/bin/env osascript

-- Create Automator Application for OpenCode to Obsidian Sync
-- Run this script to create the Automator app

tell application "Automator"
    -- Create new workflow
    set newWorkflow to make new workflow
    
    -- Add "Run Shell Script" action
    set shellAction to make new workflow action at end of workflow actions of newWorkflow with properties {action:"com.apple.Automator.ShellScript"}
    
    -- Set the shell script
    set shell script of shellAction to "#!/bin/bash\n\n# OpenCode to Obsidian Auto-Sync\n# Runs the sync daemon in the background\n\nSCRIPT_DIR=\"$HOME/k2-hardware-training/scripts\"\nPID_FILE=\"/tmp/opencode_obsidian_sync.pid\"\n\n# Check if already running\nif [ -f \"$PID_FILE\" ]; then\n    PID=$(cat \"$PID_FILE\")\n    if ps -p \"$PID\" > /dev/null 2>&1; then\n        echo \"Sync daemon is already running\"\n        exit 0\n    else\n        rm -f \"$PID_FILE\"\n    fi\nfi\n\n# Start the sync daemon\ncd \"$SCRIPT_DIR\"\n./start_sync.sh\n\necho \"Obsidian sync daemon started!\""
    
    -- Set shell to use bash
    set shell of shellAction to "/bin/bash"
    
    -- Pass input as arguments
    set input of shellAction to "as arguments"
    
    -- Save as application
    set appPath to (path to home folder as text) & "Applications:OpenCode Obsidian Sync.app"
    save newWorkflow in (POSIX file of (POSIX path of appPath))
    
    display dialog "Automator application created successfully!\n\nLocation: ~/Applications/OpenCode Obsidian Sync.app\n\nYou can now:\n1. Double-click to run the sync\n2. Add to Login Items for auto-start" buttons {"OK"} default button "OK" with title "OpenCode Obsidian Sync"
    
end tell
