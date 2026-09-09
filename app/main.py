"""Flask integration layer for the bilingual classifier and grounded RAG flow."""

from __future__ import annotations

import logging
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import joblib
from flask import Flask, jsonify, render_template, request

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.logger import log_interaction
from database import get_database
from preprocessing.clean_text import clean_text
from rag.escalation import should_escalate
from rag.generate_answer import UNAVAILABLE_MESSAGE, compose_answer
from rag.retrieve import retrieve

logger = logging.getLogger(__name__)
MODEL_PATH = ROOT_DIR / "models" / "intent_classifier_bilingual_v2.joblib"
VECTORIZER_PATH = ROOT_DIR / "models" / "tfidf_vectorizer_bilingual_v2.joblib"


@lru_cache(maxsize=1)
def get_classifier_artifacts():
    """Load the approved bilingual v2 artifacts once per application process."""
    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        raise FileNotFoundError("The bilingual v2 classifier artifacts are unavailable.")
    return joblib.load(MODEL_PATH), joblib.load(VECTORIZER_PATH)


def _public_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Expose retrieval evidence, without vector-store implementation details."""
    return [
        {
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "similarity_score": round(float(chunk["similarity_score"]), 4),
        }
        for chunk in chunks
    ]


def run_query_pipeline(query: str) -> Dict[str, Any]:
    """Run query classification, routed retrieval, grounded answer, and escalation."""
    cleaned_query = clean_text(query)
    if not cleaned_query:
        raise ValueError("Query must not be empty.")

    model, vectorizer = get_classifier_artifacts()
    query_vector = vectorizer.transform([cleaned_query])
    predicted_intent = model.predict(query_vector)[0]
    classifier_confidence = float(model.predict_proba(query_vector)[0].max())

    retrieval_failure = False
    try:
        retrieved_chunks = retrieve(cleaned_query, predicted_intent)
    except Exception:
        retrieval_failure = True
        retrieved_chunks = []

    answer_result = compose_answer(query, predicted_intent, retrieved_chunks)
    escalation = should_escalate(
        classifier_confidence,
        retrieved_chunks,
        predicted_intent,
    )
    escalation_reasons = [escalation["reason"]] if escalation["reason"] else []
    if retrieval_failure:
        escalation["escalate"] = True
        escalation_reasons.insert(0, "retrieval_failure")

    source_document = retrieved_chunks[0]["source"] if retrieved_chunks else None
    retrieval_similarity = (
        round(float(retrieved_chunks[0]["similarity_score"]), 4)
        if retrieved_chunks
        else None
    )
    if retrieval_failure:
        answer_result = {
            "answer": UNAVAILABLE_MESSAGE,
            "source": None,
            "grounded": False,
        }

    response = {
        "query": query,
        "cleaned_query": cleaned_query,
        "predicted_intent": predicted_intent,
        "classifier_confidence": round(classifier_confidence, 4),
        "source_document": source_document,
        "retrieved_chunks": _public_chunks(retrieved_chunks),
        "retrieval_similarity": retrieval_similarity,
        "answer": answer_result["answer"],
        "grounded": answer_result["grounded"],
        "escalated": escalation["escalate"],
        "escalation_reasons": escalation_reasons,
    }

    try:
        log_interaction(
            query=query,
            cleaned_query=cleaned_query,
            predicted_intent=predicted_intent,
            classifier_confidence=classifier_confidence,
            source_document=source_document,
            retrieval_similarity=retrieval_similarity,
            escalated=response["escalated"],
            escalation_reason=",".join(escalation_reasons) or None,
            answer=response["answer"],
            grounded=response["grounded"],
            response_metadata={
                "source_document": source_document,
                "retrieved_chunks": response["retrieved_chunks"],
                "retrieval_similarity": retrieval_similarity,
                "classifier_confidence": response["classifier_confidence"],
                "escalated": response["escalated"],
                "escalation_reasons": escalation_reasons,
                "predicted_intent": predicted_intent,
            },
        )
    except Exception:
        logger.exception("Interaction logging failed for query: %s", query)
        response["escalation_reasons"].append("logging_failure")

    return response


def create_app() -> Flask:
    """Create the minimal HTTP API for the academic prototype."""
    app = Flask(__name__)

    @app.get("/")
    def index():
        """Serve the helpdesk workspace."""
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/history")
    def history():
        """Return recent MongoDB interactions for the history view."""
        try:
            records = get_database()["helpdesk_interactions"].find(
                {},
                {
                    "timestamp": 1,
                    "query": 1,
                    "predicted_intent": 1,
                    "classifier_confidence": 1,
                    "source_document": 1,
                    "retrieval_similarity": 1,
                    "escalated": 1,
                    "grounded": 1,
                },
            ).sort("timestamp", -1).limit(100)
            interactions = [
                {
                    "timestamp": record.get("timestamp"),
                    "query": record.get("query", ""),
                    "predicted_intent": record.get("predicted_intent", "other"),
                    "classifier_confidence": record.get("classifier_confidence"),
                    "source_document": record.get("source_document"),
                    "retrieval_similarity": record.get("retrieval_similarity"),
                    "escalated": bool(record.get("escalated", False)),
                    "grounded": record.get("grounded"),
                }
                for record in records
            ]
            return jsonify({"interactions": interactions})
        except Exception:
            logger.exception("Interaction history could not be loaded")
            return jsonify({"error": "Interaction history is temporarily unavailable."}), 503

    @app.post("/query")
    def query():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400
        if "query" not in payload:
            return jsonify({"error": "Missing required field: query."}), 400
        if not isinstance(payload["query"], str) or not payload["query"].strip():
            return jsonify({"error": "Query must be a non-empty string."}), 400

        try:
            return jsonify(run_query_pipeline(payload["query"]))
        except FileNotFoundError:
            return jsonify({"error": "Bilingual classifier artifacts are unavailable."}), 503
        except Exception:
            return jsonify(
                {
                    "error": "The query could not be processed safely.",
                    "answer": UNAVAILABLE_MESSAGE,
                    "escalated": True,
                    "escalation_reasons": ["pipeline_failure"],
                }
            ), 503

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

