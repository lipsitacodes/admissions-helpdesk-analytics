"""Phase 6: CNN Document Layer Dataset Schema & Specification.

Strict Rule: The CSV files themselves do not contain page-image data.
Actual CNN image training data must not be fabricated from the CSVs.
This module defines the architectural schema for Document Page Visual Layout:
Visual Layout Classes:
- heading
- table
- paragraph
- other
"""

from typing import Dict, List

DOCUMENT_LAYOUT_CLASSES = [
    "heading",
    "table",
    "paragraph",
    "other",
]

IMAGE_INPUT_SHAPE = (1, 224, 224)  # Grayscale document patch 224x224


def get_dataset_status() -> Dict[str, str]:
    """Report status of document layout image data."""
    return {
        "status": "awaiting_valid_source_page_scans",
        "allowed_source": "CUTM_Category_CSVs",
        "note": "CSV files do not contain page-image scans. Preserving integrity without synthetic fact fabrication.",
        "target_classes": DOCUMENT_LAYOUT_CLASSES,
        "input_shape": str(IMAGE_INPUT_SHAPE),
    }
