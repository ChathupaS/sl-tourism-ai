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
│   ├── main.py            # FastAPI app, routes & request validation
│   ├── rag_pipeline.py    # RAG: retrieve context + generate itinerary
│   ├── load_data.py       # Build the vector store from data/*.txt
│   ├── config.py          # Central settings (models, paths, CORS) from env
│   ├── test_pipeline.py   # Quick CLI smoke test of the pipeline
│   ├── data/              # Knowledge base (attractions, hotels, transport)
│   ├── chroma_db/         # Generated vector store (git-ignored)
│   ├── pyproject.toml     # Python dependencies
│   ├── .env.example       # Copy to .env and fill in your API key
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

# Add your API key (copy the template, then edit .env)
cp .env.example .env        # then put your key in GOOGLE_API_KEY

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

The backend reads its settings from `backend/.env` (see
[backend/.env.example](backend/.env.example)). Only `GOOGLE_API_KEY` is
required; everything else has a sensible default and is centralized in
[backend/config.py](backend/config.py).

| Variable         | Default              | Description                                            |
| ---------------- | -------------------- | ----------------------------------------------------- |
| `GOOGLE_API_KEY` | —                    | Your Google Gemini API key (**required**)             |
| `EMBEDDING_MODEL`| `gemini-embedding-2` | Embedding model — used for both build and query       |
| `LLM_MODEL`      | `gemini-2.5-flash`   | Chat model that writes the itinerary                  |
| `RETRIEVER_K`    | `5`                  | Number of knowledge chunks retrieved per request      |
| `CHUNK_SIZE`     | `500`                | Character chunk size when building the vector store   |
| `CHUNK_OVERLAP`  | `50`                 | Character overlap between chunks                       |
| `CHROMA_DIR`     | `./chroma_db`        | Where the vector store is persisted                   |
| `DATA_DIR`       | `./data`             | Where the knowledge-base `.txt` files live            |
| `CORS_ORIGINS`   | `http://localhost:5173` | Comma-separated allowed frontend origins           |

`.env` is git-ignored — **never commit your API key.**

## API reference

### `GET /health`

Health check. `vector_store_ready` is `false` until you've run `load_data.py`.

```json
{ "status": "ok", "vector_store_ready": true }
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
| `days`       | int        | Trip length, **1–14** (validated)                  |
| `interests`  | string[]   | At least one, e.g. `beach`, `culture`, `wildlife`, `hiking`, `history`, `food` |
| `budget`     | string     | One of `budget`, `mid-range`, `luxury` (validated) |
| `start_city` | string     | Non-empty, e.g. `Colombo`, `Kandy`, `Galle`, `Negombo` |

Invalid input is rejected with `422` and a message describing the offending field.

**Response**

```json
{ "itinerary": "Day 1: ...markdown..." }
```

**Errors**

- `422` — Invalid request body (e.g. `days` out of range, unknown `budget`, no interests).
- `429` — Gemini free-tier quota/rate limit reached; wait and retry.
- `502` — Itinerary generation failed; retry.
- `503` — Vector store not built yet; run `load_data.py` first.

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
- Build-time and query-time embeddings must use the **same** model or retrieval
  fails. Both now read `EMBEDDING_MODEL` from
  [config.py](backend/config.py), so change it in one place — and rebuild the
  vector store (`load_data.py`) afterwards.
