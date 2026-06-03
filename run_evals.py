import os
import json
import httpx
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Data contracts for evaluation
OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
API_URL = "http://127.0.0.1:8000/api/v1/query"

def load_golden_dataset(filepath: str = "tests/eval_dataset.json") -> list:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def query_rag_system(question: str) -> dict:
    """Hits our running FastAPI instance to get the RAG response."""
    try:
        response = httpx.post(API_URL, json={"question": question}, timeout=30.0)
        if response.status_code == 200:
            return response.json()
        return {"answer": f"Error: API returned status {response.status_code}", "sources": []}
    except Exception as e:
        return {"answer": f"Error connecting to API: {str(e)}", "sources": []}

def judge_answer(question: str, expected_answer: str, actual_answer: str) -> dict:
    """LLM-as-a-judge prompt to evaluate accuracy and faithfulness."""
    system_prompt = (
        "You are an impartial, strict quality assurance judge evaluating an HR RAG assistant. "
        "Your task is to compare the 'Actual Answer' against the 'Expected Ground Truth Answer'.\n\n"
        "Grade the response on two parameters:\n"
        "1. Correctness: Does the actual answer accurately capture the core factual information of the expected answer? (0.0 to 1.0)\n"
        "2. Faithfulness: Does the actual answer avoid hallucinating unmentioned facts or over-promising? (0.0 to 1.0)\n\n"
        "Respond ONLY with a valid JSON object containing the keys: 'correctness', 'faithfulness', and 'reasoning'."
    )
    
    user_content = f"""
    Question asked: {question}
    Expected Ground Truth Answer: {expected_answer}
    Actual RAG System Answer: {actual_answer}
    """
    
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o",  # We use a heavier model to act as a reliable judge
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"correctness": 0.0, "faithfulness": 0.0, "reasoning": f"Judge failed: {str(e)}"}

def main():
    print("🚀 Starting RAG Baseline Evaluation...")
    dataset = load_golden_dataset()
    
    total_correctness = 0.0
    total_faithfulness = 0.0
    results = []

    for idx, case in enumerate(dataset, 1):
        print(f"\n[{idx}/{len(dataset)}] Testing: {case['question']}")
        
        # 1. Get RAG Response
        rag_output = query_rag_system(case["question"])
        actual_answer = rag_output.get("answer", "")
        
        # 2. Judge Response
        evaluation = judge_answer(case["question"], case["expected_answer"], actual_answer)
        
        total_correctness += evaluation["correctness"]
        total_faithfulness += evaluation["faithfulness"]
        
        print(f"   | Score -> Correctness: {evaluation['correctness']} | Faithfulness: {evaluation['faithfulness']}")
        print(f"   | Reason: {evaluation['reasoning']}")
        
        results.append({
            "id": case["id"],
            "question": case["question"],
            "actual_answer": actual_answer,
            "scores": evaluation
        })

    # Calculate final averages
    count = len(dataset)
    avg_correctness = total_correctness / count
    avg_faithfulness = total_faithfulness / count

    print("\n" + "="*40)
    print("📊 FINAL BASELINE SCORECARD")
    print("="*40)
    print(f"Average Answer Correctness: {avg_correctness:.2f}")
    print(f"Average Answer Faithfulness: {avg_faithfulness:.2f}")
    print("="*40)

    # --- 🛑 THE CI/CD GATEKEEPER ---
    # If the system drops below 60% correctness or 95% faithfulness, fail the build!
    if avg_correctness < 0.60 or avg_faithfulness < 0.95:
        print("\n❌ CI/CD ALERT: Evaluation scores fell below acceptable production thresholds.")
        sys.exit(1) # This tells GitHub Actions to highlight the pipeline in RED
    else:
        print("\n✅ CI/CD SUCCESS: Evaluation passed production thresholds.")
        sys.exit(0) # This tells GitHub Actions it passed (GREEN)

if __name__ == "__main__":
    main()