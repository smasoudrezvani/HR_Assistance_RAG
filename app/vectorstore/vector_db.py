from chromadb import PersistentClient
from app.db.models import Chunk, RetrievedChunk
import os
from rank_bm25 import BM25Okapi
import string


# Initialize local persistent ChromaDB client
DB_DIR = os.path.join(os.getcwd(), "chroma_data")
chroma_client = PersistentClient(path=DB_DIR)

# Global in-memory storage for the BM25 Sparse Index
BM25_INDEX = None
BM25_CHUNKS_MAP = []

def tokenize_text(text: str) -> list[str]:
    """Helper to split text into lowercase tokens and remove basic punctuation."""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.split()

def sync_sparse_index(chunks: list[Chunk]):
    """Builds the BM25 index in memory using the processed system chunks."""
    global BM25_INDEX, BM25_CHUNKS_MAP
    print(f"[*] Syncing BM25 sparse index with {len(chunks)} chunks...")

    tokenized_corpus = [tokenize_text(chunk.text) for chunk in chunks]
    BM25_INDEX = BM25Okapi(tokenized_corpus)
    BM25_CHUNKS_MAP = chunks  # Keeps a parallel array matching the index order

def query_dense(collection_name: str, query_embedding: list[float], top_k: int = 3) -> list[RetrievedChunk]:
    """Pure Vector/Dense Search."""
    collection = chroma_client.get_or_create_collection(name=collection_name)
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    retrieved_chunks = []
    
    if not results or not results.get("ids") or not results["ids"][0]:
        return retrieved_chunks
        
    # THE FIX: Ensure we loop through 'ids'
    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        retrieved_chunks.append(RetrievedChunk(
            id=results["ids"][0][i],
            filename=metadata["filename"],
            text=results["documents"][0][i],
            distance=results["distances"][0][i]
        ))
    return retrieved_chunks

def query_sparse(query: str, top_k: int = 5) -> list[RetrievedChunk]:
    """Pure Sparse Search: Uses the BM25 index to find relevant chunks based on keyword matching."""
    global BM25_INDEX, BM25_CHUNKS_MAP
    if BM25_INDEX is None:
        return []
    
    tokenized_query = tokenize_text(query)
    # Get raw scores for all documents in the index
    scores = BM25_INDEX.get_scores(tokenized_query)
    
    # Sort indices by highest score descending
    top_indices = sorted(range(len(scores)), key= lambda i: scores[i], reverse=True)[:top_k]

    retrieved_chunks = []
    for idx in top_indices:
        if scores[idx] == 0:  # Skip chunks with zero keyword overlap
            continue
        chunk = BM25_CHUNKS_MAP[idx]
        # Normalize sparse scores into a pseudo-distance layout for contract compatibility
        pseudo_distance = 1.0 / (1.0 + scores[idx])
        retrieved_chunks.append(RetrievedChunk(
            id=chunk.id,
            filename=chunk.filename,
            text=chunk.text,
            distance=pseudo_distance
        ))
    
    return retrieved_chunks


def upsert_chunks(collection_name: str, chunks: list[Chunk], embeddings: list[list[float]]):
    """Saves chunks to ChromaDB and automatically kicks off a BM25 index re-sync."""
    collection = chroma_client.get_or_create_collection(name=collection_name)
    
    ids = [chunk.id for chunk in chunks]
    documents = [chunk.text for chunk in chunks]
    metadatas = [{"filename": chunk.filename} for chunk in chunks]
    
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )

    sync_sparse_index(chunks)