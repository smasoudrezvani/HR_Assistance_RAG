You are an expert AI Engineer building a Golden Q&A Evaluation Dataset to test a new Retrieval-Augmented Generation (RAG) system. 

I am going to provide you with a set of internal company policy documents. Your task is to generate exactly 20 test questions based strictly on these documents. 

These questions must test the limits of a chunk-based vector search pipeline. You must generate a mix of standard questions and highly specific edge cases. 

Here is the required distribution of the 20 questions:

5 Standard Lookups (Easy: Single fact in a single document)

4 Multi-Hop (Hard: Requires combining facts from at least 2 different documents)

3 Negative Constraints (Hard: Asks what is NOT allowed or NOT included)

2 Temporal/Date-Bound (Medium: Requires understanding when a policy went into effect)

2 Mathematical/Aggregation (Medium: Requires counting items or calculating days/allowances)

2 Needle in a Haystack (Medium: Asks about a tiny exception buried deep in a bulleted list or footnote)

2 False Premise / Hallucination Bait (Medium: Asks about a completely fake policy to ensure the RAG system refuses to answer)

INSTRUCTIONS:

For every question (except the False Premise ones), the answer MUST be verifiable within the provided documents.

For the "expected_sources" field, you must provide the exact filenames where the answer is found.

For False Premise questions, the "expected_answer" must be a variation of: "I don't have enough information in the current documents to answer that." and the sources must be an empty list [].

OUTPUT FORMAT:
You must output ONLY a valid JSON array of objects. Do not include markdown formatting like ```json, just the raw text. Use this exact schema:

[
  {
    "id": "q1_standard_lookup",
    "question": "...",
    "expected_answer": "...",
    "expected_sources": ["filename.md"],
    "difficulty": "easy",
    "edge_case_type": null
  },
  // ... 19 more
]