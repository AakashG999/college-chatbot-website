"""Smoke-tests the full RAG pipeline (router -> retrieve -> answer) through
the real FastAPI endpoint, in mock mode (USE_MOCK_LLM=true) -- no OpenAI API
key or network access required.

Run from the backend/ directory:

    python scripts/test_mock_chat.py

This sends a handful of representative student questions (one per
knowledge-base category, plus an off-topic one) through /api/chat and prints
the routed category, retrieved source file(s), and the mock answer for each,
so you can eyeball that retrieval is pulling the right material before
wiring up a real OpenAI key.

It forces mock mode (so it never spends API credit, even with a real key
configured) but otherwise uses the SAME CHROMA_PERSIST_DIR as the rest of
the app, rather than a hardcoded one -- hardcoding a different directory
meant that ingesting per the README's main quickstart left this script
looking in the wrong place. The mock store lives alongside any real Chroma
store in that directory under its own filename, so the two don't collide.
If the mock store isn't there yet, it's built automatically below.
"""
import os
import sys
from pathlib import Path

# Must be set before app.config is imported -- it resolves mode at import time.
os.environ["USE_MOCK_LLM"] = "true"

# Allow running as `python scripts/test_mock_chat.py` from backend/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402

_store = Path(settings.chroma_persist_dir) / "mock_store.pkl"
if not _store.exists():
    print(f"Mock store not found at '{_store}' -- building it now...")
    from app.rag.ingest import build_vector_store  # noqa: E402

    build_vector_store()
    print("Done.\n")

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

QUESTIONS = [
    "What's the minimum attendance required to sit for exams?",
    "How much is the hostel fee and what's the curfew time?",
    "I want to apply for a scholarship, what are my options?",
    "Can I reset my student portal password myself?",
    "What's the policy on ragging and how do I report it?",
    "When is the placement season and what's the eligibility?",
    "Who do I contact about a grievance that hasn't been resolved?",
    "What's the weather like today?",  # off-topic control case
]


def main():
    client = TestClient(app)
    history = []
    for question in QUESTIONS:
        response = client.post("/api/chat", json={"message": question, "history": history})
        print("=" * 100)
        print(f"Q: {question}")
        if response.status_code != 200:
            print(f"ERROR {response.status_code}: {response.text}")
            continue
        data = response.json()
        print(f"-> category: {data['category']}")
        print(f"-> sources: {data['sources']}")
        print(f"-> reply:\n{data['reply']}")
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": data["reply"]})

    print("=" * 100)
    print("Done. If every question routed to a sensible category and pulled")
    print("from the matching source file, the RAG wiring is working.")


if __name__ == "__main__":
    main()
