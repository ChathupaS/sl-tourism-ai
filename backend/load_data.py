from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config

# Source filename (inside config.DATA_DIR) -> category metadata.
DATA_FILES = {
    "attractions.txt": "attractions",
    "hotels.txt": "hotels",
    "transport.txt": "transport",
}


def load_documents() -> list[Document]:
    """Read each knowledge-base file into a tagged Document."""
    docs: list[Document] = []
    for filename, category in DATA_FILES.items():
        path = config.DATA_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing data file: {path}")
        docs.append(Document(
            page_content=path.read_text(encoding="utf-8"),
            metadata={"source": str(path), "category": category},
        ))
        print(f"✅ Read {path}")
    return docs


def build_vector_store() -> int:
    """Embed the knowledge base and persist it to ChromaDB.

    Returns the number of chunks stored.
    """
    config.require_api_key()

    docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    print(f"\n📄 Split into {len(chunks)} chunks")

    print(f"\n⏳ Embedding chunks with {config.EMBEDDING_MODEL} (takes about 30 seconds)...")
    embeddings = GoogleGenerativeAIEmbeddings(model=config.EMBEDDING_MODEL)

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(config.CHROMA_DIR),
    )
    print(f"\n✅ Done! {len(chunks)} chunks stored in {config.CHROMA_DIR}")
    return len(chunks)


if __name__ == "__main__":
    build_vector_store()
