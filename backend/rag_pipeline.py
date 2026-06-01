from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

import config

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


@lru_cache(maxsize=1)
def _get_retriever() -> VectorStoreRetriever:
    """Build (once) the retriever over the persisted vector store."""
    if not config.vector_store_exists():
        raise RuntimeError(
            f"No vector store found at {config.CHROMA_DIR}. "
            "Build it first with:  python load_data.py"
        )
    config.require_api_key()
    embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=str(config.CHROMA_DIR),
        embedding_function=embeddings,
    )
    return vectorstore.as_retriever(search_kwargs={"k": config.RETRIEVER_K})


@lru_cache(maxsize=1)
def _get_llm() -> ChatGoogleGenerativeAI:
    """Build (once) the Gemini chat model."""
    config.require_api_key()
    return ChatGoogleGenerativeAI(model=config.LLM_MODEL)


def _response_to_text(content) -> str:
    """Normalise a LangChain message ``content`` into a plain string."""
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict)
    )


def generate_itinerary(
    days: int,
    interests: list[str],
    budget: str,
    start_city: str,
) -> str:
    """Retrieve relevant context and generate an itinerary as Markdown."""
    query = (
        f"{' '.join(interests)} attractions activities Sri Lanka "
        f"{budget} hotels transport from {start_city}"
    )
    relevant_docs = _get_retriever().invoke(query)
    context = "\n\n".join(doc.page_content for doc in relevant_docs)

    prompt_value = _PROMPT.invoke({
        "days": days,
        "interests": ", ".join(interests),
        "budget": budget,
        "start_city": start_city,
        "context": context,
    })

    response = _get_llm().invoke(prompt_value)
    return _response_to_text(response.content)
