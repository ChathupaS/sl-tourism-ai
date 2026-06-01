import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(
            f"Environment variable {name!r} must be an integer, got {raw!r}."
        ) from exc


DATA_DIR = Path(os.getenv("DATA_DIR") or BASE_DIR / "data")
CHROMA_DIR = Path(os.getenv("CHROMA_DIR") or BASE_DIR / "chroma_db")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

RETRIEVER_K = _get_int("RETRIEVER_K", 5)
CHUNK_SIZE = _get_int("CHUNK_SIZE", 500)
CHUNK_OVERLAP = _get_int("CHUNK_OVERLAP", 50)

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]


def require_api_key() -> str:
    """Return the Google API key, or raise a clear error if it's missing."""
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Add it to backend/.env "
            "(GOOGLE_API_KEY=your_key_here). Create a free key at "
            "https://aistudio.google.com/app/apikey."
        )
    return key


def vector_store_exists() -> bool:
    """True once a ChromaDB vector store has been built at CHROMA_DIR."""
    return (CHROMA_DIR / "chroma.sqlite3").exists()
