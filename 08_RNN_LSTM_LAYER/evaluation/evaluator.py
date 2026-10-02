"""Phase 9: Evaluation for Conversational Memory Layer.

Evaluates:
- Slot retention accuracy (e.g. keeping course across follow-ups)
- Contextual query resolution correctness
"""

import json
from pathlib import Path
from ..dataset.schema import SAMPLE_DIALOGUES
from ..memory import ConversationMemoryManager

BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_DIR = BASE_DIR / "evaluation"


def evaluate_conversation_memory() -> dict:
    """Evaluate multi-turn context retention on benchmark dialogues."""
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    manager = ConversationMemoryManager()

    total_turns = 0
    correct_course_slots = 0
    correct_intent_slots = 0

    for dlg in SAMPLE_DIALOGUES:
        session_id = f"eval_{dlg['dialogue_id']}"
        manager.clear_session(session_id)

        for turn in dlg["turns"]:
            total_turns += 1
            # In turn 1 course is explicit, in turn 2+ it might be omitted
            extracted_course = turn["course"] if turn["turn_id"] == 1 else None
            res = manager.update_and_resolve_query(
                session_id=session_id,
                current_query=turn["user_utterance"],
                extracted_course=extracted_course,
                extracted_intents=turn["intents"],
            )

            if res["active_course"] == turn["course"]:
                correct_course_slots += 1

            if set(res["intents"]) == set(turn["intents"]):
                correct_intent_slots += 1

    metrics = {
        "total_eval_turns": total_turns,
        "course_slot_retention_accuracy": round(correct_course_slots / max(total_turns, 1), 4),
        "intent_slot_accuracy": round(correct_intent_slots / max(total_turns, 1), 4),
    }

    with open(EVAL_DIR / "memory_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == "__main__":
    m = evaluate_conversation_memory()
    print("RNN/LSTM Memory Metrics:", m)
