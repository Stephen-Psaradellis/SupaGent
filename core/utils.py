"""
Common utility functions used across the application.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional


def get_document_hash(content: str) -> str:
    """Generate SHA-256 hash for document content.
    
    Used for deduplication of documents in vector stores.
    
    Args:
        content: Document content to hash.
        
    Returns:
        Hexadecimal hash string.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def format_document_for_response(
    doc: Dict[str, Any],
    max_content_length: int = 200,
    include_metadata: bool = True,
) -> Dict[str, Any]:
    """Format a document dictionary for API responses.
    
    Standardizes document format across endpoints and truncates
    content for preview purposes.
    
    Args:
        doc: Document dictionary with "page_content" and "metadata" keys.
        max_content_length: Maximum length for content preview.
        include_metadata: Whether to include full metadata.
        
    Returns:
        Formatted document dictionary.
    """
    content = doc.get("page_content", "")
    metadata = doc.get("metadata", {})
    
    result: Dict[str, Any] = {
        "content_preview": (
            content[:max_content_length] + "..."
            if len(content) > max_content_length
            else content
        ),
        "content_length": len(content),
    }
    
    if include_metadata:
        result["metadata"] = metadata
        result["title"] = (
            metadata.get("title")
            or metadata.get("source")
            or "Unknown"
        )
    
    return result


def format_documents_for_response(
    docs: List[Dict[str, Any]],
    max_content_length: int = 200,
) -> List[Dict[str, Any]]:
    """Format multiple documents for API responses.
    
    Args:
        docs: List of document dictionaries.
        max_content_length: Maximum length for content preview.
        
    Returns:
        List of formatted document dictionaries.
    """
    return [
        format_document_for_response(doc, max_content_length)
        for doc in docs
    ]


def extract_title_from_doc(doc: Dict[str, Any]) -> str:
    """Extract title from document metadata.
    
    Tries multiple metadata fields to find a title.
    
    Args:
        doc: Document dictionary with metadata.
        
    Returns:
        Title string or "Document" if not found.
    """
    metadata = doc.get("metadata", {})
    return (
        metadata.get("title")
        or metadata.get("source")
        or "Document"
    )


def safe_get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Safely get environment variable.
    
    Args:
        key: Environment variable name.
        default: Default value if not found.
        
    Returns:
        Environment variable value or default.
    """
    import os
    return os.getenv(key, default)


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate.
        max_length: Maximum length.
        
    Returns:
        Truncated text with "..." if truncated.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def normalize_session_id(session_id: Optional[str]) -> str:
    """Normalize session ID to a valid value.
    
    Args:
        session_id: Optional session ID.
        
    Returns:
        Session ID or "default" if None.
    """
    return session_id or "default"

