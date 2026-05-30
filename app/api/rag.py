from fastapi import APIRouter, HTTPException
from app.db.models import QueryRequest, QueryResponse
from app.retrieval.hybrid import advanced_retrieval
from app.rag.generator import generate_grounded_answer
from langfuse import observe
import traceback

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
        # UPGRADE: replaced the raw query_db with our advanced router
        top_chunks = advanced_retrieval(
            query=request.question,
            collection_name=COLLECTION_NAME,
            strategy="rerank" # Switch to "naive" or "hybrid" to compare
        )

        if not top_chunks:
            return QueryResponse(
                answer="I couldn't find any relevant context in the company policies.",
                sources=[]
            )

        answer = generate_grounded_answer(request.question, top_chunks)
        unique_sources = list({chunk.filename for chunk in top_chunks})

        return QueryResponse(answer=answer, sources=unique_sources)
        
    except Exception as e:
        print("\n--- 🛑 SERVER CRASH TRACEBACK ---")
        traceback.print_exc()
        print("---------------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))
