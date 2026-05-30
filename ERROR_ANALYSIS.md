# 📊 Baseline Error Analysis Matrix (stage 2)

* **Current Score:** Correctness: `0.56` | Faithfulness: `1.00`
* **Analysis Date:** May 2026
* **Judge Engine:** `gpt-4o`

---

## 🔍 Failure Modes & Triage Log

### 1. The Keyword Dilution Failure
* **Example Case:** *"What is the name of the company?"* (Scored `0.0` Correctness)
* **Root Cause:** The word "Talk360" appears continuously across all documents as structural boilerplate. Because it is everywhere, the dense embedding model dilutes its semantic value. The query searches for the *concept* of naming an entity, rather than matching on the specific keyword.
* **Stage 3 Remediation Strategy:** **BM25 Sparse Retrieval**. Keyword frequency matching will instantly catch instances where explicit terms appear, matching the exact name regardless of surrounding semantic abstractions.

### 2. The Partial Summarization Failure
* **Example Cases:** Referral conditions (`q2`), Resignation protocols (`q5`), L&D formulas (`q9`), Board approvals (`q18`) (Scored `0.5` Correctness)
* **Root Cause:** ChromaDB successfully fetched the correct text blocks. However, the generator engine (`gpt-4o-mini`) parsed only the primary sentence and omitted secondary restrictions or conditions (e.g., matching the budget amount but failing to mention that unused budget does not roll over).
* **Stage 4 Remediation Strategy:** **Prompt Optimization**. We will adjust the generation prompt framework to force explicit, structured extraction of all boundary conditions and sub-clauses.

### 3. Complete Retrieval Drop (Semantic Mismatch)
* **Example Cases:** Vacation allowances (`q3`), Fireflies interface variables (`q6`) (Scored `0.0` Correctness)
* **Root Cause:** The query string used terms that did not cleanly align with the exact phrasing inside the underlying text chunks. The vector database prioritized generic HR paragraphs over the highly specific target clauses.
* **Stage 3 Remediation Strategy:** **Cross-Encoder Reranking**. We will increase our baseline vector retrieval pull size (from Top-3 to Top-15) to maximize recall, then use a Cross-Encoder model to analyze text interactions directly and bubble the perfect context match to the top.

---

## 🧪 Adversarial Experiments Summary

### The `Lies.md` and `Not_lies.md` Paradox (`q21` & `q22`)
* **Objective:** Test if explicit warning headers prevent an LLM from consuming untrusted context data.
* **Observed Baseline Behavior:** The system scored `0.0` on Correctness but maintained a perfect `1.0` on Faithfulness. The model successfully printed a refusal string ("I don't have enough information") instead of blindly mimicking the absurd claims in `Lies.md`.
* **Action Item:** During Stage 3, we will monitor how the introduction of BM25 and Rerankers impacts this balance. We must ensure that higher keyword matching does not trick the generator into bypassing system prompt safety notices.

# 📊 Hybrid Search & Reranking Error Matrix (stage 3)

---

## 🔍 Triage Log & Remediation Actions

### 1. Incomplete Metric Aggregations (Scores: 0.0 - 0.5)
* **Example Case:** Vacation Days (`q3`), Leadership metrics (`q15`), L&D updates (`q18`)
* **Root Cause Analysis:** To execute these evaluations correctly, the LLM needs a broad window of structural records spread out across multiple sections. By compressing the final Cross-Encoder payload down to `top_k=3`, we isolated individual clauses while completely cutting off adjacent sub-paragraphs containing the secondary metrics.
* **Stage 4 Corrective Action:** Expand the target contextual window returned by `advanced_retrieval` from 3 to 5 chunks, ensuring multi-hop questions have access to the full breadth of data retrieved.

### 2. Semantic Misalignment / False Entity Extraction
* **Example Case:** Customer Support blockers (`q7`) - RAG returned 'Jill' instead of 'Mahmoud'.
* **Root Cause Analysis:** Fixed-size chunking broke sentences in half at arbitrary limits. The cross-encoder saw an isolated phrase matching support management structural context and mistakenly paired a nearby name with the blocker statement.
* **Stage 4 Corrective Action:** **Recursive Structure-Aware Chunking**. We will scrap fixed-size slicing and rebuild the processing engine to respect Markdown block headers and physical paragraphs. This guarantees that names, roles, and conditions stay logically grouped together within the same chunk container.