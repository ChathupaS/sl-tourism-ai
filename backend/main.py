from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from rag_pipeline import generate_itinerary

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
        raise HTTPException(status_code=500, detail=str(e))