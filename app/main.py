"""Authoritative Flask application entry point delegation.

This module delegates directly to backend.main, ensuring there is a single
authoritative Flask application running the current bilingual classifier and RAG pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import (
    MODEL_PATH,
    VECTORIZER_PATH,
    app,
    create_app,
    get_classifier_artifacts,
    run_query_pipeline,
)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


