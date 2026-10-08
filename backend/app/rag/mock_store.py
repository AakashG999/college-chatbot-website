"""A tiny, dependency-free stand-in for the Chroma vector store, used only
when USE_MOCK_LLM=true. It lets the full RAG pipeline (ingest -> retrieve ->
answer) be exercised end-to-end with no API key, no network access, and none
of Chroma/chromadb's heavier dependencies.

It represents each chunk as a hashed bag-of-words vector (deterministic
across processes via zlib.crc32, unlike Python's salted built-in hash()) and
answers similarity_search with plain cosine similarity. This is good enough
to prove the retrieval wiring and category filtering work correctly — it is
NOT a substitute for real embedding quality, and should never be used in
production.
"""
import math
import pickle
import re
import zlib
from collections import Counter
from pathlib import Path

from langchain_core.documents import Document

DIM = 512
TOKEN_RE = re.compile(r"[a-z0-9]+")


def vectorize(text: str) -> list[float]:
    tokens = TOKEN_RE.findall(text.lower())
    counts = Counter(tokens)
    vec = [0.0] * DIM
    for token, count in counts.items():
        idx = zlib.crc32(token.encode("utf-8")) % DIM
        vec[idx] += count
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine(a: list[float], b: list[float]) -> float:
    # Both vectors are already L2-normalized, so the dot product IS the
    # cosine similarity.
    return sum(x * y for x, y in zip(a, b))


class MockVectorStore:
    """Minimal stand-in exposing the same `similarity_search(query, k=,
    filter=)` surface this project's retriever.py calls on a real Chroma
    store."""

    def __init__(self, entries: list[tuple[list[float], Document]]):
        self._entries = entries

    @classmethod
    def build(cls, documents: list[Document]) -> "MockVectorStore":
        entries = [(vectorize(doc.page_content), doc) for doc in documents]
        return cls(entries)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self._entries, f)

    @classmethod
    def load(cls, path: Path) -> "MockVectorStore":
        if not path.exists():
            raise RuntimeError(
                f"Mock vector store not found at '{path}'. Run "
                "`python -m app.rag.ingest` (with USE_MOCK_LLM=true) first."
            )
        with open(path, "rb") as f:
            entries = pickle.load(f)
        return cls(entries)

    def similarity_search(
        self, query: str, k: int = 4, filter: dict | None = None
    ) -> list[Document]:
        qvec = vectorize(query)
        candidates = self._entries
        if filter:
            candidates = [
                (vec, doc)
                for vec, doc in candidates
                if all(doc.metadata.get(fk) == fv for fk, fv in filter.items())
            ]
        scored = sorted(candidates, key=lambda pair: _cosine(qvec, pair[0]), reverse=True)
        return [doc for _, doc in scored[:k]]
