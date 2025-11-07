"""
CRM/Ticketing system integration adapter.
Supports multiple platforms via adapter pattern.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import os


class CRMAdapter(ABC):
    """Abstract base class for CRM integrations."""

    @abstractmethod
    def create_ticket(
        self,
        title: str,
        description: str,
        customer_id: Optional[str] = None,
        priority: str = "normal",
        tags: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a ticket in the CRM system."""
        pass

    @abstractmethod
    def get_customer(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieve customer information by identifier."""
        pass

    @abstractmethod
    def log_interaction(
        self,
        customer_id: str,
        activity_type: str,
        details: Dict[str, Any],
    ) -> bool:
        """Log an interaction in the CRM system."""
        pass

    @abstractmethod
    def update_ticket(
        self,
        ticket_id: str,
        updates: Dict[str, Any],
    ) -> bool:
        """Update a ticket in the CRM system."""
        pass


class GenericCRMAdapter(CRMAdapter):
    """Generic REST API adapter for CRM systems."""

    def __init__(
        self,
        api_endpoint: str,
        api_key: Optional[str] = None,
        auth_type: str = "bearer",  # bearer, basic, oauth
    ):
        self.api_endpoint = api_endpoint.rstrip("/")
        self.api_key = api_key or os.getenv("CRM_API_KEY")
        self.auth_type = auth_type

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.auth_type == "bearer" and self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif self.auth_type == "basic" and self.api_key:
            # Basic auth would need username:password format
            import base64
            auth_str = base64.b64encode(self.api_key.encode()).decode()
            headers["Authorization"] = f"Basic {auth_str}"
        return headers

    def create_ticket(
        self,
        title: str,
        description: str,
        customer_id: Optional[str] = None,
        priority: str = "normal",
        tags: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Create a ticket via REST API."""
        try:
            from core.http_client import get_http_client
            
            payload = {
                "title": title,
                "description": description,
                "priority": priority,
                "tags": tags or [],
            }
            if customer_id:
                payload["customer_id"] = customer_id

            client = get_http_client(timeout=10.0)
            response = client.post(
                f"{self.api_endpoint}/tickets",
                json=payload,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Return mock response if API is not configured
            import time
            return {
                "id": f"ticket_{int(time.time())}",
                "title": title,
                "status": "created",
                "error": str(e) if isinstance(e, Exception) else "API not configured",
            }

    def get_customer(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retrieve customer information."""
        try:
            from core.http_client import get_http_client
            
            client = get_http_client(timeout=10.0)
            response = client.get(
                f"{self.api_endpoint}/customers/{identifier}",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def log_interaction(
        self,
        customer_id: str,
        activity_type: str,
        details: Dict[str, Any],
    ) -> bool:
        """Log an interaction."""
        try:
            from core.http_client import get_http_client
            
            payload = {
                "customer_id": customer_id,
                "activity_type": activity_type,
                "details": details,
            }

            client = get_http_client(timeout=10.0)
            response = client.post(
                f"{self.api_endpoint}/activities",
                json=payload,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    def update_ticket(
        self,
        ticket_id: str,
        updates: Dict[str, Any],
    ) -> bool:
        """Update a ticket."""
        try:
            from core.http_client import get_http_client
            
            client = get_http_client(timeout=10.0)
            response = client.patch(
                f"{self.api_endpoint}/tickets/{ticket_id}",
                json=updates,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return True
        except Exception:
            return False


def get_crm_adapter() -> Optional[CRMAdapter]:
    """Factory function to get configured CRM adapter.
    
    Uses centralized configuration for better maintainability.
    """
    try:
        from core.config import get_config
        config = get_config()
        
        if not config.crm_api_endpoint:
            return None
        
        if config.crm_type == "generic":
            return GenericCRMAdapter(
                api_endpoint=config.crm_api_endpoint,
                api_key=config.crm_api_key,
                auth_type=config.crm_auth_type,
            )
    except Exception:
        # Fallback to environment variables for backward compatibility
        crm_type = os.getenv("CRM_TYPE", "generic").lower()
        api_endpoint = os.getenv("CRM_API_ENDPOINT")
        
        if not api_endpoint:
            return None
        
        if crm_type == "generic":
            return GenericCRMAdapter(
                api_endpoint=api_endpoint,
                api_key=os.getenv("CRM_API_KEY"),
                auth_type=os.getenv("CRM_AUTH_TYPE", "bearer"),
            )
    
    # Future: Add specific adapters for Salesforce, Zendesk, etc.
    return None

