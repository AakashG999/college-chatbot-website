"""Centralized app settings, loaded from environment variables (.env)."""
import os
from dotenv import load_dotenv

load_dotenv()


def _as_bool(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


# Values that mean "no real key was actually provided" -- e.g. the
# placeholder left in .env.example if someone copies it without editing it.
_PLACEHOLDER_API_KEYS = {"", "sk-your-key-here", "your-key-here", "changeme"}


def _looks_like_real_api_key(key: str) -> bool:
    return key.strip() not in _PLACEHOLDER_API_KEYS


_openai_api_key = os.getenv("OPENAI_API_KEY", "")

# Mock mode runs the whole RAG pipeline with no external API calls: a hashed
# bag-of-words vector store stands in for OpenAI embeddings, and a
# keyword/extractive stand-in replaces the chat model. Good for wiring and
# local testing, not for real answer quality.
#
# Resolution order:
#   1. USE_MOCK_LLM set explicitly (true/false) -> always respected, so you
#      can still force mock mode even with a real key configured.
#   2. Otherwise, auto-detected: mock mode turns on automatically when no
#      usable OPENAI_API_KEY is set, and off automatically once a real key
#      is in place -- no env var needs to change by hand.
_use_mock_override = os.getenv("USE_MOCK_LLM")
if _use_mock_override is not None:
    _use_mock = _as_bool(_use_mock_override)
    _mode_reason = f"USE_MOCK_LLM explicitly set to '{_use_mock_override}'"
elif _looks_like_real_api_key(_openai_api_key):
    _use_mock = False
    _mode_reason = "OPENAI_API_KEY is set"
else:
    _use_mock = True
    _mode_reason = "no OPENAI_API_KEY configured (or it's still the .env.example placeholder)"


class Settings:
    openai_api_key: str = _openai_api_key
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    chroma_persist_dir: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
        if origin.strip()
    ]
    use_mock: bool = _use_mock
    mode_reason: str = _mode_reason

    @property
    def collection_name(self) -> str:
        return "college_admin_kb_mock" if self.use_mock else "college_admin_kb"


settings = Settings()
