"""Interactive terminal tester for the complete helpdesk query pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import run_query_pipeline


def display_result(result: dict) -> None:
    """Print the pipeline result in a compact, readable format."""
    reasons = result["escalation_reasons"] or ["None"]
    print(f"Predicted Intent: {result['predicted_intent']}")
    print(f"Classifier Confidence: {result['classifier_confidence']:.4f}")
    print(f"Retrieved Source: {result['source_document'] or 'None'}")
    similarity = result["retrieval_similarity"]
    print(f"Retrieval Similarity: {similarity:.4f}" if similarity is not None else "Retrieval Similarity: None")
    print(f"Answer: {result['answer']}")
    print(f"Grounded: {result['grounded']}")
    print(f"Escalated: {result['escalated']}")
    print(f"Escalation Reasons: {', '.join(reasons)}")


def main() -> None:
    print("=" * 40)
    print("Multilingual Admissions Helpdesk")
    print("Type 'exit' or 'quit' to quit")
    print("=" * 40)

    while True:
        try:
            query = input("\nQuery: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            return

        if query.lower() in {"exit", "quit"}:
            print("Exiting.")
            return
        if not query:
            print("Please enter a query, or type 'exit' to quit.")
            continue

        try:
            result = run_query_pipeline(query)
            display_result(result)
        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
