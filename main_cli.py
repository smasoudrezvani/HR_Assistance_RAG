import os
from dotenv import load_dotenv

load_dotenv()
if not os.environ.get("OPENAI_API_KEY"):
    raise ValueError("Missing OPENAI_API_KEY in environment!")

from app.ingestion.loader import load_documents
from app.ingestion.chunker import process_documents
from app.embeddings.embedder import get_embeddings_batch, get_embedding
from app.vectorstore.vector_db import upsert_chunks, query_db
from app.vectorstore.vector_db import chroma_client
from app.rag.generator import generate_grounded_answer

COLLECTION_NAME = "hr_policies_prod"

def setup_database():
    """Checks if data exists. If not, runs the ingestion pipeline."""
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    if collection.count() > 0:
        print(f"[*] Database ready: {collection.count()} chunks found. Skipping ingestion.")
        return
    
    print("[*] Empty database detected. Starting ingestion pipeline...")

    # 1. Load
    docs = load_documents("docs")
    if not docs:
        print("[!] No markdown files found in the 'docs/' folder. Please add some!")
        exit(1)
    print(f"[*] Loaded {len(docs)} documents.")

    # 2. Chunk
    chunks = process_documents(docs, chunk_size=500, overlap=50)
    print(f"[*] Created {len(chunks)} smart chunks.")

    # 3. Embed
    print("[*] Generating embeddings via OpenAI (this takes a moment)...")
    texts = [chunk.text for chunk in chunks]
    embeddings = get_embeddings_batch(texts)

    # 4. Store
    upsert_chunks(COLLECTION_NAME, chunks, embeddings)
    print("[*] Ingestion complete!\n")


def main():
    print("============================================")
    print("      🏢 Comapny CLI Policy Assistant       ")
    print("============================================")

    setup_database()

    print("\nType 'exit' or 'quit' to stop.")

    while True:
        try:
            query = input("\n🧑‍💻 You: ").strip()
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\nGoodbye!")
            break
            
        if query.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        
        if not query:
            continue

        # --- THE RAG PIPELINE ---

        # 1. Embed Query
        query_vector = get_embedding(query)

        # 2. Retrieve
        top_chunks = query_db(COLLECTION_NAME, query_vector, top_k=3)

        if not top_chunks:
            print("🤖 Assistant: No relevant context found.")
            continue

        # 3. Generate
        answer = generate_grounded_answer(query, top_chunks)

        # 4. Print Results
        print(f"\n🤖 Assistant: {answer}")
        
        print("\n--- Retrieved Context Used ---")
        for i, chunk in enumerate(top_chunks, 1):
            print(f"{i}. [Distance: {chunk.distance:.4f}] {chunk.filename}")
        print("------------------------------")


if __name__ == "__main__":
    main()