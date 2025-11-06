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
    role: str  # "user" or "assistant"
    text: str
    ts: float


class SessionStore:
    """Append-only JSONL session store with in-memory index for speed.

    Restart-tolerant: data persists under data/sessions/{session_id}.jsonl
    Thread-safe for simple single-process FastAPI usage.
    """

    def __init__(self, root_dir: str = "./data/sessions", max_turns: int = 8):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        self.max_turns = max_turns
        self._locks: Dict[str, threading.Lock] = {}

    def _path(self, session_id: str) -> Path:
        return self.root / f"{session_id}.jsonl"

    def _lock(self, session_id: str) -> threading.Lock:
        if session_id not in self._locks:
            self._locks[session_id] = threading.Lock()
        return self._locks[session_id]

    def append(self, session_id: str, role: str, text: str) -> None:
        p = self._path(session_id)
        turn = Turn(role=role, text=text, ts=time.time())
        with self._lock(session_id):
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(turn), ensure_ascii=False) + "\n")

    def history(self, session_id: str) -> List[Turn]:
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
        p = self._path(session_id)
        with self._lock(session_id):
            if p.exists():
                p.unlink()
