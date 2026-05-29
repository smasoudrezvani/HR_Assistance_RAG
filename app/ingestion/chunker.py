import re
from app.db.models import Document, Chunk

def smart_chunker(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Splits text by semantic boundaries (paragraphs, sentences) and packs them."""
    splits = re.split(r'(\n\n|\n|\. )', text)

    blocks = []
    for i in range(0, len(splits) - 1, 2):
        blocks.append(splits[i] + splits[i+1])
    if len(splits) % 2 != 0:
        blocks.append(splits[-1])

    blocks = [b for b in blocks if b.strip()]

    chunks = []
    current_chunk = ""

    for block in blocks:
        if len(current_chunk) + len(block) <= chunk_size:
            current_chunk += block
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            overlap_text = current_chunk[-overlap:] if current_chunk else ""
            clean_start = overlap_text.find(" ")
            if clean_start != -1:
                overlap_text = overlap_text[clean_start:]
                
            current_chunk = overlap_text + block

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def process_documents(documents: list[Document], chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """Takes a list of Documents and returns a list of Pydantic Chunk objects."""
    all_chunks = []
    
    for doc in documents:
        raw_chunks = smart_chunker(doc.content, chunk_size, overlap)
        for i, text_chunk in enumerate(raw_chunks):
            chunk = Chunk(
                id=f"{doc.filename}_smart_{i}",
                filename=doc.filename,
                text=text_chunk
            )
            all_chunks.append(chunk)
            
    return all_chunks