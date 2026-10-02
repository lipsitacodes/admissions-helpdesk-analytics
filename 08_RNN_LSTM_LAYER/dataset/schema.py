"""Phase 9: RNN/LSTM Conversational Context Dataset.

Contains multi-turn dialogue episodes demonstrating conversational state tracking:
Turn 1: Explicit course reference (e.g., 'BSc Agriculture ka fees kya hai?')
Turn 2+: Elliptical follow-ups requiring memory context (e.g., 'Aur hostel?', 'Faculty kaun hai?', 'Rayagada campus me?')
"""

from typing import Any, Dict, List

SAMPLE_DIALOGUES = [
    {
        "dialogue_id": "D001",
        "turns": [
            {
                "turn_id": 1,
                "user_utterance": "BSc Agriculture ka fees kya hai?",
                "course": "B Sc Hons Agriculture",
                "campus": "Paralakhemundi",
                "intents": ["fees"],
                "resolved_query": "B Sc Hons Agriculture fees",
            },
            {
                "turn_id": 2,
                "user_utterance": "Aur hostel?",
                "course": "B Sc Hons Agriculture",
                "campus": "Paralakhemundi",
                "intents": ["hostel"],
                "resolved_query": "B Sc Hons Agriculture hostel information",
            },
            {
                "turn_id": 3,
                "user_utterance": "Faculty kaun hai?",
                "course": "B Sc Hons Agriculture",
                "campus": "Paralakhemundi",
                "intents": ["faculty"],
                "resolved_query": "B Sc Hons Agriculture faculty details",
            },
        ],
    },
    {
        "dialogue_id": "D002",
        "turns": [
            {
                "turn_id": 1,
                "user_utterance": "What is the fee for BTech CSE?",
                "course": "Bachelor Of Technology In Computer Science And Engineering",
                "campus": None,
                "intents": ["fees"],
                "resolved_query": "Bachelor Of Technology In Computer Science And Engineering fees",
            },
            {
                "turn_id": 2,
                "user_utterance": "Bhubaneswar campus me?",
                "course": "Bachelor Of Technology In Computer Science And Engineering",
                "campus": "Bhubaneswar",
                "intents": ["fees"],
                "resolved_query": "Bachelor Of Technology In Computer Science And Engineering Bhubaneswar fees",
            },
            {
                "turn_id": 3,
                "user_utterance": "Aur eligibility?",
                "course": "Bachelor Of Technology In Computer Science And Engineering",
                "campus": "Bhubaneswar",
                "intents": ["eligibility"],
                "resolved_query": "Bachelor Of Technology In Computer Science And Engineering eligibility criteria",
            },
        ],
    },
]
