import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

load_dotenv()
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("Missing OPENAI_API_KEY in environment!")

from app.ingestion.loader import load_documents
from app.ingestion.chunker import process_documents
from app.embeddings.embedder import get_embeddings_batch
from app.vectorstore.vector_db import upsert_chunks, chroma_client
from app.api.rag import router as rag_router

COLLECTION_NAME = "hr_policies_prod"

def setup_database():
    """Checks if data exists. If not, runs the ingestion pipeline."""
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    if collection.count() > 0:
        print(f"[*] Database ready: {collection.count()} chunks found.")
        return

    print("[*] Empty database detected. Starting ingestion pipeline...")
    docs = load_documents("docs")
    chunks = process_documents(docs, chunk_size=500, overlap=50)
    print(f"[*] Created {len(chunks)} smart chunks. Generating embeddings...")
    texts = [chunk.text for chunk in chunks]
    embeddings = get_embeddings_batch(texts)
    upsert_chunks(COLLECTION_NAME, chunks, embeddings)
    print("[*] Ingestion complete!")

@asynccontextmanager
async def lifespan(app):
    """Runs exactly once when the server starts."""
    print("🚀 Starting up Company RAG Server...")
    setup_database()
    yield
    print("🛑 Shutting down server...")

# Initialize FastAPI App
app = FastAPI(
    title = "Company HR Assistant API",
    description = "A production RAG pipeline for company policies.",
    version = "1.0.0",
    lifespan=lifespan
)

# Attach our API endpoints
app.include_router(rag_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", host = "0.0.0.0", port = 8000, reload = True)

