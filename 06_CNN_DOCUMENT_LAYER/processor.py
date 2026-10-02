"""Phase 6: CNN Document Processor Interface."""

from typing import Dict, Any, Optional
import torch
from .model.cnn_model import DocumentLayoutCNN
from .dataset.schema import DOCUMENT_LAYOUT_CLASSES, get_dataset_status


class DocumentLayoutProcessor:
    """Processes document layout visual components using DocumentLayoutCNN."""

    def __init__(self):
        self.model = DocumentLayoutCNN(in_channels=1, num_classes=len(DOCUMENT_LAYOUT_CLASSES))
        self.model.eval()

    def classify_region(self, region_tensor: torch.Tensor) -> Dict[str, float]:
        """Classify a visual region into heading, table, paragraph, or other."""
        with torch.no_grad():
            probs = self.model.predict_structure(region_tensor)[0]
        return {
            cls_name: float(round(probs[idx].item(), 4))
            for idx, cls_name in enumerate(DOCUMENT_LAYOUT_CLASSES)
        }

    def status(self) -> Dict[str, Any]:
        """Return layer status."""
        return get_dataset_status()
