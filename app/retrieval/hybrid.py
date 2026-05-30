from app.db.models import RetrievedChunk
from app.embeddings.embedder import get_embedding
from app.vectorstore.vector_db import query_dense, query_sparse
from app.retrieval.reranker import rerank_chunks

def reciprocal_rank_fusion(dense_results: list[RetrievedChunk], sparse_results: list[RetrievedChunk], k: int = 60) -> list[RetrievedChunk]:
    """Combines dense and sparse results using RRF math."""
    rrf_scores = {}
    chunk_map = {}

    def score_list(results: list[RetrievedChunk]):
        for rank, chunk in enumerate(results, start=1):
            if chunk.id not in rrf_scores:
                rrf_scores[chunk.id] = 0.0
                chunk_map[chunk.id] = chunk
            # The RRF Math
            rrf_scores[chunk.id] += 1.0 / (k + rank)
    
    score_list(dense_results)
    score_list(sparse_results)

    # Re-sort the combined chunks based on their new RRF scores
    fused_chunks = []
    for chunk_id, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True):
        chunk = chunk_map[chunk_id]
        chunk.distance = score # Overwrite with the RRF score
        fused_chunks.append(chunk)

    return fused_chunks

def advanced_retrieval(query: str, collection_name: str, strategy: str = "rerank") -> list[RetrievedChunk]:
    """Master routing function for all retrieval strategies."""

    # Strategy 1: Naive (Stage 1 Baseline)
    if strategy == "naive":
        query_vector = get_embedding(query)
        return query_dense(collection_name, query_vector, top_k=3)
    
    # Strategy 2: Hybrid only (Dense + Sparse + RRF)
    elif strategy == "hybrid":
        query_vector = get_embedding(query)
        dense = query_dense(collection_name, query_vector, top_k=5)
        sparse = query_sparse(query, top_k=5)
        return reciprocal_rank_fusion(dense, sparse)[:3]
    
    # Strategy 3: Full Production (High Recall Hybrid + High Precision Rerank)
    elif strategy == "rerank":
        # 1. High Recall Phase (Cast a wide net)
        query_vector = get_embedding(query)
        dense = query_dense(collection_name, query_vector, top_k=15)
        sparse = query_sparse(query, top_k=15)
        fused = reciprocal_rank_fusion(dense, sparse)
        
        # 2. High Precision Phase (Cross-Encoder filtering)
        return rerank_chunks(query, fused, top_k=3)