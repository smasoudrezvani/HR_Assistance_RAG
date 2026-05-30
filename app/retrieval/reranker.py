from sentence_transformers import CrossEncoder
from app.db.models import RetrievedChunk

# Initialize local cross-encoder model (downloads ~80MB on first run)
print("[*] Loading Cross-Encoder Model...")
encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", max_length=512)

def rerank_chunks(query: str, chunks: list[RetrievedChunk], top_k: int = 5) -> list[RetrievedChunk]:
    """Scores query-chunk pairs together and returns the highest precision matches."""
    if not chunks:
        return []
    
    # Prepare pairs format expected by the model: [[query, text], [query, text]]
    pairs = [[query, chunk.text] for chunk in chunks]

    # Predict relevance scores
    scores = encoder.predict(pairs)

    # Attach new cross-encoder scores back to our Pydantic objects
    for chunk, score in zip(chunks, scores):
        chunk.distance = float(score)  # Higher is better for Cross-Encoders
    
    # Sort descending (highest relevance first)
    reranked = sorted(chunks, key= lambda x: x.distance, reverse=True)
    
    return reranked[:top_k]