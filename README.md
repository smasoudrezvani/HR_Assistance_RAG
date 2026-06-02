# 🏢 Company HR Policy Assistant (RAG Pipeline)

This project is a production-grade Retrieval-Augmented Generation (RAG) system built from scratch in Python. It currently serves as a FastAPI backend, utilizing semantic chunking, OpenAI embeddings, and a local ChromaDB vector store.

## 🗺️ Codebase Map

### Root Directory
* **`main.py`**: The entry point. It orchestrates the database setup and runs the FastAPI web server via Uvicorn.
* **`ROADMAP.md`**: Tracks project progress and upcoming architectural stages.
* **`.env`**: (Git-ignored) Stores the `OPENAI_API_KEY`.
* **`requirements.txt`**: List of dependencies for the `uv` environment.

### `app/` (Core Application Logic)
* **`api/`** *(Network Layer)*
  * `rag.py`: Contains the FastAPI routes (e.g., `POST /api/v1/query`) that expose the RAG engine to external clients.

* **`db/`** *(Data Contracts)*
  * `models.py`: Uses Pydantic to strictly define internal data (`Document`, `Chunk`, `RetrievedChunk`) and external network payloads (`QueryRequest`, `QueryResponse`).

* **`ingestion/`** *(Data Processing)*
  * `loader.py`: Reads raw `.md` files from the `docs/` folder.
  * `chunker.py`: The "Smart Semantic Chunker." Uses regex to split text safely at paragraph and sentence boundaries.

* **`embeddings/`** *(Math & Vectors)*
  * `embedder.py`: Talks to OpenAI's `text-embedding-3-small` API to convert text chunks into 1536-dimensional vectors.

* **`vectorstore/`** *(Database Operations)*
  * `vector_db.py`: The isolated ChromaDB client. Handles saving (`upsert_chunks`) and searching (`query_db`) the vector graph.

* **`rag/`** *(LLM Interaction)*
  * `generator.py`: Constructs the grounded system prompt and interacts with `gpt-4o-mini` to generate cited answers.

### Other Folders
* **`docs/`**: The raw Markdown files (HR policies) that the system reads from.
* **`tests/`**: Contains `test_core.py` to automatically verify data models and DB connections using `pytest`.