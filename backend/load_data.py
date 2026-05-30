from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

DATA_FILES = {
    "data/attractions.txt": "attractions",
    "data/hotels.txt":      "hotels",
    "data/transport.txt":   "transport",
}

docs = []
for filepath, category in DATA_FILES.items():
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    docs.append(Document(
        page_content=content,
        metadata={"source": filepath, "category": category}
    ))
    print(f"✅ Read {filepath}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
chunks = splitter.split_documents(docs)
print(f"\n📄 Split into {len(chunks)} chunks")

# store in ChromaDB
print("\n⏳ Embedding chunks with Gemini (takes about 30 seconds)...")

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
)

print(f"\n✅ Done! {len(chunks)} chunks stored in ./chroma_db")