import re
import uuid
from app.db.models import Chunk

def split_by_separators(text: str, separators: list[str], max_length: int) -> list[str]:
    """Recursively splits text using a prioritized list of regex separators."""
    if not separators:
        # Fallback: strict character split if no separators are left
        return [text[i:i+max_length] for i in range(0, len(text), max_length)]
    
    sep = separators[0]
    splits = re.split(sep, text)
    good_splits = []
    for s in splits:
        if len(s) <= max_length:
            good_splits.append(s)
        else:
            # If the chunk is STILL too big, recursively try the next smaller separator
            good_splits.extend(split_by_separators(s, separators[1:], max_length))

    return good_splits
    
def process_documents(docs: list[dict], chunk_size : int = 800, overlap: int = 100) -> list[Chunk]:
    """
    Creates structure-aware chunks. 
    Assumes 'docs' is a list of dicts: [{"filename": "...", "text": "..."}]
    """
    # 1. Paragraphs, 2. Single Newlines, 3. Sentences
    separators = [r'\n\n+', r'\n', r'(?<=\.)\s+']

    final_chunks = []

    for doc in docs:
        filename = doc.filename
        raw_text = doc.content

        # Get natural splits based on Markdown structure
        raw_splits = split_by_separators(raw_text, separators, chunk_size)

        current_text = ""

        for split in raw_splits:
            if not split.strip():
                continue
                
            # If adding the next split fits inside our chunk window, append it
            if len(current_text) + len(split) + 1 <= chunk_size:
                current_text += split + " "
            else:
                # Window is full. Save the chunk.
                if current_text:
                    final_chunks.append(Chunk(
                        id=uuid.uuid4().hex, 
                        filename=filename, 
                        text=current_text.strip()
                    ))
                    
                # Setup the next chunk, preserving an overlap from the end of the previous chunk
                overlap_text = current_text[-overlap:] if overlap > 0 and len(current_text) > overlap else ""
                current_text = overlap_text + split + " "
        
        # Catch the final lingering chunk
        if current_text.strip():
            final_chunks.append(Chunk(
                id=uuid.uuid4().hex, 
                filename=filename, 
                text=current_text.strip()
            ))
            
    return final_chunks
