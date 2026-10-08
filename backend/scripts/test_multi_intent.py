"""Checks that multi-intent questions ("hostel curfew and admit card dates?")
are routed to every topic they touch, retrieve material for each, and come
back answered -- through the real FastAPI endpoints.

Run from the backend/ directory:

    python scripts/test_multi_intent.py          # mock mode, no API key needed
    python scripts/test_multi_intent.py --real   # against the configured OpenAI model

Mock mode checks the wiring (router -> per-topic retrieval -> answer ->
API). --real checks what actually matters in production: that the LLM
router splits genuine multi-topic questions and does NOT split single-topic
ones. It costs a few cents of API credit per run.

Exits non-zero if any check fails, so it can gate CI.
"""
import json
import os
import sys
from pathlib import Path

REAL = "--real" in sys.argv[1:]
if not REAL:
    # Must be set before app.config is imported -- it resolves mode at import time.
    os.environ["USE_MOCK_LLM"] = "true"

# Allow running as `python scripts/test_multi_intent.py` from backend/.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402

if REAL and settings.use_mock:
    sys.exit(f"--real needs a usable OPENAI_API_KEY ({settings.mode_reason}).")

if settings.use_mock:
    _store = Path(settings.chroma_persist_dir) / "mock_store.pkl"
    if not _store.exists():
        print(f"Mock store not found at '{_store}' -- building it now...")
        from app.rag.ingest import build_vector_store  # noqa: E402

        build_vector_store()

from fastapi.testclient import TestClient  # noqa: E402
from app.agents.graph import parse_categories  # noqa: E402
from app.main import app  # noqa: E402
from app.suggestions import suggestions_for_categories  # noqa: E402

SOURCE_FOR = {
    "exams": "examinations.md",
    "fees": "fees_and_scholarships.md",
    "hostel": "hostel_and_facilities.md",
    "it": "it_services.md",
    "library": "library_services.md",
    "placements": "placements.md",
    "contact": "contacts_directory.md",
}

# (question, categories it must route to)
MULTI_INTENT = [
    ("What is the hostel curfew, and when are admit cards released?", ["hostel", "exams"]),
    ("How do I reset my portal password, and what are the library timings?", ["it", "library"]),
    (
        "Where can I borrow books, how do I pay tuition, and is there a placement cell?",
        ["library", "fees", "placements"],
    ),
]

# Single-topic questions must NOT be split -- the regression to watch for.
SINGLE_INTENT = [
    ("Can I reset my student portal password myself?", "it"),
    ("When is the placement season?", "placements"),
    ("What's the weather like today?", "contact"),  # off-topic control case
]

failures = []


def check(ok: bool, label: str):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    if not ok:
        failures.append(label)


def test_parser():
    print("parse_categories (router output parsing)")
    cases = [
        ("hostel", ["hostel"]),
        ("Hostel, Exams", ["hostel", "exams"]),
        ("fees,exams\n", ["fees", "exams"]),
        ('"campus-life", it.', ["campus-life", "it"]),
        ("fees, fees, nonsense", ["fees"]),
        ("hostel, exams, fees, library", ["hostel", "exams", "fees"]),  # capped at 3
        ("I'm not sure", ["contact"]),
        ("", ["contact"]),
    ]
    for raw, expected in cases:
        got = parse_categories(raw)
        check(got == expected, f"{raw!r} -> {got} (expected {expected})")


def test_suggestions():
    print("\nsuggestion chips skip what was already asked")
    # (question, categories, chips that must be hidden, chips that must stay)
    cases = [
        (
            "What is the hostel curfew, and when are admit cards released?",
            ["hostel", "exams"],
            ["What is the curfew time?", "When are admit cards released?"],
            ["Can I change my meal plan?"],
        ),
        ("What are hostel fees?", ["hostel"], ["What are the hostel fees?"], ["What is the curfew time?"]),
        (
            "When is the placement season and what's the eligibility?",
            ["placements"],
            ["When is the placement season?", "What is the placement eligibility?"],
            ["Are internships available?"],
        ),
        # A shared verb alone must not hide an unrelated chip.
        ("Can I change rooms in the hostel?", ["hostel"], [], ["Can I change my meal plan?"]),
    ]
    for question, categories, hidden, kept in cases:
        chips = suggestions_for_categories(categories, [question])
        for chip in hidden:
            check(chip not in chips, f"{question!r} hides {chip!r}")
        for chip in kept:
            check(chip in chips, f"{question!r} keeps {chip!r}")


def test_chat(client):
    for question, expected in MULTI_INTENT:
        print(f"\nMULTI  Q: {question}")
        data = client.post("/api/chat", json={"message": question, "history": []}).json()
        cats, sources = data.get("categories", []), data.get("sources", [])
        print(f"  categories: {cats}\n  sources:    {sources}")
        check(set(expected) <= set(cats), f"routed to all of {expected}")
        for c in expected:
            check(SOURCE_FOR[c] in sources, f"retrieved {SOURCE_FOR[c]} for '{c}'")
        check(data.get("category") == cats[0], "`category` is the first of `categories`")
        check(bool(data.get("reply", "").strip()), "non-empty reply")
        check(len(data.get("suggestions", [])) > 0, "follow-up suggestions present")
        check(not any(s.lower().rstrip("?") in question.lower() for s in data.get("suggestions", [])),
              "no chip repeats the question")

    for question, expected in SINGLE_INTENT:
        print(f"\nSINGLE Q: {question}")
        data = client.post("/api/chat", json={"message": question, "history": []}).json()
        cats = data.get("categories", [])
        print(f"  categories: {cats}\n  sources:    {data.get('sources')}")
        check(cats == [expected], f"routed only to '{expected}'")


def test_stream(client):
    question, expected = MULTI_INTENT[0]
    print(f"\nSTREAM Q: {question}")
    events = []
    with client.stream(
        "POST", "/api/chat/stream", json={"message": question, "history": []}
    ) as response:
        for line in response.iter_lines():
            if line.strip():
                events.append(json.loads(line))
    statuses = [e["label"] for e in events if e["type"] == "status"]
    done = next((e for e in events if e["type"] == "done"), {})
    print(f"  statuses:   {statuses}")
    print(f"  categories: {done.get('categories')}")
    check(any(" and " in s and "Searching" in s for s in statuses),
          "status line names every topic being searched")
    check(set(expected) <= set(done.get("categories") or []), "done event carries all categories")


def main():
    print(f"Mode: {'REAL (' + settings.chat_model + ')' if not settings.use_mock else 'mock'}\n")
    test_parser()
    test_suggestions()
    client = TestClient(app)
    test_chat(client)
    test_stream(client)

    print("\n" + "=" * 80)
    if failures:
        print(f"{len(failures)} check(s) failed:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print("All multi-intent checks passed.")


if __name__ == "__main__":
    main()
