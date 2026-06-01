# Ceylon Compass · AI Sri Lanka Travel Planner

Ceylon Compass is a full-stack AI travel planner that generates personalized,
day-by-day Sri Lanka itineraries. Tell it how long you're travelling, what you're
into, your budget and your starting city — and it crafts a practical plan with
morning/afternoon/evening activities, food picks, accommodation suggestions and
transport between stops.

Under the hood it uses **Retrieval-Augmented Generation (RAG)**: a curated
knowledge base of Sri Lankan attractions, hotels and transport is embedded into a
vector store, the most relevant facts are retrieved for each request, and Google
Gemini writes the itinerary grounded in that knowledge.

---

## Features

- 🗺️ **Day-by-day itineraries** with realistic travel times for Sri Lanka's slow roads
- 🎯 **Tailored to you** — trip length (1–14 days), interests, budget level and starting city
- 🧠 **Grounded in real data** — recommendations come from a local knowledge base, not hallucinations
- 🍛 Food, accommodation and transport suggestions for every day
- 📋 Copy or print the generated plan
- ⚡ Clean React UI with loading, empty and error states

## How it works

```
 data/*.txt ──► load_data.py ──► chunks ──► Gemini embeddings ──► ChromaDB (./chroma_db)
                                                                        │
 User fills form ──► POST /generate-itinerary ──► retrieve top-5 relevant chunks
                                                                        │
                                              prompt + context ──► Gemini (LLM)
                                                                        │
                                              Markdown itinerary ──► React UI
```

1. **Ingestion** ([backend/load_data.py](backend/load_data.py)) reads the text
   files in [backend/data/](backend/data/), splits them into chunks, embeds them
   with Gemini and stores the vectors in a local ChromaDB at `backend/chroma_db/`.
2. **Retrieval + generation** ([backend/rag_pipeline.py](backend/rag_pipeline.py))
   turns the user's preferences into a query, pulls the 5 most relevant chunks,
   injects them into a prompt template and asks Gemini to write the itinerary.
3. **API** ([backend/main.py](backend/main.py)) exposes the pipeline over a small
   FastAPI service.
4. **Frontend** ([frontend/src/App.jsx](frontend/src/App.jsx)) collects preferences
   and renders the returned Markdown.

## Tech stack

| Layer       | Technologies                                                              |
| ----------- | ------------------------------------------------------------------------- |
| Frontend    | React 19, Vite, react-markdown                                            |
| Backend     | FastAPI, Uvicorn, Pydantic                                                |
| AI / RAG    | LangChain, ChromaDB, Google Gemini (chat + embeddings)                    |
| Tooling     | `uv` (Python deps), npm (JS deps)                                         |

## Project structure

```
sl-tourism-ai/
├── backend/
│   ├── main.py            # FastAPI app & routes
│   ├── rag_pipeline.py    # RAG: retrieve context + generate itinerary
│   ├── load_data.py       # Build the vector store from data/*.txt
│   ├── test_pipeline.py   # Quick CLI smoke test of the pipeline
│   ├── data/              # Knowledge base (attractions, hotels, transport)
│   ├── chroma_db/         # Generated vector store (git-ignored)
│   ├── pyproject.toml     # Python dependencies
│   └── .env               # GOOGLE_API_KEY (git-ignored)
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   └── components/
    │       ├── PreferenceForm.jsx     # Trip preferences input
    │       └── ItineraryDisplay.jsx   # Renders the itinerary
    └── package.json
```

## Prerequisites

- **Python 3.11+** and [`uv`](https://docs.astral.sh/uv/) (or use `pip` + `venv`)
- **Node.js 18+** and npm
- A **Google Gemini API key** — create one for free at
  [Google AI Studio](https://aistudio.google.com/app/apikey)

## Getting started

### 1. Backend

```bash
cd backend

# Add your API key
echo "GOOGLE_API_KEY=your_key_here" > .env

# Install dependencies
uv sync

# Build the vector store (one-time; re-run when you change data/*.txt)
uv run python load_data.py

# Start the API on http://localhost:8000
uv run uvicorn main:app --reload --port 8000
```

> Using plain `pip` instead of `uv`? Create a virtualenv, then
> `pip install fastapi uvicorn python-dotenv langchain langchain-chroma langchain-google-genai langchain-text-splitters chromadb`
> and run the same `python load_data.py` / `uvicorn` commands.

Sanity check the pipeline without the frontend:

```bash
uv run python test_pipeline.py
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the printed URL (Vite defaults to **http://localhost:5173**). The frontend
calls the backend at `http://localhost:8000`, and the backend's CORS is configured
for `http://localhost:5173`, so keep those ports unless you update both sides.

## Environment variables

The backend reads a single variable from `backend/.env`:

| Variable         | Description                          |
| ---------------- | ------------------------------------ |
| `GOOGLE_API_KEY` | Your Google Gemini API key (required) |

`.env` is git-ignored — **never commit your API key.**

## API reference

### `GET /health`

Health check.

```json
{ "status": "ok" }
```

### `POST /generate-itinerary`

Generate an itinerary from trip preferences.

**Request body**

```json
{
  "days": 5,
  "interests": ["beach", "culture", "wildlife"],
  "budget": "mid-range",
  "start_city": "Colombo"
}
```

| Field        | Type       | Notes                                              |
| ------------ | ---------- | -------------------------------------------------- |
| `days`       | int        | Trip length (UI allows 1–14)                       |
| `interests`  | string[]   | e.g. `beach`, `culture`, `wildlife`, `hiking`, `history`, `food` |
| `budget`     | string     | `budget`, `mid-range` or `luxury`                  |
| `start_city` | string     | e.g. `Colombo`, `Kandy`, `Galle`, `Negombo`        |

**Response**

```json
{ "itinerary": "Day 1: ...markdown..." }
```

**Errors**

- `429` — Gemini free-tier quota/rate limit reached; wait and retry.
- `502` — Itinerary generation failed; retry.

## Customizing the knowledge base

The AI only recommends places it knows about. To extend or change its knowledge,
edit the text files in [backend/data/](backend/data/):

- `attractions.txt` — sights, parks, towns
- `hotels.txt` — accommodation by budget tier
- `transport.txt` — how to get around

After editing, rebuild the vector store:

```bash
cd backend
uv run python load_data.py
```

## Notes

- Itineraries are AI-generated — double-check entry fees, opening times and
  transport details before you travel.
- The vector store (`backend/chroma_db/`) and `.env` are git-ignored. A fresh
  clone must run `load_data.py` before the API can return results.
- The embedding model in [load_data.py](backend/load_data.py) must match the one
  in [rag_pipeline.py](backend/rag_pipeline.py), or retrieval will fail — keep them
  in sync if you change models.
