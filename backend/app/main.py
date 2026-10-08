from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.api.feedback import router as feedback_router

FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

app = FastAPI(
    title="College Admin Chatbot API",
    description="LangGraph multi-agent RAG chatbot answering student queries "
    "about college administration (admissions, fees, academics, exams, "
    "hostel, and general contacts).",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
# Demo-only sign-in flow -- see the warning at the top of app/api/auth.py.
app.include_router(auth_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")

_mode = "mock" if settings.use_mock else "real (OpenAI)"
print(f"[college-chatbot] Running in {_mode} mode ({settings.mode_reason}).")
if settings.use_mock:
    print(
        "[college-chatbot] No usable OPENAI_API_KEY found, so answers are "
        "extractive stand-ins, not real LLM responses. Set OPENAI_API_KEY in "
        ".env (and re-run `python -m app.rag.ingest`) to switch to real "
        "OpenAI-backed answers automatically."
    )


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "mode": "mock" if settings.use_mock else "real",
        "mode_reason": settings.mode_reason,
    }


# Serve the plain HTML/CSS/JS site (frontend/) at the root, so the whole app
# (website + chatbot API) runs from this single FastAPI/uvicorn process.
# Must be mounted last so it doesn't shadow the /api routes above.
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
