"""
Dependency injection container for SupaGent.

Provides a simple service container for managing dependencies
and component lifecycle.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, TypeVar

from core.config import AppConfig, get_config

T = TypeVar("T")


class ServiceContainer:
    """Simple dependency injection container.
    
    Manages service instances and their dependencies,
    providing lazy initialization and singleton support.
    """
    
    def __init__(self, config: Optional[AppConfig] = None):
        """Initialize the container.
        
        Args:
            config: Optional configuration. Uses get_config() if not provided.
        """
        self.config = config or get_config()
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, bool] = {}
    
    def register(
        self,
        name: str,
        factory: Callable[[], Any],
        singleton: bool = True,
    ) -> None:
        """Register a service factory.
        
        Args:
            name: Service name.
            factory: Factory function that creates the service.
            singleton: Whether to create only one instance (default: True).
        """
        self._factories[name] = factory
        self._singletons[name] = singleton
    
    def register_instance(self, name: str, instance: Any) -> None:
        """Register a service instance directly.
        
        Args:
            name: Service name.
            instance: Service instance.
        """
        self._services[name] = instance
    
    def get(self, name: str) -> Any:
        """Get a service instance.
        
        Creates the instance on first access if not already created.
        Respects singleton settings.
        
        Args:
            name: Service name.
            
        Returns:
            Service instance.
            
        Raises:
            KeyError: If service is not registered.
        """
        # Return existing instance if available
        if name in self._services:
            return self._services[name]
        
        # Create new instance if factory exists
        if name in self._factories:
            instance = self._factories[name]()
            if self._singletons.get(name, True):
                self._services[name] = instance
            return instance
        
        raise KeyError(f"Service '{name}' not registered")
    
    def has(self, name: str) -> bool:
        """Check if a service is registered.
        
        Args:
            name: Service name.
            
        Returns:
            True if service is registered, False otherwise.
        """
        return name in self._services or name in self._factories
    
    def clear(self, name: Optional[str] = None) -> None:
        """Clear service instance(s).
        
        Args:
            name: Optional service name. If None, clears all instances.
        """
        if name:
            self._services.pop(name, None)
        else:
            self._services.clear()


def create_container(config: Optional[AppConfig] = None) -> ServiceContainer:
    """Create and configure a service container.
    
    Registers common services with their factories.
    
    Args:
        config: Optional configuration. Uses get_config() if not provided.
        
    Returns:
        Configured ServiceContainer instance.
    """
    container = ServiceContainer(config)
    config = container.config
    
    # Register core services
    def make_vector_store():
        from memory.vector_store import VectorStore
        return VectorStore(
            persist_dir=config.chroma_persist_dir,
            embedding_model=config.embedding_model,
        )
    
    def make_mcp_client():
        from memory.mcp_client import MCPClient
        store = container.get("vector_store")
        return MCPClient(store.similarity_search)
    
    def make_rag():
        from agents.rag import RAGAnswerer
        mcp = container.get("mcp_client")
        return RAGAnswerer(mcp)
    
    def make_sessions():
        from memory.session import SessionStore
        return SessionStore(root_dir=config.sessions_dir)
    
    def make_analytics():
        from memory.analytics import AnalyticsStore
        return AnalyticsStore(root_dir=config.analytics_dir)
    
    def make_escalations():
        from memory.escalation import EscalationStore
        return EscalationStore(root_dir=config.escalations_dir)
    
    def make_compliance():
        from memory.compliance import ComplianceStore
        return ComplianceStore(root_dir=config.compliance_dir)
    
    def make_crm():
        from integrations.crm import get_crm_adapter
        return get_crm_adapter()
    
    def make_conversation_service():
        from core.services import ConversationService
        return ConversationService(
            rag=container.get("rag"),
            mcp=container.get("mcp_client"),
            sessions=container.get("sessions"),
            analytics_store=container.get("analytics"),
            escalation_store=container.get("escalations"),
            compliance_store=container.get("compliance"),
            crm_adapter=container.get("crm"),
        )
    
    def make_voice_service():
        from core.services import VoiceService
        return VoiceService(
            rag=container.get("rag"),
            config=config,
        )
    
    # Register all services
    container.register("vector_store", make_vector_store)
    container.register("mcp_client", make_mcp_client)
    container.register("rag", make_rag)
    container.register("sessions", make_sessions)
    container.register("analytics", make_analytics)
    container.register("escalations", make_escalations)
    container.register("compliance", make_compliance)
    container.register("crm", make_crm)
    container.register("conversation_service", make_conversation_service)
    container.register("voice_service", make_voice_service)
    
    return container

