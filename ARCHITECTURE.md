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

🔄 End-to-End Hybrid Pipeline Trace Loop
1. User Request: Client posts a message to /api/v1/query.

2. Orchestration Branch (app/retrieval/hybrid.py):

- Dense Fetch: Query text converts to a float vector and pulls the Top 15 chunks from ChromaDB.

- Sparse Fetch: Query text hits the raw keyword token indices to pull the Top 15 chunks via BM25.

- RRF Consolidation: Both arrays merge mathematically based entirely on structural position rank.

- Reranker Compression: The local Cross-Encoder analyzes the 30 candidate blocks simultaneously, sorting and squeezing them down to the final Top 3 chunks.

3. Generation Stage: app/rag/generator.py processes the 3 chunks and outputs the grounded text response back to the client router.