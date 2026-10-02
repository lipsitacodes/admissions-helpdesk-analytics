"""Phase 6: CNN Document Image Transforms & Preprocessing.

Standardizes document page regions into normalized tensor representations.
"""

from typing import Any
import torch
import torch.nn.functional as F


def preprocess_document_patch(image_tensor: torch.Tensor, target_size=(224, 224)) -> torch.Tensor:
    """Resize and normalize document layout patch tensor."""
    if len(image_tensor.shape) == 2:
        image_tensor = image_tensor.unsqueeze(0).unsqueeze(0)
    elif len(image_tensor.shape) == 3:
        image_tensor = image_tensor.unsqueeze(0)

    # Resize to target layout shape
    resized = F.interpolate(image_tensor, size=target_size, mode="bilinear", align_corners=False)
    # Normalize pixel intensity to [0, 1]
    normalized = (resized - resized.min()) / (resized.max() - resized.min() + 1e-7)
    return normalized
