from sentence_transformers import CrossEncoder
from app.db.models import RetrievedChunk

# Load the model once into memory
reranker_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)

def rerank_chunks(query: str, chunks: list[RetrievedChunk], top_k: int = 5) -> list[RetrievedChunk]:
    """Scores chunks using a Cross-Encoder and sorts by highest relevancy."""
    if not chunks:
        return []
        
    # Prepare the pairs for the Cross-Encoder: [ [query, text1], [query, text2], ... ]
    pairs = [[query, chunk.text] for chunk in chunks]
    
    # Predict returns a list of logit scores
    scores = reranker_model.predict(pairs)
    
    # Attach the new scores to our chunks
    for idx, chunk in enumerate(chunks):
        chunk.distance = float(scores[idx]) 
        
    # THE CRITICAL FIX: reverse=True ensures HIGHEST scores (best matches) go to the top!
    chunks.sort(key=lambda x: x.distance, reverse=True)
    
    return chunks[:top_k]