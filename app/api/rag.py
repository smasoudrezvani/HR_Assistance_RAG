from fastapi import APIRouter, HTTPException
from app.db.models import QueryRequest, QueryResponse
from app.retrieval.hybrid import advanced_retrieval 
from app.rag.generator import generate_grounded_answer
from langfuse import observe 
import traceback

router = APIRouter()
COLLECTION_NAME = "hr_policies_prod"

# Lowering this threshold stops the bouncer from blocking good answers.
CONFIDENCE_THRESHOLD = -5.0   # Cross-Encoder Logit Threshold # Lower the threshold to let context through

@router.post("/query", response_model=QueryResponse)
@observe() 
async def ask_question(request: QueryRequest):
    """ Accepts a question, runs it through the RAG pipeline, and returns the grounded answer. """
    try:
        # 1. Fetch top chunks using our Stage 3/4 pipeline
        top_chunks = advanced_retrieval(
            query=request.question, 
            collection_name=COLLECTION_NAME, 
            strategy="rerank" 
        )

        # 2. 📡 THE LOGS BLOCK: This will now explicitly print to your main.py window
        print(f"\n=======================================================")
        print(f"📡 RETRIEVAL INTERCEPT FOR: '{request.question}'")
        print(f"=======================================================")
        print(f"Total Chunks Returned by Pipeline: {len(top_chunks)}")
        
        if top_chunks:
            print(f"Top Chunk ID: {top_chunks[0].id}")
            print(f"Top Chunk Source: {top_chunks[0].filename}")
            print(f"Top Chunk Score (Logit): {top_chunks[0].distance:.4f}")
            print(f"Top Chunk Text Preview: {top_chunks[0].text[:120]}...")
        else:
            print("⚠️ ALERT: The retrieval pipeline returned an EMPTY list!")
        print(f"=======================================================\n")

        # 3. Apply Threshold Guardrail
        if not top_chunks or top_chunks[0].distance < CONFIDENCE_THRESHOLD:
            return QueryResponse(
                answer="I don't have enough information in the current documents to answer that.",
                sources=[]
            )

        # 4. Run Generation
        answer = generate_grounded_answer(request.question, top_chunks)
        unique_sources = list({chunk.filename for chunk in top_chunks})

        return QueryResponse(answer=answer, sources=unique_sources)
        
    except Exception as e:
        print("\n--- 🛑 SERVER CRASH TRACEBACK ---")
        traceback.print_exc()
        print("---------------------------------\n")
        raise HTTPException(status_code=500, detail=str(e))