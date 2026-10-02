"""Phase 13: Escalation Decision Appropriateness Evaluation."""

import importlib
from typing import Dict, Any

_orchestrator = importlib.import_module("09_QUERY_ORCHESTRATION.orchestrator")
_answerer = importlib.import_module("10_ANSWER_LAYER.answerer")
_escalator = importlib.import_module("11_ESCALATION_LAYER.escalator")

ESCALATION_BENCHMARKS = [
    {
        "query": "I want to file a police complaint about ragging in hostel",
        "expected_decision": "ESCALATION",
    },
    {
        "query": "Who is winning the cricket world cup?",
        "expected_decision": "ESCALATION",
    },
    {
        "query": "What is the fee for BSc Agriculture?",
        "expected_decision": "ANSWER",
    },
]


def run_escalation_eval() -> Dict[str, Any]:
    correct = 0
    total = len(ESCALATION_BENCHMARKS)

    for item in ESCALATION_BENCHMARKS:
        q = item["query"]
        q_data = _orchestrator.orchestrate_query(q, session_id="eval_esc")
        ans_data = _answerer.produce_final_answer(q_data)
        esc_data = _escalator.process_confidence_and_escalation(q_data, ans_data)

        if esc_data["decision"] == item["expected_decision"]:
            correct += 1

    return {
        "total_queries_tested": total,
        "escalation_appropriateness_accuracy": round(correct / max(total, 1), 4),
    }


if __name__ == "__main__":
    print(run_escalation_eval())
