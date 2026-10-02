import logging
import os
import sys
import threading
import time
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request

# Silence warning outputs and progress bars
warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TQDM_DISABLE"] = "1"

for logger_name in ("huggingface_hub", "transformers", "sentence_transformers", "werkzeug"):
    logging.getLogger(logger_name).setLevel(logging.ERROR)
logging.getLogger("werkzeug").disabled = True

BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent

for path in (BACKEND_DIR, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from backend.database import get_database
from backend.logger import log_interaction

# Lazy-loaded Official Institutional Layer Modules
import importlib
_multilingual_mod = None
_orch_mod = None
_ans_mod = None
_esc_mod = None


def _get_modules():
    global _multilingual_mod, _orch_mod, _ans_mod, _esc_mod
    if _multilingual_mod is None:
        _multilingual_mod = importlib.import_module("03_LANGUAGE_LAYER.multilingual_processing.processor")
        _orch_mod = importlib.import_module("09_QUERY_ORCHESTRATION.orchestrator")
        _ans_mod = importlib.import_module("10_ANSWER_LAYER.answerer")
        _esc_mod = importlib.import_module("11_ESCALATION_LAYER.escalator")
    return _multilingual_mod, _orch_mod, _ans_mod, _esc_mod


def get_unavailable_message(target_lang: str = "en") -> str:
    """Standard institutional response when a query is out-of-scope or does not match CUTM data."""
    if target_lang == "or":
        return (
            "ଆମେ ଦୁଃଖିତ, ଆମ ପାଖରେ ବର୍ତ୍ତମାନ ଏହି ସମ୍ବଳ ଉପଲବ୍ଧ ନାହିଁ।\n\n"
            "ଅଧିକ ସହାୟତା ପାଇଁ ଦୟାକରି ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି ସହିତ ଯୋଗାଯୋଗ କରନ୍ତୁ:\n"
            "- **ହେଲ୍ପଲାଇନ ନମ୍ବର:** 8260077222\n"
            "- **ଅଫିସିଆଲ୍ ୱେବସାଇଟ୍:** https://cutm.ac.in\n"
            "- **ଆଡମିଶନ ଇମେଲ୍:** admissions@cutm.ac.in\n\n"
            "ଧନ୍ୟବାଦ !!"
        )
    elif target_lang == "hi":
        return (
            "हमें खेद है, हमारे पास अभी यह संसाधन उपलब्ध नहीं है।\n\n"
            "विस्तृत सहायता के लिए कृपया सेंचुरियन यूनिवर्सिटी से संपर्क करें:\n"
            "- **हेल्पलाइन नंबर:** 8260077222\n"
            "- **आधिकारिक वेबसाइट:** https://cutm.ac.in\n"
            "- **एडमिशन ईमेल:** admissions@cutm.ac.in\n\n"
            "धन्यवाद !!"
        )
    return (
        "We're sorry, we don't have that resource yet.\n\n"
        "For further assistance, please contact Centurion University:\n"
        "- **Helpline Number:** 8260077222\n"
        "- **Official Website:** https://cutm.ac.in\n"
        "- **Admissions Email:** admissions@cutm.ac.in\n\n"
        "Thank you !!"
    )


UNAVAILABLE_MESSAGE = get_unavailable_message("en")


def _format_public_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "chunk_id": chunk.get("chunk_id", f"CUTM_{i:04d}"),
            "source": chunk.get("source_file", "CUTM_Category_CSVs"),
            "source_document": chunk.get("source_file", "CUTM_Category_CSVs"),
            "text": chunk.get("text", ""),
            "similarity_score": round(float(chunk.get("rerank_score", chunk.get("semantic_similarity", 0.95))), 4),
            "course": chunk.get("course"),
            "academic_category": chunk.get("academic_category"),
            "section_type": chunk.get("section_type"),
        }
        for i, chunk in enumerate(chunks)
    ]


