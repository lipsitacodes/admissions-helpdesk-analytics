"""Phase 13: Answer Correctness & Groundedness Evaluation."""

import importlib
from typing import Dict, Any, List

_orchestrator = importlib.import_module("09_QUERY_ORCHESTRATION.orchestrator")
_answerer = importlib.import_module("10_ANSWER_LAYER.answerer")

BENCHMARK_ANSWERS = [
    {
        "query": "BSc Agriculture fee structure",
        "expected_substring": "1,50,000",
    },
    {
        "query": "BTech Computer Science Bhubaneswar fee",
        "expected_substring": "1,85,000",
    },
    {
        "query": "Who are you?",
        "expected_substring": "Centurion",
    },
]


def run_answer_eval() -> Dict[str, Any]:
    correct = 0
    grounded_count = 0
    total = len(BENCHMARK_ANSWERS)

    for item in BENCHMARK_ANSWERS:
        q = item["query"]
        q_data = _orchestrator.orchestrate_query(q, session_id="eval_ans")
        ans_data = _answerer.produce_final_answer(q_data)

        if item["expected_substring"].lower() in ans_data["answer"].lower():
            correct += 1
        if ans_data["is_grounded"]:
            grounded_count += 1

    return {
        "total_queries_tested": total,
        "answer_correctness_accuracy": round(correct / max(total, 1), 4),
        "groundedness_rate": round(grounded_count / max(total, 1), 4),
    }


if __name__ == "__main__":
    print(run_answer_eval())
