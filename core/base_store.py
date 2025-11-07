"""
Base classes for data stores.

Provides common functionality for JSONL-based append-only stores
with thread-safe operations.
"""
from __future__ import annotations

import json
import threading
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


class BaseJSONLStore(ABC):
    """Base class for JSONL-based append-only stores.
    
    Provides thread-safe file operations and common patterns
    for storing and retrieving data in JSONL format.
    
    Attributes:
        root: Root directory for store files.
        _locks: Dictionary of per-file locks for thread safety.
    """
    
    def __init__(self, root_dir: str):
        """Initialize the store.
        
        Args:
            root_dir: Root directory for storing files.
        """
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, threading.Lock] = {}
    
    def _path(self, filename: str) -> Path:
        """Get the file path for a given filename.
        
        Args:
            filename: Name of the file.
            
        Returns:
            Path object for the file.
        """
        return self.root / filename
    
    def _lock(self, key: str) -> threading.Lock:
        """Get or create a thread lock for a key.
        
        Args:
            key: Lock key identifier.
            
        Returns:
            Threading lock for the key.
        """
        if key not in self._locks:
            self._locks[key] = threading.Lock()
        return self._locks[key]
    
    def _append_record(
        self,
        filename: str,
        record: Any,
        lock_key: Optional[str] = None,
    ) -> None:
        """Append a record to a JSONL file.
        
        Thread-safe append operation.
        
        Args:
            filename: Name of the file to append to.
            record: Record to append (must be serializable to dict).
            lock_key: Optional lock key. Uses filename if not provided.
        """
        p = self._path(filename)
        lock_key = lock_key or filename
        record_dict = asdict(record) if hasattr(record, "__dataclass_fields__") else record
        
        with self._lock(lock_key):
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record_dict, ensure_ascii=False) + "\n")
    
    def _read_records(
        self,
        filename: str,
        lock_key: Optional[str] = None,
        filter_fn: Optional[callable] = None,
    ) -> List[Dict[str, Any]]:
        """Read records from a JSONL file.
        
        Thread-safe read operation with optional filtering.
        
        Args:
            filename: Name of the file to read.
            lock_key: Optional lock key. Uses filename if not provided.
            filter_fn: Optional function to filter records.
                Should accept a dict and return bool.
                
        Returns:
            List of record dictionaries.
        """
        p = self._path(filename)
        if not p.exists():
            return []
        
        lock_key = lock_key or filename
        records: List[Dict[str, Any]] = []
        
        with self._lock(lock_key):
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    try:
                        obj = json.loads(line)
                        if filter_fn is None or filter_fn(obj):
                            records.append(obj)
                    except Exception:
                        continue
        
        return records
    
    def _clear_file(self, filename: str, lock_key: Optional[str] = None) -> None:
        """Clear a file (delete it).
        
        Thread-safe file deletion.
        
        Args:
            filename: Name of the file to clear.
            lock_key: Optional lock key. Uses filename if not provided.
        """
        p = self._path(filename)
        lock_key = lock_key or filename
        
        with self._lock(lock_key):
            if p.exists():
                p.unlink()
    
    @abstractmethod
    def save(self, record: Any) -> None:
        """Save a record to the store.
        
        Must be implemented by subclasses.
        
        Args:
            record: Record to save.
        """
        pass
    
    @abstractmethod
    def get(self, **kwargs) -> List[Dict[str, Any]]:
        """Retrieve records from the store.
        
        Must be implemented by subclasses.
        
        Args:
            **kwargs: Filter parameters.
            
        Returns:
            List of record dictionaries.
        """
        pass

