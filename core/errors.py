"""
Custom exception classes for SupaGent.

Provides structured error handling with clear error types.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


class SupaGentError(Exception):
    """Base exception for all SupaGent errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the error.
        
        Args:
            message: Error message.
            error_code: Optional error code for programmatic handling.
            details: Optional additional error details.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses.
        
        Returns:
            Dictionary representation of the error.
        """
        return {
            "error": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class ConfigurationError(SupaGentError):
    """Error related to configuration issues."""
    pass


class VectorStoreError(SupaGentError):
    """Error related to vector store operations."""
    pass


class RAGError(SupaGentError):
    """Error related to RAG operations."""
    pass


class VoiceError(SupaGentError):
    """Error related to voice operations."""
    pass


class MCPError(SupaGentError):
    """Error related to MCP operations."""
    pass


class CRMError(SupaGentError):
    """Error related to CRM operations."""
    pass

