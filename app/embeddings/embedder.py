import os
from openai import OpenAI

# Initialize client. Ensure load_dotenv() is called in your main script before this runs.
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_embedding(text : str, model : str = 'text-embedding-3-small') -> list[float]:
    """Generates an embedding for a single string."""
    response = client.embeddings.create(input=text, model=model)
    return response.data[0].embedding

def get_embeddings_batch(texts : list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    """Generates embeddings for a list of strings efficiently."""
    response = client.embeddings.create(input=texts, model=model)
    return [data.embedding for data in response.data]


