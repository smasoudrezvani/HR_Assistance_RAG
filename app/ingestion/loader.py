import os
import glob
from app.db.models import Document

def load_documents(directory_path : str) -> list[Document]:
    """Reads all markdown files in a directory and returns a list of Document models."""
    documents = []
    file_paths = glob.glob(f"{directory_path}/*.md")

    for file_path in file_paths:
        with open(file_path, 'r', encoding = 'utf-8') as file:
            content = file.read()
            # Instantiate our Pydantic model
            doc = Document(
                filename=os.path.basename(file_path),
                content=content
            )
            documents.append(doc)
    
    return documents
