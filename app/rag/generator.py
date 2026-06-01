import os
from openai import OpenAI
from app.db.models import RetrievedChunk
from langfuse import observe 

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@observe(as_type="generation")
def generate_grounded_answer(query: str, retrieved_chunks: list[RetrievedChunk]) -> str:
    """Takes the user query and strictly typed chunks, and asks GPT for an answer."""
    context_blocks = []
    for chunk in retrieved_chunks:
        context_blocks.append(f"[ID: {chunk.id}] (Source: {chunk.filename})\n{chunk.text}\n")
    
    context_str = "\n".join(context_blocks)

    # # ──── 🔍 DEBUG PRINT BLOCK ────
    # print(f"\n=======================================================")
    # print(f"📬 LLM PROMPT WINDOW FOR QUERY: '{query}'")
    # print(f"=======================================================")
    # print(f"Active Chunks Sent: {len(retrieved_chunks)}")
    # print(f"Context Text Provided:\n{context_str[:1000]}...") # Print first 1000 chars
    # print(f"=======================================================\n")
    # # ──────────────────────────────

    system_prompt = (
        "You are an expert HR assistant. Answer the user's question using ONLY the provided context.\n"
        "CRITICAL INSTRUCTION: Every single factual claim you make MUST be followed by the exact ID of the chunk it came from, formatted as [ID].\n"
        "Example: 'Employees receive 25 vacation days [a1b2c3d4].'\n"
        "If you combine facts from multiple chunks, cite all of them: [a1b2c3d4][f9e8d7c6].\n"
        "If the context does not contain the answer, say exactly: 'I don't have enough information in the current documents to answer that.'"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {query}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.0
    )

    return response.choices[0].message.content