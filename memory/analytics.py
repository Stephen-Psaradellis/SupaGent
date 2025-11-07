"""
Analytics data storage and retrieval for conversation metrics.
Uses JSONL format for append-only, restart-tolerant storage.
"""
from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


@dataclass
class ConversationMetrics:
    """Metrics for a single conversation."""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    resolution_status: str = "unresolved"  # resolved, escalated, unresolved
    escalation_reason: Optional[str] = None
    query_count: int = 0
    avg_confidence: float = 0.0
    cost: float = 0.0
    customer_id: Optional[str] = None
    language: Optional[str] = None


@dataclass
class FeedbackEntry:
    """User feedback for a conversation or specific answer."""
    session_id: str
    query_text: Optional[str] = None
    answer_text: Optional[str] = None
    feedback_type: str = "explicit"  # explicit, implicit
    rating: Optional[int] = None  # 1-5 stars, or thumbs up/down (1 or 0)
    comment: Optional[str] = None
    timestamp: float = 0.0
    escalation_triggered: bool = False
    knowledge_gap: bool = False


@dataclass
class KnowledgeGap:
    """Identified knowledge gap in the knowledge base."""
    query_text: str
    session_id: str
    timestamp: float
    gap_type: str  # no_results, low_confidence, escalation, negative_feedback
    confidence_score: Optional[float] = None
    frequency: int = 1
    suggested_action: Optional[str] = None
    priority: int = 0  # Calculated based on frequency and impact


class AnalyticsStore:
    """Append-only JSONL store for analytics data."""

    def __init__(self, root_dir: str = "./data/analytics"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, threading.Lock] = {}

    def _lock(self, key: str) -> threading.Lock:
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        return self._locks[key]

    def _path(self, filename: str) -> Path:
        return self.root / filename

    def save_metrics(self, metrics: ConversationMetrics) -> None:
        """Save conversation metrics."""
        p = self._path("conversations.jsonl")
        with self._lock("conversations"):
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(metrics), ensure_ascii=False) + "\n")

    def save_feedback(self, feedback: FeedbackEntry) -> None:
        """Save user feedback."""
        p = self._path("feedback.jsonl")
        feedback.timestamp = feedback.timestamp or time.time()
        with self._lock("feedback"):
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(feedback), ensure_ascii=False) + "\n")

    def save_knowledge_gap(self, gap: KnowledgeGap) -> None:
        """Save identified knowledge gap."""
        p = self._path("knowledge_gaps.jsonl")
        gap.timestamp = gap.timestamp or time.time()
        with self._lock("gaps"):
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(gap), ensure_ascii=False) + "\n")

    def get_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve conversation metrics with optional filtering."""
        p = self._path("conversations.jsonl")
        if not p.exists():
            return []

        metrics: List[Dict[str, Any]] = []
        start_ts = start_date.timestamp() if start_date else 0
        end_ts = end_date.timestamp() if end_date else float("inf")

        with self._lock("conversations"):
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if session_id and obj.get("session_id") != session_id:
                            continue
                        if start_ts <= obj.get("start_time", 0) <= end_ts:
                            metrics.append(obj)
                    except Exception:
                        continue
        return metrics

    def get_feedback(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve feedback entries with optional filtering."""
        p = self._path("feedback.jsonl")
        if not p.exists():
            return []

        feedback: List[Dict[str, Any]] = []
        start_ts = start_date.timestamp() if start_date else 0
        end_ts = end_date.timestamp() if end_date else float("inf")

        with self._lock("feedback"):
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if session_id and obj.get("session_id") != session_id:
                            continue
                        ts = obj.get("timestamp", 0)
                        if start_ts <= ts <= end_ts:
                            feedback.append(obj)
                    except Exception:
                        continue
        return feedback

    def get_knowledge_gaps(
        self,
        min_priority: int = 0,
        gap_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge gaps, optionally filtered by priority and type."""
        p = self._path("knowledge_gaps.jsonl")
        if not p.exists():
            return []

        gaps: List[Dict[str, Any]] = []
        gap_map: Dict[str, Dict[str, Any]] = {}  # Aggregate by query text

        with self._lock("gaps"):
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if gap_type and obj.get("gap_type") != gap_type:
                            continue
                        if obj.get("priority", 0) < min_priority:
                            continue

                        # Aggregate gaps by query text
                        query = obj.get("query_text", "")
                        if query in gap_map:
                            gap_map[query]["frequency"] += 1
                            gap_map[query]["priority"] = max(
                                gap_map[query].get("priority", 0),
                                obj.get("priority", 0),
                            )
                        else:
                            gap_map[query] = obj
                    except Exception:
                        continue

        gaps = list(gap_map.values())
        gaps.sort(key=lambda x: (x.get("priority", 0), x.get("frequency", 0)), reverse=True)
        return gaps

    def calculate_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Calculate aggregate analytics for the given time period."""
        metrics = self.get_metrics(start_date, end_date)
        feedback = self.get_feedback(start_date, end_date)

        if not metrics:
            return {
                "resolution_rate": 0.0,
                "avg_handling_time": 0.0,
                "escalation_rate": 0.0,
                "csat": 0.0,
                "cost_per_resolution": 0.0,
                "knowledge_gap_count": 0,
                "total_conversations": 0,
            }

        total = len(metrics)
        resolved = sum(1 for m in metrics if m.get("resolution_status") == "resolved")
        escalated = sum(1 for m in metrics if m.get("resolution_status") == "escalated")
        durations = [
            m.get("duration", 0) for m in metrics if m.get("duration") is not None
        ]
        costs = [m.get("cost", 0.0) for m in metrics if m.get("cost", 0.0) > 0]

        # Calculate CSAT from explicit feedback
        ratings = [
            f.get("rating", 0)
            for f in feedback
            if f.get("feedback_type") == "explicit" and f.get("rating") is not None
        ]

        # Knowledge gaps
        gaps = self.get_knowledge_gaps()

        return {
            "resolution_rate": (resolved / total * 100) if total > 0 else 0.0,
            "avg_handling_time": sum(durations) / len(durations) if durations else 0.0,
            "escalation_rate": (escalated / total * 100) if total > 0 else 0.0,
            "csat": sum(ratings) / len(ratings) if ratings else 0.0,
            "cost_per_resolution": (
                sum(costs) / resolved if resolved > 0 and costs else 0.0
            ),
            "knowledge_gap_count": len(gaps),
            "total_conversations": total,
        }

