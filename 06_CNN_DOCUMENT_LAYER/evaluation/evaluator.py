"""Phase 6: CNN Document Layer Evaluation & Verification.

Verifies CNN parameter count, forward-pass consistency, and structural alignment.
"""

from pathlib import Path
import json
import torch
from ..model.cnn_model import DocumentLayoutCNN
from ..dataset.schema import DOCUMENT_LAYOUT_CLASSES, get_dataset_status

BASE_DIR = Path(__file__).resolve().parent.parent
EVAL_DIR = BASE_DIR / "evaluation"


def evaluate_cnn_architecture() -> dict:
    """Evaluate CNN model architecture readiness and tensor flow."""
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    model = DocumentLayoutCNN(in_channels=1, num_classes=len(DOCUMENT_LAYOUT_CLASSES))

    # Test dummy 224x224 grayscale tensor
    dummy_input = torch.randn(2, 1, 224, 224)
    with torch.no_grad():
        out = model(dummy_input)
        probs = model.predict_structure(dummy_input)

    total_params = sum(p.numel() for p in model.parameters())

    metrics = {
        "status": "ready_for_document_page_data",
        "total_parameters": total_params,
        "input_tensor_shape": list(dummy_input.shape),
        "output_tensor_shape": list(out.shape),
        "probability_sum_check": float(probs.sum(dim=-1)[0].item()),
        "classes": DOCUMENT_LAYOUT_CLASSES,
        "dataset_status": get_dataset_status(),
    }

    with open(EVAL_DIR / "cnn_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == "__main__":
    res = evaluate_cnn_architecture()
    print("CNN Architecture Evaluation:", res)
