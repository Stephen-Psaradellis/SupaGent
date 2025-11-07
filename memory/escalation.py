"""
Escalation management and context handoff.
Stores escalation data and provides context for human agents.
"""
from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum


class EscalationReason(str, Enum):
    """Reasons for escalation."""
    LOW_CONFIDENCE = "low_confidence"
    NO_RESULTS = "no_results"
    USER_REQUEST = "user_request"
    MULTIPLE_FAILURES = "multiple_failures"
    FRUSTRATION_DETECTED = "frustration_detected"


@dataclass
class EscalationContext:
    """Full context for an escalated conversation."""
    session_id: str
    escalation_reason: str
    timestamp: float
    conversation_transcript: List[Dict[str, str]]  # List of {role, text, timestamp}
    retrieved_documents: List[Dict[str, Any]]
    confidence_scores: List[float]
    suggested_responses: List[str]
    customer_id: Optional[str] = None
    customer_info: Optional[Dict[str, Any]] = None
    ticket_id: Optional[str] = None
    assigned_agent: Optional[str] = None
    status: str = "pending"  # pending, assigned, in_progress, resolved
    resolution_notes: Optional[str] = None


class EscalationStore:
    """Store for escalation data and context."""

    def __init__(self, root_dir: str = "./data/escalations"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, threading.Lock] = {}

    def _lock(self, key: str) -> threading.Lock:
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        return self._locks[key]

    def _path(self, filename: str) -> Path:
        return self.root / filename

    def save_escalation(self, escalation: EscalationContext) -> None:
        """Save escalation context."""
        p = self._path("escalations.jsonl")
        escalation.timestamp = escalation.timestamp or time.time()
        with self._lock("escalations"):
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(escalation), ensure_ascii=False, default=str) + "\n")

    def get_escalation(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve escalation context for a session."""
        p = self._path("escalations.jsonl")
        if not p.exists():
            return None

        with self._lock("escalations"):
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if obj.get("session_id") == session_id:
                            return obj
                    except Exception:
                        continue
        return None

    def get_escalations(
        self,
        status: Optional[str] = None,
        assigned_agent: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve escalations with optional filtering."""
        p = self._path("escalations.jsonl")
        if not p.exists():
            return []

        escalations: List[Dict[str, Any]] = []
        with self._lock("escalations"):
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if status and obj.get("status") != status:
                            continue
                        if assigned_agent and obj.get("assigned_agent") != assigned_agent:
                            continue
                        escalations.append(obj)
                    except Exception:
                        continue

        # Sort by timestamp, most recent first
        escalations.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return escalations

    def update_escalation(
        self,
        session_id: str,
        updates: Dict[str, Any],
    ) -> bool:
        """Update escalation status or other fields."""
        p = self._path("escalations.jsonl")
        if not p.exists():
            return False

        updated = False
        lines: List[str] = []

        with self._lock("escalations"):
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if obj.get("session_id") == session_id:
                            obj.update(updates)
                            updated = True
                        lines.append(json.dumps(obj, ensure_ascii=False, default=str))
                    except Exception:
                        lines.append(line)

            if updated:
                with p.open("w", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")

        return updated


def detect_escalation_trigger(
    confidence: float,
    has_results: bool,
    user_text: str,
    failure_count: int,
) -> Optional[EscalationReason]:
    """Detect if escalation should be triggered based on conversation state."""
    # Low confidence threshold
    if confidence < 0.5:
        return EscalationReason.LOW_CONFIDENCE

    # No results from vector store
    if not has_results:
        return EscalationReason.NO_RESULTS

    # User explicitly requests human
    user_lower = user_text.lower()
    escalation_phrases = [
        "speak to a human",
        "talk to a real person",
        "human agent",
        "this isn't helping",
        "can i talk to someone",
    ]
    if any(phrase in user_lower for phrase in escalation_phrases):
        return EscalationReason.USER_REQUEST

    # Multiple failed attempts
    if failure_count >= 3:
        return EscalationReason.MULTIPLE_FAILURES

    # Frustration indicators
    frustration_phrases = [
        "this is frustrating",
        "not working",
        "doesn't help",
        "useless",
    ]
    if any(phrase in user_lower for phrase in frustration_phrases):
        return EscalationReason.FRUSTRATION_DETECTED

    return None

