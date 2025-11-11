"""Integration adapters for CRM and ticketing systems."""

from .apollo import ApolloConnector, ApolloContact, search_and_create_contacts
from .crm import get_crm_adapter, CRMAdapter, GenericCRMAdapter

__all__ = [
    "ApolloConnector",
    "ApolloContact",
    "search_and_create_contacts",
    "get_crm_adapter",
    "CRMAdapter",
    "GenericCRMAdapter",
]

