from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

_embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

_vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=_embeddings,
)

_retriever = _vectorstore.as_retriever(search_kwargs={"k": 5})

_llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash")

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

def generate_itinerary(days: int, interests: list, budget: str, start_city: str) -> str:

    query = (
        f"{' '.join(interests)} attractions activities Sri Lanka "
        f"{budget} hotels transport from {start_city}"
    )
    relevant_docs = _retriever.invoke(query)

    context = "\n\n".join(doc.page_content for doc in relevant_docs)

    prompt_value = _PROMPT.invoke({
        "days": days,
        "interests": ", ".join(interests),
        "budget": budget,
        "start_city": start_city,
        "context": context,
    })

    response = _llm.invoke(prompt_value)
    if isinstance(response.content, str):
        return response.content

    return "".join(
        block.get("text", "")
        for block in response.content
        if isinstance(block, dict)
    )