from typing import List, Dict
import pathlib
import argparse

from langchain_text_splitters import RecursiveCharacterTextSplitter

from memory.vector_store import VectorStore


CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


def _chunk(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=["\n\n", "\n", ". ", " "]
    )
    return splitter.split_text(text)


def ingest_simple_folder(dataset_dir: str = "dataset"):
    """
    Ingest .md/.txt from dataset_dir with simple chunking.
    Metadata: {"source": relative path, "title": stem}
    """
    store = VectorStore()
    base = pathlib.Path(dataset_dir)
    docs: List[Dict] = []
    for p in base.rglob("*"):
        if p.suffix.lower() in {".md", ".txt"} and p.is_file():
            text = p.read_text(encoding="utf-8", errors="ignore")
            for i, chunk in enumerate(_chunk(text)):
                docs.append({
                    "page_content": chunk,
                    "metadata": {
                        "source": str(p.relative_to(base)),
                        "title": p.stem,
                        "chunk": i,
                    },
                })
    if docs:
        store.add_documents(docs)


def main():
    parser = argparse.ArgumentParser(description="Ingest dataset into vector store")
    parser.add_argument("--dir", default="dataset", help="Folder containing .md/.txt")
    args = parser.parse_args()
    ingest_simple_folder(args.dir)


if __name__ == "__main__":
    main()
