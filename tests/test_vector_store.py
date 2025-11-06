import os
import tempfile
import shutil

import pytest

from memory.vector_store import VectorStore


def test_vector_store_add_and_search(tmp_path):
    persist_dir = tmp_path / "chroma"
    vs = VectorStore(persist_dir=str(persist_dir))

    docs = [
        {"page_content": "To reset your password, go to settings.", "metadata": {"title": "password"}},
        {"page_content": "Shipping delays occur during holidays.", "metadata": {"title": "shipping"}},
    ]
    vs.add_documents(docs)

    results = vs.similarity_search("How do I reset password?", k=1)
    assert len(results) == 1
    assert "password" in results[0]["metadata"].get("title", "")
