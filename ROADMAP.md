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

## Stage 4: Advanced RAG Features - ✅ COMPLETED
- [ ] Increase generation prompt window target (`top_k=5` post-rerank context allowance).
- [ ] Implement structure-aware recursive chunking (split on headers/paragraphs instead of fixed-size blocks).
- [ ] Add strict inline citations `[chunk_id]` to the LLM response window.
- [ ] Build an LLM-as-a-judge citation verification engine.
  * **Stage 4 Scorecard:**
    * **Average Answer Correctness:** `0.64 / 1.00`
    * **Average Answer Faithfulness:** `0.98 / 1.00`

## Stage 5: Production LLMOps Hardening - ⏳ PLANNED
- [ ] Semantic Caching: Store previous answers to save latency and API costs.
- [ ] Guardrails: Add input validation (block prompt injection) and output validation.
- [ ] ICI/CD Pipeline: Automate your run_evals.py script to run on GitHub Actions.

## Stage 6: Multi-Agent RAG - ⏳ PLANNED
- [ ] LangGraph Orchestration: Upgrade from a linear FastAPI route to a state-machine.
- [ ] Router Agent: Build an LLM node that decides if a question needs HR policies, external web search, or a direct rejection.

## Stage 7: Production & Deployment - ⏳ PLANNED
- [ ] Streaming Responses: Upgrade the API to stream tokens back to the user like ChatGPT.
- [ ] Streamlit Frontend: Build a clean chat UI that consumes your FastAPI backend.
- [ ] Docker Containerization: Write a Dockerfile and docker-compose.yml to package the UI, API, and ChromaDB together for 1-click deployment.