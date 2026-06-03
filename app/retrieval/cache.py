import json
from app.vectorstore.vector_db import chroma_client
from app.embeddings.embedder import get_embedding

CACHE_COLLECTION = "semantic_cache"
# The distance threshold. Lower means stricter matching. 
# 0.15 requires the phrasing to be extremely similar semantically.
CACHE_THRESHOLD = 0.30

def check_cache(query : str):
    """Checks if a semantically identical question has been asked recently."""
    collection = chroma_client.get_or_create_collection(CACHE_COLLECTION)

    # If the cache is empty, skip
    if collection.count() == 0:
        return None

    query_vector = get_embedding(query)
    results = collection.query(
        query_embeddings = [query_vector],
        n_results = 1,
        include = ["metadatas", "distances"]
    )

    if results and results["ids"] and results["ids"][0]:
        distance = results["distances"][0][0]
        
        if distance < CACHE_THRESHOLD:
            print(f"⚡ CACHE HIT! Distance: {distance:.4f} (Threshold: {CACHE_THRESHOLD})")
            metadata = results["metadatas"][0][0]
            return {
                "answer": metadata["answer"],
                "sources": json.loads(metadata["sources"])
            }
        else:
            # THE NEW DEBUG LOG: Show exactly how far away the closest match was
            print(f"🐌 CACHE MISS! Closest match was distance {distance:.4f} (Needed < {CACHE_THRESHOLD})")
    
    return None

def store_in_cache(query : str, answer: str, sources: list):
    """Saves the generated answer into the vector database for future use."""
    collection = chroma_client.get_or_create_collection(name=CACHE_COLLECTION)
    query_vector = get_embedding(query)

    # Serialize the Pydantic source models (Source(BaseModel) object) into JSON for storage
    # sincee chroma doesn't support storing complex objects directly.
    # Before (Pydantic model object)
    # example:
    # source = Source(title="Python Docs", url="https://...", page_number=5)

    # After .model_dump()
    # {'title': 'Python Docs', 'url': 'https://...', 'page_number': 5}

    # Then json.dumps() converts to string
    # '{"title": "Python Docs", "url": "https://...", "page_number": 5}'
    
    serialized_sources = [s.model_dump() if hasattr(s, 'model_dump') else s for s in sources]
    
    collection.upsert(
        ids=[query], # Use the literal question string as the unique ID
        embeddings=[query_vector],
        documents=[query],
        metadatas=[{
            "answer": answer,
            "sources": json.dumps(serialized_sources)
        }]
    )