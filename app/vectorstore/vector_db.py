import chromadb
from app.db.models import Chunk, RetrievedChunk

# Persistent client connected to your local directory
chroma_client = chromadb.PersistentClient(path="./chroma_data")

def upsert_chunks(collection_name: str, chunks: list[Chunk], embeddings: list[list[float]]):
    """Stores chunks and their embeddings in ChromaDB."""
    collection = chroma_client.get_or_create_collection(name=collection_name)
    
    # Unpack the Pydantic models for Chroma
    ids = [chunk.id for chunk in chunks]
    texts = [chunk.text for chunk in chunks]
    metadatas = [{"filename": chunk.filename} for chunk in chunks]
    
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

def query_db(collection_name: str, query_embedding: list[float], top_k: int = 5) -> list[RetrievedChunk]:
    """Searches ChromaDB using a query vector and returns Pydantic RetrievedChunk models."""
    collection = chroma_client.get_or_create_collection(name=collection_name)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    retrieved_chunks = []
    # Safeguard: check if results exist
    if not results['documents'] or not results['documents'][0]:
        return retrieved_chunks

    # Repackage Chroma's dictionary output back into our Pydantic models
    for i in range(len(results['documents'][0])):
        chunk = RetrievedChunk(
            id=results['ids'][0][i],
            text=results['documents'][0][i],
            filename=results['metadatas'][0][i]['filename'],
            distance=results['distances'][0][i]
        )
        retrieved_chunks.append(chunk)
        
    return retrieved_chunks