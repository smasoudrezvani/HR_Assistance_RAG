# 🗺️ System Architecture & Data Flow Layer Map

This project utilizes a **Feature-Based Layered Architecture**. The codebase isolates core execution layers to ensure components can be easily swapped or refactored without breaking adjacent system modules.

## 🛠️ The Onion Layers

## 🛠️ Updated Stage 3 Hybrid Flow Layout

```text
  ┌────────────────────────────────────────────────────────┐
  │  OUTER LAYER: Presentation & Transport (FastAPI Router)│
  │  └─ app/api/rag.py                                     │
  │       ▲                                                │
  │       ▼                                                │
  │  MIDDLE LAYER: Application Service Orchestration       │
  │  └─ app/retrieval/hybrid.py                            │
  │       ├── Call: app/embeddings/embedder.py             │
  │       ├── Call: app/vectorstore/vector_db.py           │
  │       └── Call: app/retrieval/reranker.py              │
  │       ▲                                                │
  │       ▼                                                │
  │  INNER CORE: Data Contracts & Pure Generation Engines  │
  │  └─ app/db/models.py , app/rag/generator.py            │
  └────────────────────────────────────────────────────────┘

```
## The Stack
*   **API Framework:** FastAPI
*   **Vector Database (Dense):** ChromaDB (Local Persistent)
*   **Sparse Index (Keyword):** BM25Okapi (In-Memory)
*   **Embeddings:** OpenAI `text-embedding-3-small`
*   **Reranker:** Cross-Encoder (`ms-marco-MiniLM-L-6-v2`)
*   **LLM Generator:** OpenAI `gpt-4o-mini`
*   **Evaluation:** Custom LLM-as-a-Judge (`gpt-4o`)
*   **Observability:** Langfuse

## The 4-Valve Request Lifecycle
To effectively debug the system, it is mapped into four sequential "valves." If data stops flowing or becomes corrupted, the fault is isolated to one of these distinct boundaries:

1.  **The API Entry (`app/api/rag.py`):** 
    Receives the user's JSON payload, initiates tracing, and acts as the final gatekeeper (applying the confidence threshold guardrail) before returning the response.
2.  **The Retrieval Orchestrator (`app/retrieval/hybrid.py` & `reranker.py`):** 
    Executes the Hybrid Search strategy. It queries the Vector DB and BM25 index, fuses the results mathematically using Reciprocal Rank Fusion (RRF), and re-sorts the top matches using a Cross-Encoder neural network.
3.  **The Storage Engine (`app/vectorstore/vector_db.py` & `app/ingestion/chunker.py`):** 
    Handles data persistence. Documents are parsed using a recursive, Markdown-aware text splitter (1500 character limits, preserving paragraphs), embedded, and synced across ChromaDB and the BM25 index.
4.  **The Generator (`app/rag/generator.py`):** 
    Packages the high-precision retrieved chunks into a strict system prompt, forcing the LLM to synthesize an answer and append explicit `[chunk_id]` inline citations for every factual claim.

## Ingestion Flow
1. Load Markdown files from `docs/`.
2. Recursively split text by `\n\n`, `\n`, and sentences.
3. Generate UUIDs for each chunk.
4. Batch embed via OpenAI.
5. Upsert into ChromaDB and synchronize the in-memory BM25 dictionary.