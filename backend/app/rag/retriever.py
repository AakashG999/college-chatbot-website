"""Loads the persisted vector store and exposes retrieval helpers.

With USE_MOCK_LLM=true in the environment, this loads the local
dependency-free mock store (app/rag/mock_store.py) instead of a real Chroma
+ OpenAI-embeddings store, so retrieval works with no API key.
"""
from functools import lru_cache
from pathlib import Path

from app.config import settings

# Categories match the `category` frontmatter field in app/data/*.md
VALID_CATEGORIES = {
    "admissions",
    "fees",
    "academics",
    "exams",
    "hostel",
    "library",
    "it",
    "conduct",
    "grievance",
    "placements",
    "campus-life",
    "international",
    "health",
    "alumni",
    "contact",
}


@lru_cache(maxsize=1)
def get_vector_store():
    if settings.use_mock:
        from app.rag.mock_store import MockVectorStore

        path = Path(settings.chroma_persist_dir) / "mock_store.pkl"
        return MockVectorStore.load(path)

    from langchain_chroma import Chroma
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model, api_key=settings.openai_api_key
    )
    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_persist_dir,
    )


def retrieve(query: str, category: str | None = None, k: int = 4):
    """Return the top-k relevant chunks, optionally filtered by category.

    `category` should be one of VALID_CATEGORIES, or None/"general" to search
    across the whole knowledge base.
    """
    store = get_vector_store()
    search_kwargs = {"k": k}
    if category and category in VALID_CATEGORIES:
        search_kwargs["filter"] = {"category": category}

    results = store.similarity_search(query, **search_kwargs)
    return results
