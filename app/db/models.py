from pydantic import BaseModel, Field

class Document(BaseModel):
    """Represents a raw loaded document."""
    filename : str
    content : str

class Chunk(BaseModel):
    """Represents a processed chunk of text ready for embedding."""
    id : str
    filename : str
    text : str

class RetrievedChunk(Chunk):
    """Represents a chunk retrieved from the vector database."""
    distance : float = Field(..., description="Distance metric from ChromaDB")

class QueryRequest(BaseModel):
    """The JSON payload a client sends to our API."""
    question : str = Field(..., description="The user's question to the RAG system")

class SourceItem(BaseModel):
    filename: str
    url: str | None = None

class QueryResponse(BaseModel):
    answer: str
    # Update this line to return objects instead of strings
    sources: list[SourceItem] = Field(default_factory=list)



