from typing import List, Dict, Any

class MCPClient:
    """
    Adapter boundary that represents MCP-mediated retrieval.
    In this demo, it delegates to the local VectorStore until a real MCP server is wired.
    The return schema mirrors structured docs: {page_content, metadata}.
    """

    def __init__(self, retriever_callable):
        # retriever_callable: (query: str, k: int) -> List[Dict[str, Any]]
        self._retrieve_fn = retriever_callable

    def retrieve(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        return self._retrieve_fn(query, k)
