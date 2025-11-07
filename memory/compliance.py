"""
Compliance and security features: PII detection, audit trails, GDPR compliance.
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


@dataclass
class AuditLogEntry:
    """Audit log entry for compliance tracking."""
    timestamp: float
    event_type: str  # conversation_start, query, response, escalation, system_event, access
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    action: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None


@dataclass
class PIIDetection:
    """Detected PII in conversation data."""
    pii_type: str  # email, phone, credit_card, ssn, bank_account, ip_address, address
    value: str
    session_id: str
    timestamp: float
    redacted: bool = False


@dataclass
class DeletionRequest:
    """GDPR deletion request."""
    request_id: str
    requested_at: float
    customer_id: Optional[str] = None
    email: Optional[str] = None
    verified: bool = False
    status: str = "pending"  # pending, in_progress, completed, rejected
    completed_at: Optional[float] = None
    data_types: List[str] = None  # conversations, logs, analytics, all


class ComplianceStore:
    """Store for compliance-related data."""

    def __init__(self, root_dir: str = "./data/compliance"):
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, threading.Lock] = {}

    def _lock(self, key: str) -> threading.Lock:
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        return self._locks[key]

    def _path(self, filename: str) -> Path:
        return self.root / filename

    def log_audit_event(self, entry: AuditLogEntry) -> None:
        """Log an audit event."""
        p = self._path("audit_log.jsonl")
        entry.timestamp = entry.timestamp or time.time()
        with self._lock("audit"):
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(entry), ensure_ascii=False, default=str) + "\n")

    def save_pii_detection(self, detection: PIIDetection) -> None:
        """Save PII detection record."""
        p = self._path("pii_detections.jsonl")
        detection.timestamp = detection.timestamp or time.time()
        with self._lock("pii"):
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(detection), ensure_ascii=False) + "\n")

    def save_deletion_request(self, request: DeletionRequest) -> None:
        """Save GDPR deletion request."""
        p = self._path("deletion_requests.jsonl")
        with self._lock("deletions"):
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(request), ensure_ascii=False, default=str) + "\n")

    def get_audit_log(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve audit log entries with filtering."""
        p = self._path("audit_log.jsonl")
        if not p.exists():
            return []

        entries: List[Dict[str, Any]] = []
        start_ts = start_date.timestamp() if start_date else 0
        end_ts = end_date.timestamp() if end_date else float("inf")

        with self._lock("audit"):
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if event_type and obj.get("event_type") != event_type:
                            continue
                        if session_id and obj.get("session_id") != session_id:
                            continue
                        ts = obj.get("timestamp", 0)
                        if start_ts <= ts <= end_ts:
                            entries.append(obj)
                    except Exception:
                        continue

        entries.sort(key=lambda x: x.get("timestamp", 0))
        return entries

    def get_deletion_requests(
        self,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve deletion requests."""
        p = self._path("deletion_requests.jsonl")
        if not p.exists():
            return []

        requests: List[Dict[str, Any]] = []
        with self._lock("deletions"):
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if status and obj.get("status") != status:
                            continue
                        requests.append(obj)
                    except Exception:
                        continue

        requests.sort(key=lambda x: x.get("requested_at", 0), reverse=True)
        return requests


class PIIDetector:
    """Detect and redact PII in text."""

    # Regex patterns for PII detection
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
    CREDIT_CARD_PATTERN = re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    IP_PATTERN = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

    @classmethod
    def detect(cls, text: str) -> List[Dict[str, str]]:
        """Detect PII in text and return list of detections."""
        detections: List[Dict[str, str]] = []

        # Email addresses
        for match in cls.EMAIL_PATTERN.finditer(text):
            detections.append({"type": "email", "value": match.group()})

        # Phone numbers
        for match in cls.PHONE_PATTERN.finditer(text):
            detections.append({"type": "phone", "value": match.group()})

        # Credit card numbers (basic pattern)
        for match in cls.CREDIT_CARD_PATTERN.finditer(text):
            detections.append({"type": "credit_card", "value": match.group()})

        # SSN
        for match in cls.SSN_PATTERN.finditer(text):
            detections.append({"type": "ssn", "value": match.group()})

        # IP addresses
        for match in cls.IP_PATTERN.finditer(text):
            detections.append({"type": "ip_address", "value": match.group()})

        return detections

    @classmethod
    def redact(cls, text: str, pii_types: Optional[List[str]] = None) -> tuple[str, List[Dict[str, str]]]:
        """Redact PII from text and return redacted text plus list of redactions."""
        if pii_types is None:
            pii_types = ["email", "phone", "credit_card", "ssn", "ip_address"]

        redacted = text
        redactions: List[Dict[str, str]] = []

        detections = cls.detect(text)
        for det in detections:
            if det["type"] in pii_types:
                # Replace with masked version
                value = det["value"]
                if det["type"] == "email":
                    masked = "***@***.***"
                elif det["type"] == "phone":
                    masked = "***-***-****"
                elif det["type"] == "credit_card":
                    masked = "****-****-****-****"
                elif det["type"] == "ssn":
                    masked = "***-**-****"
                elif det["type"] == "ip_address":
                    masked = "***.***.***.***"
                else:
                    masked = "***"

                redacted = redacted.replace(value, masked)
                redactions.append(det)

        return redacted, redactions

