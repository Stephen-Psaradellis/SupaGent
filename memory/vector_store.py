from typing import List, Dict, Any
import hashlib
import os

# Strictly use modern, non-deprecated packages
from langchain_chroma import Chroma  # type: ignore
from langchain_community.vectorstores import FAISS  # FAISS remains here
from langchain_huggingface import HuggingFaceEmbeddings  # type: ignore


class VectorStore:
    """Wrapper around a vector store (Chroma or FAISS) with HuggingFace embeddings and persistence.
    
    Provides add_documents and similarity_search APIs used behind MCP.
    Supports both Chroma (default) and FAISS backends, with automatic
    persistence and deduplication of documents.
    
    Attributes:
        _persist_dir: Directory where the vector store is persisted.
        _embeddings: HuggingFace embeddings model instance.
        _backend: Backend type ("CHROMA" or "FAISS").
        _store: The underlying vector store instance.
        _seen_hashes: Set of document content hashes for deduplication.
    """

    def __init__(self, persist_dir: str | None = None, embedding_model: str | None = None):
        """Initialize the vector store.
        
        Args:
            persist_dir: Optional directory for persistence. Defaults to
                CHROMA_PERSIST_DIR env var or "./data/chroma".
            embedding_model: Optional HuggingFace model name. Defaults to
                EMBEDDING_MODEL env var or "sentence-transformers/all-MiniLM-L6-v2".
        """
        persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
        embedding_model = embedding_model or os.getenv(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        os.makedirs(persist_dir, exist_ok=True)
        self._persist_dir = persist_dir
        self._embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self._backend = os.getenv("VECTOR_BACKEND", "CHROMA").upper()
        if self._backend == "FAISS":
            self._store = self._init_faiss()
        else:
            self._store = self._init_chroma()
        self._seen_hashes: set[str] = set()

    def _init_chroma(self):
        """Initialize Chroma vector store.
        
        Returns:
            Chroma instance configured with embeddings and persistence.
        """
        return Chroma(
            collection_name="support_docs",
            embedding_function=self._embeddings,
            persist_directory=self._persist_dir,
        )

    def _init_faiss(self):
        """Initialize FAISS vector store.
        
        Loads existing index if available, otherwise creates a new empty index.
        
        Returns:
            FAISS instance configured with embeddings.
        """
        idx_path = os.path.join(self._persist_dir, "faiss_index")
        if os.path.exists(idx_path):
            return FAISS.load_local(idx_path, self._embeddings, allow_dangerous_deserialization=True)
        # Start empty index by creating from an empty corpus
        return FAISS.from_texts([""], self._embeddings)

    def _persist(self):
        """Persist the vector store to disk.
        
        For FAISS, saves the index explicitly. Chroma persists automatically
        in versions >= 0.4, so this is a no-op for Chroma.
        """
        if self._backend == "FAISS":
            idx_path = os.path.join(self._persist_dir, "faiss_index")
            self._store.save_local(idx_path)
        # Chroma >= 0.4 persists automatically; no-op here

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store.
        
        Adds documents with automatic deduplication based on SHA-256 hash
        of normalized content. Only new documents are added.
        
        Args:
            documents: List of document dictionaries with format:
                {"page_content": str, "metadata": dict}
        """
        texts: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        for d in documents:
            text = d["page_content"].strip()
            meta = d.get("metadata", {})
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if h in self._seen_hashes:
                continue
            self._seen_hashes.add(h)
            texts.append(text)
            metadatas.append(meta)
        if not texts:
            return
        if self._backend == "FAISS":
            new = FAISS.from_texts(texts, self._embeddings, metadatas=metadatas)
            # Merge or initialize
            try:
                self._store.merge_from(new)
            except Exception:
                self._store = new
        else:
            self._store.add_texts(texts=texts, metadatas=metadatas)
        self._persist()

    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar documents using semantic similarity.
        
        Args:
            query: Search query string.
            k: Number of results to return (default: 4).
            
        Returns:
            List of document dictionaries with "page_content" and "metadata" keys,
            ordered by similarity (most similar first).
        """
        docs = self._store.similarity_search(query, k=k)
        return [
            {"page_content": d.page_content, "metadata": dict(d.metadata or {})}
            for d in docs
        ]

    def as_retriever(self, k: int = 4):
        """Get a LangChain retriever interface.
        
        Args:
            k: Number of results to return (default: 4).
            
        Returns:
            LangChain retriever instance configured with k results.
        """
        return self._store.as_retriever(search_kwargs={"k": k})
