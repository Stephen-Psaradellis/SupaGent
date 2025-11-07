"""
HTTP client utilities with connection pooling and reuse.

Provides a singleton HTTP client with connection pooling for
better performance and resource management.
"""
from __future__ import annotations

import httpx
from typing import Optional


class HTTPClientManager:
    """Manager for HTTP client instances with connection pooling.
    
    Maintains a singleton httpx.Client instance for reuse across
    requests, improving performance and resource usage.
    """
    
    _client: Optional[httpx.Client] = None
    _async_client: Optional[httpx.AsyncClient] = None
    
    @classmethod
    def get_client(cls, timeout: float = 10.0) -> httpx.Client:
        """Get or create a synchronous HTTP client.
        
        Creates a client with connection pooling on first call.
        Reuses the same client for subsequent calls.
        
        Args:
            timeout: Request timeout in seconds.
            
        Returns:
            httpx.Client instance.
        """
        if cls._client is None:
            cls._client = httpx.Client(
                timeout=timeout,
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                ),
            )
        return cls._client
    
    @classmethod
    def get_async_client(cls, timeout: float = 10.0) -> httpx.AsyncClient:
        """Get or create an asynchronous HTTP client.
        
        Creates an async client with connection pooling on first call.
        Reuses the same client for subsequent calls.
        
        Args:
            timeout: Request timeout in seconds.
            
        Returns:
            httpx.AsyncClient instance.
        """
        if cls._async_client is None:
            cls._async_client = httpx.AsyncClient(
                timeout=timeout,
                limits=httpx.Limits(
                    max_keepalive_connections=20,
                    max_connections=100,
                ),
            )
        return cls._async_client
    
    @classmethod
    def close_all(cls) -> None:
        """Close all HTTP clients.
        
        Should be called during application shutdown.
        """
        if cls._client is not None:
            cls._client.close()
            cls._client = None
        
        if cls._async_client is not None:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule close for running loop
                    loop.create_task(cls._async_client.aclose())
                else:
                    loop.run_until_complete(cls._async_client.aclose())
            except Exception:
                pass
            cls._async_client = None


def get_http_client(timeout: float = 10.0) -> httpx.Client:
    """Convenience function to get HTTP client.
    
    Args:
        timeout: Request timeout in seconds.
        
    Returns:
        httpx.Client instance.
    """
    return HTTPClientManager.get_client(timeout)


def get_async_http_client(timeout: float = 10.0) -> httpx.AsyncClient:
    """Convenience function to get async HTTP client.
    
    Args:
        timeout: Request timeout in seconds.
        
    Returns:
        httpx.AsyncClient instance.
    """
    return HTTPClientManager.get_async_http_client(timeout)