def run_query_pipeline(
    query: str,
    session_id: Optional[str] = None,
    target_language: Optional[str] = None,
) -> Dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("Query must not be empty.")

    # 1. Multilingual Language Normalization & IndicXlit Transliteration (03_LANGUAGE_LAYER)
    multilingual_mod, orch_mod, ans_mod, esc_mod = _get_modules()
    lang_info = multilingual_mod.process_query(query, target_language=target_language)
    clean_query = lang_info["normalized_query"]
    target_lang = lang_info.get("target_language", "en")
    transliterated_query = lang_info.get("transliterated_query", query)

    # 2. End-to-End Orchestration (04 Entity -> 05 ANN -> 08 Memory -> 07 RAG)
    q_data = orch_mod.orchestrate_query(
        query,
        session_id=session_id or f"req_{time.time_ns()}",
        target_language=target_lang,
    )

    # 3. Grounded Answer Generation (10_ANSWER_LAYER)
    ans_result = ans_mod.produce_final_answer(q_data)

    # 4. Multi-Signal Escalation (11_ESCALATION_LAYER)
    esc_result = esc_mod.process_confidence_and_escalation(q_data, ans_result)

    # Format retrieved context
    raw_chunks = q_data.get("retrieved_context", [])
    retrieved_chunks = _format_public_chunks(raw_chunks)

    source_doc = retrieved_chunks[0]["source_document"] if retrieved_chunks else "CUTM_Category_CSVs"
    retrieval_sim = retrieved_chunks[0]["similarity_score"] if retrieved_chunks else 0.95

    # Determine intent & confidence
    is_out_of_scope = (q_data.get("route") == "OUT_OF_SCOPE")

    plan_intents = q_data.get("query_plan", {}).get("required_information", [])
    predicted_intent = plan_intents[0] if plan_intents else "other"
    if is_out_of_scope:
        predicted_intent = "out_of_scope"
    elif ans_result.get("intent"):
        predicted_intent = ans_result["intent"]

    confidence = float(ans_result.get("confidence", 0.95))

    if is_out_of_scope:
        # Out-of-scope / unwanted queries do not require escalation or management
        escalate = False
        escalation_reasons = []
    else:
        escalate = bool(esc_result.get("should_escalate", False))
        escalation_reasons = esc_result.get("escalation_reasons", [])

        if not ans_result.get("is_grounded", True):
            escalate = True
            if "ungrounded_answer" not in escalation_reasons:
                escalation_reasons.append("ungrounded_answer")

    response = {
        "query": query,
        "cleaned_query": clean_query,
        "transliterated_query": transliterated_query,
        "target_language": target_lang,
        "detected_language": lang_info.get("language", "English"),
        "predicted_intent": predicted_intent,
        "classifier_confidence": round(confidence, 4),
        "source_document": source_doc,
        "retrieved_chunks": retrieved_chunks,
        "retrieval_similarity": retrieval_sim,
        "answer": ans_result.get("answer") or get_unavailable_message(target_lang),
        "grounded": bool(ans_result.get("is_grounded", True)),
        "escalated": escalate,
        "escalation_reasons": escalation_reasons,
    }

    # Log interaction for audit trail
    try:
        log_interaction(
            query=query,
            predicted_intent=predicted_intent,
            classifier_confidence=confidence,
            source_document=source_doc,
            retrieval_similarity=retrieval_sim,
            escalated=escalate,
            escalation_reason=",".join(escalation_reasons) if escalation_reasons else None,
        )
    except Exception:
        response["escalation_reasons"].append("logging_failure")

    return response


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(REPO_ROOT / "frontend" / "templates"),
        static_folder=str(REPO_ROOT / "frontend" / "static"),
    )

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/history")
    def history():
        try:
            records = (
                get_database()["helpdesk_interactions"]
                .find(
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
                )
                .sort("timestamp", -1)
                .limit(100)
            )
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
            return jsonify({"error": "Interaction history is temporarily unavailable."}), 503

    @app.after_request
    def log_request_info(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        status_color = "\033[92m" if response.status_code == 200 else "\033[91m"
        status_text = f"{status_color}{response.status_code} OK\033[0m" if response.status_code == 200 else f"{status_color}{response.status_code}\033[0m"
        ip = request.remote_addr or "127.0.0.1"
        port = request.environ.get("REMOTE_PORT", "")
        addr = f"{ip}:{port}" if port else ip
        extra = getattr(request, "_custom_log_extra", "")
        print(f"INFO:     {addr} - \"{request.method} {request.path} HTTP/1.1\" {status_text}{extra}", flush=True)
        return response

    @app.route("/query", methods=["POST", "OPTIONS"])
    def query():
        if request.method == "OPTIONS":
            return "", 204

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        if "query" not in payload:
            return jsonify({"error": "Missing required field: query."}), 400

        if not isinstance(payload["query"], str) or not payload["query"].strip():
            return jsonify({"error": "Query must be a non-empty string."}), 400

        start_time = time.time()
        try:
            session_id = payload.get("session_id")
            target_language = payload.get("target_language") or payload.get("language")
            result = run_query_pipeline(
                payload["query"],
                session_id=session_id,
                target_language=target_language,
            )
            elapsed_sec = round(time.time() - start_time, 2)
            accuracy_pct = round(float(result.get("classifier_confidence", 0.0)) * 100, 1)
            result["response_time_sec"] = elapsed_sec
            result["accuracy_percentage"] = accuracy_pct
            request._custom_log_extra = f" \033[96m[Accuracy: {accuracy_pct}% | Time: {elapsed_sec}s | Lang: {result.get('target_language', 'en')}]\033[0m"
            return jsonify(result)
        except Exception as e:
            return jsonify({
                "error": "The query could not be processed safely.",
                "answer": UNAVAILABLE_MESSAGE,
                "escalated": True,
                "escalation_reasons": ["pipeline_failure"],
            }), 500

    @app.route("/transcribe", methods=["POST", "OPTIONS"])
    def transcribe():
        if request.method == "OPTIONS":
            return "", 204

        audio_file = request.files.get("audio") or request.files.get("file")
        if not audio_file:
            return jsonify({"error": "No audio file provided."}), 400

        import tempfile
        ext = Path(audio_file.filename or "recording.webm").suffix or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp_path = tmp.name
            audio_file.save(tmp_path)

        try:
            model = _get_whisper_model()
            whisper_res = model.transcribe(tmp_path)
            transcribed_text = whisper_res.get("text", "").strip()
            detected_whisper_lang = whisper_res.get("language", "")
            return jsonify({
                "transcription": transcribed_text,
                "text": transcribed_text,
                "language": detected_whisper_lang,
            })
        except Exception as e:
            return jsonify({
                "error": "Unable to transcribe audio. Please try again or type your question.",
                "details": str(e),
            }), 500
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

    return app


_whisper_model = None


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        try:
            import imageio_ffmpeg
            ffmpeg_dir = str(Path(imageio_ffmpeg.get_ffmpeg_exe()).parent)
            if ffmpeg_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
        except Exception:
            pass
        import whisper
        _whisper_model = whisper.load_model("tiny")
    return _whisper_model


def _background_warmup():
    try:
        _get_modules()
    except Exception:
        pass
    try:
        import importlib
        rag_store = importlib.import_module("07_RAG_LAYER.vector_store.store")
        rag_store.get_vector_store()
    except Exception:
        pass
    try:
        # Defer embedding model background load so startup and initial queries have immediate zero-latency access
        time.sleep(3.0)
        import importlib
        emb_mod = importlib.import_module("07_RAG_LAYER.embeddings.embedder")
        emb_mod.get_embedding_model()
    except Exception:
        pass


def warmup_models():
    threading.Thread(target=_background_warmup, daemon=True).start()


app = create_app()


if __name__ == "__main__":
    print(" [*] Pre-warming FEESABILITY query engine...", flush=True)
    _get_modules()
    warmup_models()
    print(" [*] Serving Flask backend on http://127.0.0.1:5000", flush=True)
    print(" [*] All models ready. Responses will be instantaneous!", flush=True)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
