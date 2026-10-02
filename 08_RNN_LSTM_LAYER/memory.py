"""Phase 9: Conversation Memory Manager Interface.

Unifies RNN and LSTM state tracking to manage multi-turn dialogues.
Resolves contextual / elliptical queries:
Turn 1: 'BSc Agriculture ka fees kya hai?' -> stores course 'B Sc Hons Agriculture'
Turn 2: 'Aur hostel?' -> resolves to 'B Sc Hons Agriculture hostel information'
"""

import re
from typing import Any, Dict, List, Optional
import torch

from .rnn.sequential_context_rnn import SequentialContextRNN
from .lstm.conversation_memory_lstm import ConversationMemoryLSTM
from .preprocessing.sequence_tokenizer import DialogueSequenceTokenizer


class ConversationMemoryManager:
    """Maintains multi-turn conversational slots across turns in a session."""

    def __init__(self):
        self.tokenizer = DialogueSequenceTokenizer(vocab_size=1000, max_seq_len=20)
        self.rnn = SequentialContextRNN(vocab_size=1000, embed_dim=64, hidden_dim=64)
        self.lstm = ConversationMemoryLSTM(vocab_size=1000, embed_dim=64, hidden_dim=128)

        # In-memory session store: session_id -> slot state
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "active_course": None,
                "active_academic_category": None,
                "active_campus": None,
                "previous_intents": [],
                "turn_history": [],
                "lstm_state": None,
            }
        return self._sessions[session_id]

    def update_and_resolve_query(
        self,
        session_id: str,
        current_query: str,
        extracted_course: Optional[str] = None,
        extracted_category: Optional[str] = None,
        extracted_campuses: Optional[List[str]] = None,
        extracted_intents: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update conversational state and resolve elliptical references."""
        session = self.get_or_create_session(session_id)
        extracted_campuses = extracted_campuses or []
        extracted_intents = extracted_intents or []

        # Check if query is an elliptical follow-up
        FOLLOW_UP_INDICATORS = {
            "aur", "and", "iski", "iska", "iskaa", "uske", "uska", "its", "it", "this",
            "what about", "how about", "same", "also", "bhi"
        }
        query_words = set(current_query.lower().split())
        has_follow_up_word = bool(query_words & FOLLOW_UP_INDICATORS) or any(
            phrase in current_query.lower() for phrase in ["what about", "how about", "aur batao", "iska fees", "iski fees"]
        )
        is_general_topic = (
            any(i in (extracted_intents or []) for i in ("scholarship", "campus_info"))
            or bool(re.search(r"\b(courses?|campuses?|scholarships?|hostels?)\b", current_query.lower()))
        )
        is_short_attribute_query = (
            not is_general_topic
            and len(query_words) <= 4
            and any(intent in (extracted_intents or []) for intent in ["fees", "cutoff", "placement"])
        )

        is_follow_up = False
        resolved_course = extracted_course
        resolved_campus = extracted_campuses[0] if extracted_campuses else None

        if not extracted_course and session["active_course"] and (has_follow_up_word or is_short_attribute_query):
            # User explicitly asked a contextual follow-up to active course
            resolved_course = session["active_course"]
            is_follow_up = True
        elif extracted_course:
            # User explicitly mentioned a course -> updates active slot
            session["active_course"] = extracted_course
            session["active_academic_category"] = extracted_category

        if not resolved_campus and session["active_campus"]:
            resolved_campus = session["active_campus"]
        elif extracted_campuses:
            session["active_campus"] = extracted_campuses[0]

        # Formulate resolved query for downstream RAG retrieval
        if is_follow_up and resolved_course:
            intents_str = " ".join(extracted_intents) if extracted_intents else "information"
            campus_str = f" {resolved_campus}" if resolved_campus else ""
            resolved_query = f"{resolved_course}{campus_str} {intents_str}".strip()
        else:
            resolved_query = current_query

        # Record turn
        session["previous_intents"] = extracted_intents
        session["turn_history"].append({
            "utterance": current_query,
            "resolved_query": resolved_query,
            "course": resolved_course,
            "intents": extracted_intents,
        })

        return {
            "is_follow_up": is_follow_up,
            "resolved_query": resolved_query,
            "active_course": resolved_course,
            "active_academic_category": session["active_academic_category"],
            "active_campus": resolved_campus,
            "intents": extracted_intents,
        }

    def clear_session(self, session_id: str):
        """Reset conversation session."""
        if session_id in self._sessions:
            del self._sessions[session_id]


_memory_instance = ConversationMemoryManager()


def resolve_conversational_context(
    session_id: str,
    query: str,
    course: Optional[str] = None,
    category: Optional[str] = None,
    campuses: Optional[List[str]] = None,
    intents: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Top-level helper to maintain state and resolve queries."""
    return _memory_instance.update_and_resolve_query(
        session_id=session_id,
        current_query=query,
        extracted_course=course,
        extracted_category=category,
        extracted_campuses=campuses,
        extracted_intents=intents,
    )
