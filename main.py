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
from app.db.models import Chunk
from app.vectorstore.vector_db import sync_sparse_index

COLLECTION_NAME = "hr_policies_prod"

def setup_database():
    """Checks if data exists. If not, ingests. If yes, syncs BM25."""
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    
    if collection.count() > 0:
        print(f"[*] Database ready: {collection.count()} chunks found.")
        print("[*] Rebuilding BM25 Sparse Index from ChromaDB data...")
        
        # Fetch all existing documents from Chroma to rebuild BM25 in RAM
        existing_data = collection.get(include=["documents", "metadatas"])
        rebuilt_chunks = []
        for i in range(len(existing_data["ids"])):
            rebuilt_chunks.append(Chunk(
                id=existing_data["ids"][i],
                filename=existing_data["metadatas"][i]["filename"],
                text=existing_data["documents"][i]
            ))
        sync_sparse_index(rebuilt_chunks)
        return

    print("[*] Empty database detected. Starting ingestion pipeline...")
    docs = load_documents("docs")
    # Give chunks room to breathe so paragraphs don't break
    chunks = process_documents(docs, chunk_size=1500, overlap=200)
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
    uvicorn.run("main:app", host ="0.0.0.0", port = 8000, reload = True)

