import os
import pytest
from dotenv import load_dotenv

# Load environment variables BEFORE importing app modules
load_dotenv()
assert os.environ.get("OPENAI_API_KEY") is not None, "Missing OPENAI_API_KEY in environment!"

from app.db.models import Document, Chunk
from app.ingestion.chunker import process_documents
from app.embeddings.embedder import get_embedding
from app.vectorstore.vector_db import upsert_chunks, query_db

@pytest.fixture(autouse=True)
# NOTE : Testing enviroment after fixture does not worked, so I moved the env check to the top of the file.
# def check_env():
#     """Test that the api key is existed."""
#     from dotenv import load_dotenv
#     load_dotenv()
#     assert os.getenv("OPENAI_API_KEY") is not None, "Missing OPENAI_API_KEY"

def test_chunking_logic():
    """Test that the chunker outputs correct Pydantic models."""
    doc = Document(
        filename="test_policy.md", 
        content="This is sentence one. \n\nThis is a new paragraph."
    )
    
    chunks = process_documents([doc], chunk_size=50, overlap=10)
    
    assert len(chunks) > 0
    assert isinstance(chunks[0], Chunk)
    assert chunks[0].filename == "test_policy.md"

def test_embedder_api():
    """Test that OpenAI is returning the correct vector dimensions."""
    vector = get_embedding("Test string for embedding.")
    
    # text-embedding-3-small always returns exactly 1536 dimensions
    assert len(vector) == 1536
    assert isinstance(vector[0], float)

def test_vector_db_integration():
    """Test full flow: chunking -> embedding -> storage -> retrieval."""
    TEST_COLLECTION = "test_collection"
    
    # 1. Create a dummy chunk
    test_chunk = Chunk(
        id="test_id_1",
        filename="test_file.md",
        text="The company mascot is a blue penguin."
    )
    
    # 2. Embed it
    embedding = get_embedding(test_chunk.text)
    
    # 3. Upsert to DB
    upsert_chunks(
        collection_name=TEST_COLLECTION,
        chunks=[test_chunk],
        embeddings=[embedding]
    )
    
    # 4. Query the DB
    query_vector = get_embedding("What animal is our mascot?")
    results = query_db(
        collection_name=TEST_COLLECTION, 
        query_embedding=query_vector, 
        top_k=1
    )
    
    # 5. Assertions
    assert len(results) == 1 # suggests we got a result back
    assert results[0].id == "test_id_1" # Verify we got the correct chunk back
    assert "blue penguin" in results[0].text # Verify the content matches
    assert hasattr(results[0], 'distance') # Verify it's a RetrievedChunk