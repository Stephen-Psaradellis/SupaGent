from typing import List, Dict, Any

class MCPClient:
    """Adapter boundary that represents MCP-mediated retrieval.
    
    In this demo, it delegates to the local VectorStore until a real MCP server is wired.
    The return schema mirrors structured docs: {page_content, metadata}.
    
    This abstraction allows the RAG pipeline to work with either local vector stores
    or remote MCP servers without code changes.
    
    Attributes:
        _retrieve_fn: Callable that performs the actual retrieval.
            Signature: (query: str, k: int) -> List[Dict[str, Any]]
    """

    def __init__(self, retriever_callable):
        """Initialize the MCP client.
        
        Args:
            retriever_callable: Function that performs retrieval. Should accept
                (query: str, k: int) and return List[Dict[str, Any]] with
                documents containing "page_content" and "metadata" keys.
        """
        # retriever_callable: (query: str, k: int) -> List[Dict[str, Any]]
        self._retrieve_fn = retriever_callable

    def retrieve(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve documents matching the query.
        
        Args:
            query: Search query string.
            k: Number of results to return (default: 4).
            
        Returns:
            List of document dictionaries with "page_content" and "metadata" keys.
        """
        return self._retrieve_fn(query, k)
