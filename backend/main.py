import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from rag_pipeline import generate_itinerary

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Sri Lanka Tourism AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripPreferences(BaseModel):
    days: int
    interests: List[str]
    budget: str
    start_city: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/generate-itinerary")
def generate(preferences: TripPreferences):
    try:
        itinerary = generate_itinerary(
            days=preferences.days,
            interests=preferences.interests,
            budget=preferences.budget,
            start_city=preferences.start_city,
        )
        return {"itinerary": itinerary}
    except Exception as e:
        msg = str(e)
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