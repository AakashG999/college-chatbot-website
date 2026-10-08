# College Administration Chatbot Website

A college website with an AI-powered chatbot that answers student queries
about college administration (admissions, fees, academics, exams, hostel
facilities, and general contacts).

## Architecture

- **frontend/** — Plain HTML/CSS/JS site (no build step, no Node required):
  Home, Admissions, Academics, and Contact pages, plus a floating chat
  widget (vanilla JS) that calls the backend.
- **backend/** — FastAPI service exposing `POST /api/chat`, backed by a
  LangGraph multi-agent pipeline:
  1. **Router agent** classifies the question into one of 14 categories
     (admissions, fees, academics, exams, hostel, library, IT, conduct,
     grievance, placements, campus-life, international, health, alumni) or
     falls back to `contact`.
  2. **Retriever node** runs RAG (Retrieval-Augmented Generation) over a
     Chroma vector store built from the markdown knowledge base in
     `backend/app/data/` (15 files, one per topic), filtered by category.
  3. **Answer agent** composes the final reply strictly from the retrieved
     context, citing which source documents it used.
  - LLM provider: OpenAI (`gpt-4o-mini` for chat, `text-embedding-3-small`
    for embeddings by default — configurable via `.env`).

FastAPI serves the `frontend/` folder directly (mounted as static files), so
**one process runs the whole app** — there's no separate frontend server.

```
college-chatbot-website/
├── backend/
│   ├── app/
│   │   ├── agents/      # LangGraph graph + prompts
│   │   ├── api/         # FastAPI routes (/api/chat)
│   │   ├── data/        # Knowledge base (markdown docs with category frontmatter)
│   │   ├── rag/         # Vector store ingestion + retrieval
│   │   ├── config.py
│   │   └── main.py      # also mounts ../frontend as static files
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── admissions.html
    ├── academics.html
    ├── contact.html
    └── assets/
        ├── css/style.css
        └── js/chat-widget.js
```

## Setup and run

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set OPENAI_API_KEY (optional -- see mode auto-detection below)

# Build the vector store from the knowledge base docs (run once, and again
# whenever files under app/data/ change, or whenever you add/remove the key)
python -m app.rag.ingest

# Start the server (serves both the website and the /api/chat endpoint)
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` in your browser for the website (with the chat
widget in the bottom-right corner), and `http://localhost:8000/docs` for the
interactive API docs.

### Mode is auto-detected — real OpenAI if a key is set, mock otherwise

There's nothing to toggle by hand: on startup, the app checks `OPENAI_API_KEY`
in `.env`.

- **A real key is set** → it runs in real mode, calling OpenAI for both
  embeddings and chat.
- **No key (or still the `sk-your-key-here` placeholder)** → it automatically
  falls back to mock mode (see below) so the app still runs end-to-end with
  zero setup.

`uvicorn` prints which mode it picked and why on startup, and `GET
/api/health` reports it too (`{"status": "ok", "mode": "mock" | "real",
"mode_reason": "..."}`). Whenever you add, remove, or change
`OPENAI_API_KEY`, re-run `python -m app.rag.ingest` afterwards — mock and
real mode use separate, incompatible vector stores, so switching modes
without re-ingesting will leave you querying the wrong (or missing) store.

If you ever want to force one mode regardless of whether a key is
configured (e.g. force mock mode for a quick test even with a real key
present), set `USE_MOCK_LLM=true` or `USE_MOCK_LLM=false` in `.env` — an
explicit value always overrides auto-detection.

If you'd rather open the HTML files directly from disk (e.g. via a separate
static file server or a different port) instead of letting FastAPI serve
them, update `ALLOWED_ORIGINS` in `.env` to match that origin so CORS allows
the browser to call `/api/chat`.

## Testing locally with no OpenAI API key (mock mode)

Mock mode runs the entire pipeline with zero external API calls — useful for
verifying the RAG wiring (routing + retrieval + category filtering) before
you have an OpenAI key, or just to sanity-check changes to `app/data/`. It
now turns on **automatically** whenever `OPENAI_API_KEY` isn't set to a real
key (see the auto-detection section above) — you don't need to set
`USE_MOCK_LLM` yourself unless you want to force it on or off explicitly. In
this mode:

- Embeddings are replaced by a deterministic hashed bag-of-words vector
  (`app/rag/mock_store.py`), so similarity search is driven by keyword
  overlap rather than real semantic understanding.
- The chat model is replaced by simple keyword-based routing plus an
  extractive "answer" that returns the top retrieved excerpt verbatim,
  labeled `[MOCK MODE]` (`app/agents/mock_llm.py`).
- Answer *quality* in this mode is not representative of the real thing —
  it only proves that the right source document gets retrieved for a given
  question.

```bash
# With no OPENAI_API_KEY set, this auto-detects mock mode and builds the mock
# store inside CHROMA_PERSIST_DIR (as mock_store.pkl, so it sits alongside any
# real Chroma store there without colliding)
python -m app.rag.ingest

# Run a batch of sample questions through the real /api/chat endpoint and
# print the routed category, retrieved source file, and mock answer for each.
# This always forces mock mode, so it's safe to run even with a real key
# configured, and it builds the mock store first if it isn't there yet.
python scripts/test_mock_chat.py

# Or run the live server (auto-detected mock mode) and use the chat widget
# in the browser
uvicorn app.main:app --reload --port 8000
```

To switch to real answers, set a real `OPENAI_API_KEY` in `.env` — mode
switches automatically, no flag to flip — then re-run `python -m
app.rag.ingest` once against the real `CHROMA_PERSIST_DIR` before starting
the server normally.

## Extending the knowledge base

Add or edit markdown files in `backend/app/data/`. Each file should start
with frontmatter specifying a `category` (one of: `admissions`, `fees`,
`academics`, `exams`, `hostel`, `library`, `it`, `conduct`, `grievance`,
`placements`, `campus-life`, `international`, `health`, `alumni`, `contact`)
and a `title`:

```markdown
---
category: admissions
title: Admissions Process
---

# Admissions
...
```

After editing, re-run `python -m app.rag.ingest` to rebuild the vector
store (mode is auto-detected, so this works whether or not you have an API
key configured).

A standalone, more narratively-written version of this same knowledge base
— useful for handing to non-technical college staff to review and edit — is
in `college-administration-knowledge-base.md` at the project root; it's the
source these 15 files were split from.

## Notes / next steps

- This scaffold uses a single-collection Chroma store filtered by metadata;
  for a larger knowledge base, consider separate collections per category or
  a managed vector DB.
- Conversation history is currently kept client-side only (sent with each
  request); add a persistent session store if you need server-side history
  across page reloads.
- Add authentication in front of the API before deploying publicly if you
  want to restrict usage or track per-student conversations.
