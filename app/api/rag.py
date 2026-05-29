from fastapi import APIRouter, HTTPException
from app.db.models import QueryRequest, QueryResponse
from app.embeddings.embedder import get_embedding
from app.vectorstore.vector_db import query_db
from app.rag.generator import generate_grounded_answer
from langfuse import observe

# Create a router to group our RAG endpoints
router = APIRouter()

COLLECTION_NAME = "hr_policies_prod"

@router.post("/query", response_model=QueryResponse)
@observe()
async def ask_question(request: QueryRequest):
    """
    Accepts a question, runs it through the RAG pipeline, and returns the grounded answer.
    """
    try:
        # 1. Embed Query
        query_vector = get_embedding(request.question)

        # 2. Retrieve context from ChromaDB
        top_chunks = query_db(COLLECTION_NAME, query_vector, top_k=3)

        if not top_chunks:
            return QueryResponse(
                answer="Sorry, I couldn't find any relevant context in the company policies.",
                sources=[]
                )
        
        # 3. Generate Answer
        answer = generate_grounded_answer(request.question, top_chunks)

        # 4. Extract unique source filenames for the response
        # We use a set comprehension to ensure we don't list the same file twice
        unique_sources = list({chunk.filename for chunk in top_chunks})

        # Return strictly formatted JSON
        return QueryResponse(
            answer=answer,
            sources=unique_sources
        )

    except Exception as e:
        # If anything breaks (e.g., OpenAI API is down), return a clean 500 error
        raise HTTPException(status_code=500, detail=str(e))
