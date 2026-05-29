import os
from openai import OpenAI
from app.db.models import RetrievedChunk
from langfuse import observe

# Initialize client (main.py will have already loaded the .env file)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@observe(as_type = "generation")
def generate_grounded_answer(query : str, retrieved_chunks : list[RetrievedChunk]) -> str:
    """Takes the user query and strictly typed chunks, and asks GPT for an answer."""

    # Extract the text and filename from our Pydantic models
    context_text = "\n\n---\n\n".join(
        [f"Source: {chunk.filename}\n{chunk.text}" for chunk in retrieved_chunks]
    )

    system_prompt = f""" You are a helpful HR and Company Policy assistant. 
    You will be provided with context from internal company documents.
    Answer the user's question using ONLY the provided context. 
    If the answer is not contained in the context, say "I don't have enough information in the current documents to answer that."
    Do not make up policies or guess.

    CONTEXT:
    {context_text}"""

    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature = 0.0, # We want deterministic answers

    )

    return response.choices[0].message.content


