from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# ----------------------------------------------------------------
# These are loaded ONCE when the server starts, not on every request.
# Loading ChromaDB and the LLM on every request would be very slow.
# ----------------------------------------------------------------

print("⏳ Loading ChromaDB and Gemini...")

_embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

_vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=_embeddings,
)

# k=5 means: return the 5 most relevant chunks from ChromaDB
_retriever = _vectorstore.as_retriever(search_kwargs={"k": 5})

_llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

print("✅ RAG pipeline ready")

# ----------------------------------------------------------------
# Prompt template — this is what gets sent to Gemini.
# The {placeholders} get filled in at runtime.
# ----------------------------------------------------------------

_PROMPT = ChatPromptTemplate.from_template("""
You are an expert Sri Lanka travel guide with deep knowledge of the island.

Create a detailed day-by-day itinerary based on these traveller preferences:
- Duration: {days} days
- Interests: {interests}
- Budget level: {budget}
- Starting city: {start_city}

Use this knowledge about Sri Lanka to plan the trip:
{context}

Write a practical itinerary with the following for each day:
- A clear "Day X:" heading
- Morning, afternoon and evening plan
- One food recommendation
- Accommodation suggestion matching the {budget} budget
- How to get to the next destination

Keep travel times realistic — Sri Lanka roads are slow.
Only recommend places mentioned in the knowledge above.
""")


# ----------------------------------------------------------------
# Main function — called by the FastAPI endpoint
# ----------------------------------------------------------------

def generate_itinerary(days: int, interests: list, budget: str, start_city: str) -> str:

    # Step 1: Build a search query from the user's preferences.
    # This is what we search ChromaDB with.
    query = (
        f"{' '.join(interests)} attractions activities Sri Lanka "
        f"{budget} hotels transport from {start_city}"
    )

    # Step 2: Search ChromaDB — returns the 5 most relevant text chunks
    relevant_docs = _retriever.invoke(query)

    # Step 3: Join the chunks into one block of context text
    context = "\n\n".join(doc.page_content for doc in relevant_docs)

    # Step 4: Fill in the prompt template with real values
    prompt_value = _PROMPT.invoke({
        "days": days,
        "interests": ", ".join(interests),
        "budget": budget,
        "start_city": start_city,
        "context": context,
    })

    # Step 5: Send to Gemini and return the text response
    response = _llm.invoke(prompt_value)
    if isinstance(response.content, str):
        return response.content

    return "".join(
        block.get("text", "")
        for block in response.content
        if isinstance(block, dict)
    )