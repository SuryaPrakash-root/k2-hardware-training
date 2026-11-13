#!/usr/bin/env python3
"""
OpenCode to Obsidian Auto-Sync System
Automatically saves OpenCode sessions to Obsidian AI Memory folder.
"""

import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
OBSIDIAN_VAULT = Path.home() / "Documents" / "Obsidian" / "Surya" / "AI Memory"
OPENCODE_SESSIONS_DIR = Path.home() / ".opencode" / "sessions"
SYNC_INTERVAL = 1  # seconds

class OpenCodeSession:
    def __init__(self, session_id: str, data: dict):
        self.id = session_id
        self.data = data
        self.created_at = data.get("created_at", datetime.now().isoformat())
        self.updated_at = data.get("updated_at", datetime.now().isoformat())
        self.messages = data.get("messages", [])
        self.title = data.get("title", f"Session {session_id[:8]}")

    def to_markdown(self) -> str:
        """Convert session to Obsidian markdown format"""
        md = f"""---
session_id: {self.id}
created: {self.created_at}
updated: {self.updated_at}
type: opencode-session
tags: [opencode, session, ai]
---

# {self.title}

**Session ID:** `{self.id}`
**Created:** {self.created_at}
**Last Updated:** {self.updated_at}

---

## Messages

"""
        for msg in self.messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            if role == "user":
                md += f"### 👤 User ({timestamp})\n\n{content}\n\n---\n\n"
            elif role == "assistant":
                md += f"### 🤖 Assistant ({timestamp})\n\n{content}\n\n---\n\n"
            elif role == "system":
                md += f"### ⚙️ System ({timestamp})\n\n{content}\n\n---\n\n"
        
        return md

class ObsidianSync:
    def __init__(self):
        self.vault_path = OBSIDIAN_VAULT
        self.sessions_dir = OPENCODE_SESSIONS_DIR
        self.synced_sessions = {}
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        self.vault_path.mkdir(parents=True, exist_ok=True)
        (self.vault_path / "OpenCode Sessions").mkdir(exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def get_session_file_path(self, session_id: str) -> Path:
        """Get the Obsidian file path for a session"""
        safe_id = session_id.replace("/", "-").replace("\\", "-")
        return self.vault_path / "OpenCode Sessions" / f"{safe_id}.md"
    
    def sync_session(self, session_id: str, data: dict):
        """Sync a single session to Obsidian"""
        session = OpenCodeSession(session_id, data)
        file_path = self.get_session_file_path(session_id)
        
        # Check if content has changed
        new_content = session.to_markdown()
        new_hash = hashlib.md5(new_content.encode()).hexdigest()
        
        if session_id in self.synced_sessions:
            if self.synced_sessions[session_id] == new_hash:
                return False  # No changes
        
        # Write to Obsidian
        file_path.write_text(new_content, encoding="utf-8")
        self.synced_sessions[session_id] = new_hash
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Synced session: {session_id[:8]}...")
        return True
    
    def sync_all_sessions(self):
        """Sync all OpenCode sessions"""
        if not self.sessions_dir.exists():
            return
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                session_id = session_file.stem
                data = json.loads(session_file.read_text())
                self.sync_session(session_id, data)
            except Exception as e:
                print(f"Error syncing {session_file}: {e}")
    
    def create_empty_session(self, session_id: str, title: str = None):
        """Create an empty session file in Obsidian"""
        if title is None:
            title = f"New Session {session_id[:8]}"
        
        data = {
            "id": session_id,
            "title": title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": []
        }
        
        self.sync_session(session_id, data)
        print(f"Created empty session: {session_id[:8]}...")

class SessionFileHandler(FileSystemEventHandler):
    def __init__(self, sync: ObsidianSync):
        self.sync = sync
    
    def on_modified(self, event):
        if event.src_path.endswith(".json"):
            session_id = Path(event.src_path).stem
            try:
                data = json.loads(Path(event.src_path).read_text())
                self.sync.sync_session(session_id, data)
            except Exception as e:
                print(f"Error handling file change: {e}")
    
    def on_created(self, event):
        if event.src_path.endswith(".json"):
            session_id = Path(event.src_path).stem
            self.sync.create_empty_session(session_id)

def run_sync_daemon():
    """Run the sync daemon"""
    print("=" * 50)
    print("  OpenCode → Obsidian Auto-Sync")
    print("=" * 50)
    print(f"  Vault: {OBSIDIAN_VAULT}")
    print(f"  Sessions: {OPENCODE_SESSIONS_DIR}")
    print(f"  Interval: {SYNC_INTERVAL}s")
    print("=" * 50)
    
    sync = ObsidianSync()
    
    # Initial sync
    sync.sync_all_sessions()
    
    # Set up file watcher
    event_handler = SessionFileHandler(sync)
    observer = Observer()
    observer.schedule(event_handler, str(OPENCODE_SESSIONS_DIR), recursive=True)
    observer.start()
    
    print("\nSync daemon running... Press Ctrl+C to stop\n")
    
    try:
        while True:
            time.sleep(SYNC_INTERVAL)
            sync.sync_all_sessions()
    except KeyboardInterrupt:
        print("\nStopping sync daemon...")
        observer.stop()
    observer.join()

if __name__ == "__main__":
    run_sync_daemon()
