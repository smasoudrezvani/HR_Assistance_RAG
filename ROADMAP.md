# 🗺️ AI Engineering RAG Project Roadmap

## Stage 1: Baseline (Naive RAG) - ✅ COMPLETED
- [x] Load markdown files from a local directory.
- [x] Chunk text using standard Python.
- [x] Embed with OpenAI `text-embedding-3-small`.
- [x] Store in ChromaDB (local persistent client).
- [x] Retrieve top-K chunks by cosine similarity.
- [x] Pass to GPT-4o-mini with a grounded-answer prompt.
- [x] Abstracted into a modular architecture (`app/` directory).
- [x] Wrapped in a FastAPI web server.

## Stage 2: Evaluation & Observability - ✅ COMPLETED
- [x] Write 22 hand-crafted test questions representing real-world failure modes.
- [x] Format test cases as JSON (Golden Q&A Dataset).
- [x] Add Langfuse tracing to the FastAPI application.
- [x] Build an LLM-as-a-judge evaluator using `gpt-4o`.
- [x] Run baseline RAG against the golden set to establish a baseline scorecard.
  * **Baseline Scorecard (May 2026):**
    * **Average Answer Correctness:** `0.56 / 1.00`
    * **Average Answer Faithfulness:** `1.00 / 1.00`

## Stage 3: Hybrid Search & Reranking - ✅ COMPLETED
- [x] Implemented BM25 sparse retrieval.
- [x] Implemented Reciprocal Rank Fusion (RRF) math.
- [x] Integrated `ms-marco-MiniLM` Cross-Encoder reranker.
- [x] Synchronized database memory indexes on application lifecycles.
  * **Stage 3 Scorecard (Hybrid + Rerank):**
    * **Average Answer Correctness:** `0.47 / 1.00` (Dropped due to tight context compression)
    * **Average Answer Faithfulness:** `1.00 / 1.00`

## Stage 4: Advanced RAG Features - 🔄 IN PROGRESS
- [ ] Increase generation prompt window target (`top_k=5` post-rerank context allowance).
- [ ] Implement structure-aware recursive chunking (split on headers/paragraphs instead of fixed-size blocks).
- [ ] Add strict inline citations `[chunk_id]` to the LLM response window.
- [ ] Build an LLM-as-a-judge citation verification engine.

## Stage 5: Multi-Agent RAG (LangGraph) - ⏳ PLANNED
- [ ] Introduce LangGraph for state-machine orchestration.
- [ ] Build a Router Agent to decompose multi-hop questions.
- [ ] Implement Specialist Retrievers and a Synthesis Agent.

## Stage 6: Production & Deployment - ⏳ PLANNED
- [ ] Containerize with Docker (`Dockerfile` + `docker-compose.yml`).
- [ ] Add streaming token responses via FastAPI `StreamingResponse`.
- [ ] Build a simple Streamlit frontend interface.