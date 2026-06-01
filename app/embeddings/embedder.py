import os
from openai import OpenAI

# Initialize client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL_NAME = "text-embedding-3-small"

def get_embedding(text: str) -> list[float]:
    """Generates an embedding for a single string query."""
    response = client.embeddings.create(
        input=[text],
        model=MODEL_NAME
    )
    return response.data[0].embedding

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generates embeddings for a batch of text chunks during ingestion."""
    if not texts:
        return []
    response = client.embeddings.create(
        input=texts,
        model=MODEL_NAME
    )
    return [item.embedding for item in response.data]


