import logging
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

import config
from rag_pipeline import generate_itinerary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Sri Lanka Tourism AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TripPreferences(BaseModel):
    days: int = Field(..., ge=1, le=14, description="Trip length in days (1–14).")
    interests: list[str] = Field(..., min_length=1, description="At least one interest.")
    budget: Literal["budget", "mid-range", "luxury"]
    start_city: str = Field(..., min_length=1, description="City the trip starts from.")

    @field_validator("interests")
    @classmethod
    def _clean_interests(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        if not cleaned:
            raise ValueError("Provide at least one non-empty interest.")
        return cleaned

    @field_validator("start_city")
    @classmethod
    def _clean_start_city(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("start_city must not be empty.")
        return cleaned


@app.get("/health")
def health():
    """Liveness + readiness: reports whether the vector store is built."""
    return {
        "status": "ok",
        "vector_store_ready": config.vector_store_exists(),
    }


@app.post("/generate-itinerary")
def generate(preferences: TripPreferences):
    if not config.vector_store_exists():
        raise HTTPException(
            status_code=503,
            detail=(
                "The knowledge base isn't ready yet. Build the vector store "
                "by running load_data.py, then try again."
            ),
        )

    try:
        itinerary = generate_itinerary(
            days=preferences.days,
            interests=preferences.interests,
            budget=preferences.budget,
            start_city=preferences.start_city,
        )
    except Exception as exc:
        msg = str(exc)
        if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
            logger.warning("Gemini rate limit / quota hit: %s", msg)
            raise HTTPException(
                status_code=429,
                detail=(
                    "The AI model is rate-limited right now (Gemini free-tier "
                    "quota reached). Wait a minute and try again, or check the "
                    "API key's quota in Google AI Studio."
                ),
            )
        logger.exception("Failed to generate itinerary")
        raise HTTPException(
            status_code=502,
            detail="Could not generate the itinerary. Please try again.",
        )

    return {"itinerary": itinerary}
