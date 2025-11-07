from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


@dataclass
class Turn:
    """A single conversation turn.
    
    Attributes:
        role: Role of the speaker ("user" or "assistant").
        text: The message text content.
        ts: Timestamp of when the turn occurred (Unix timestamp).
    """
    role: str  # "user" or "assistant"
    text: str
    ts: float


class SessionStore:
    """Append-only JSONL session store with in-memory index for speed.

    Restart-tolerant: data persists under data/sessions/{session_id}.jsonl
    Thread-safe for simple single-process FastAPI usage.
    
    Attributes:
        root: Root directory for session files.
        max_turns: Maximum number of turns to keep in history (default: 8).
        _locks: Dictionary of per-session locks for thread safety.
    """

    def __init__(self, root_dir: str = "./data/sessions", max_turns: int = 8):
        """Initialize the session store.
        
        Args:
            root_dir: Root directory for storing session files.
            max_turns: Maximum number of conversation turns to keep per session.
        """
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        self.max_turns = max_turns
        self._locks: Dict[str, threading.Lock] = {}

    def _path(self, session_id: str) -> Path:
        """Get the file path for a session.
        
        Args:
            session_id: Unique session identifier.
            
        Returns:
            Path object for the session's JSONL file.
        """
        return self.root / f"{session_id}.jsonl"

    def _lock(self, session_id: str) -> threading.Lock:
        """Get or create a thread lock for a session.
        
        Args:
            session_id: Unique session identifier.
            
        Returns:
            Threading lock for the session.
        """
        if session_id not in self._locks:
            self._locks[session_id] = threading.Lock()
        return self._locks[session_id]

    def append(self, session_id: str, role: str, text: str) -> None:
        """Append a conversation turn to a session.
        
        Thread-safe append operation that writes to the session's JSONL file.
        
        Args:
            session_id: Unique session identifier.
            role: Role of the speaker ("user" or "assistant").
            text: Message text content.
        """
        p = self._path(session_id)
        turn = Turn(role=role, text=text, ts=time.time())
        with self._lock(session_id):
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(turn), ensure_ascii=False) + "\n")

    def history(self, session_id: str) -> List[Turn]:
        """Retrieve conversation history for a session.
        
        Returns the most recent turns up to max_turns. Returns empty list
        if session doesn't exist.
        
        Args:
            session_id: Unique session identifier.
            
        Returns:
            List of Turn objects, most recent first, limited to max_turns.
        """
        p = self._path(session_id)
        if not p.exists():
            return []
        turns: List[Turn] = []
        with self._lock(session_id):
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        turns.append(Turn(**obj))
                    except Exception:
                        continue
        return turns[-self.max_turns :]

    def clear(self, session_id: str) -> None:
        """Clear all conversation history for a session.
        
        Permanently deletes the session file. Thread-safe operation.
        
        Args:
            session_id: Unique session identifier.
        """
        p = self._path(session_id)
        with self._lock(session_id):
            if p.exists():
                p.unlink()
