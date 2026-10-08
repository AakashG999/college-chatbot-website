"""Builds the vector store from the markdown knowledge base in app/data.

Run this once (and again whenever the docs in app/data change):

    python -m app.rag.ingest

Mode is auto-detected (see app/config.py): if a real OPENAI_API_KEY is set,
this builds a real Chroma + OpenAI-embeddings store; otherwise it
automatically falls back to the local dependency-free mock store
(app/rag/mock_store.py), so ingestion always works even with no API key.
Set USE_MOCK_LLM=true/false explicitly to override the auto-detection.
"""
import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import settings

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Very small YAML-ish frontmatter parser for our simple `key: value` docs."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    raw_meta, body = match.groups()
    meta = {}
    for line in raw_meta.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, body.strip()


def load_documents() -> list[Document]:
    docs = []
    for path in sorted(DATA_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)
        meta["source"] = path.name
        docs.append(Document(page_content=body, metadata=meta))
    return docs


def build_vector_store():
    raw_docs = load_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(raw_docs)

    if settings.use_mock:
        from app.rag.mock_store import MockVectorStore

        store = MockVectorStore.build(chunks)
        store.save(Path(settings.chroma_persist_dir) / "mock_store.pkl")
        return store

    from langchain_chroma import Chroma
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model, api_key=settings.openai_api_key
    )
    store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.chroma_persist_dir,
        collection_name=settings.collection_name,
    )
    return store


if __name__ == "__main__":
    build_vector_store()
    print(f"Mode: {'mock' if settings.use_mock else 'real (OpenAI)'} ({settings.mode_reason})")
    if settings.use_mock:
        print(
            f"[mock mode] Ingested knowledge base into a local mock vector "
            f"store at '{settings.chroma_persist_dir}/mock_store.pkl'. "
            "No API calls were made."
        )
    else:
        print(
            f"Ingested knowledge base into Chroma at '{settings.chroma_persist_dir}' "
            f"(collection: {settings.collection_name})."
        )
