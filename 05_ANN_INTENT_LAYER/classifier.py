"""Phase 5: ANN Intent Classifier Runtime Interface.

Loads trained neural network weights and outputs multi-label probability scores.
Example:
Input: 'Bhai BSc Agriculture ka fees aur hostel batao'
Output: {'fees': 0.96, 'hostel': 0.91}
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional
import torch

from .model.ann_model import MultiLabelANN
from .preprocessing.vectorizer import load_vectorizer

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model"


class ANNIntentClassifier:
    """Runtime classifier interface for multi-label intent prediction."""

    def __init__(self):
        self.model: Optional[MultiLabelANN] = None
        self.vectorizer = None
        self.classes: List[str] = []
        self._load()

    def _load(self):
        meta_file = MODEL_DIR / "classes.json"
        weights_file = MODEL_DIR / "ann_intent_weights.pt"
        vec_file = MODEL_DIR / "vectorizer.joblib"

        if not (meta_file.exists() and weights_file.exists() and vec_file.exists()):
            # Lazy train if not yet built
            from .training.trainer import train_ann_intent_model
            self.model = train_ann_intent_model(epochs=10)
            with open(meta_file, "r") as f:
                meta = json.load(f)
            self.classes = meta["classes"]
            self.vectorizer = load_vectorizer(str(vec_file))
            return

        with open(meta_file, "r") as f:
            meta = json.load(f)

        self.classes = meta["classes"]
        self.vectorizer = load_vectorizer(str(vec_file))
        self.model = MultiLabelANN(
            input_dim=meta["input_dim"],
            hidden_dim=128,
            output_dim=meta["output_dim"]
        )
        self.model.load_state_dict(torch.load(weights_file, map_location="cpu"))
        self.model.eval()

    def predict_intents(self, query: str, threshold: float = 0.35) -> Dict[str, float]:
        """Predict multi-label intents and return dict of {intent: probability}."""
        if self.model is None or self.vectorizer is None:
            self._load()

        vec = self.vectorizer.transform([query]).toarray()
        x_tensor = torch.tensor(vec, dtype=torch.float32)

        with torch.no_grad():
            probs = self.model.predict_proba(x_tensor).numpy()[0]

        predictions = {}
        for intent, prob in zip(self.classes, probs):
            prob_float = float(round(prob, 4))
            if prob_float >= threshold:
                predictions[intent] = prob_float

        # Fallback if no intent crossed threshold
        if not predictions:
            max_idx = int(probs.argmax())
            predictions[self.classes[max_idx]] = float(round(probs[max_idx], 4))

        return predictions


_classifier = ANNIntentClassifier()


def classify_intent(query: str, threshold: float = 0.35) -> Dict[str, float]:
    """Top-level helper returning {intent: probability}."""
    return _classifier.predict_intents(query, threshold)
