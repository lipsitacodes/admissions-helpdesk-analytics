"""Phase 5: ANN Intent Dataset Builder.

Constructs multi-label training data strictly using canonical CUTM course titles
and domain-specific admission intents:
- fees
- course_information
- faculty
- hostel
- eligibility
- admission
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
DOC_LAYER_JSON = (
    PROJECT_ROOT
    / "01_DOCUMENT_LAYER"
    / "transformed"
    / "knowledge_records.json"
)

TARGET_INTENTS = [
    "fees",
    "course_information",
    "faculty",
    "hostel",
    "eligibility",
    "admission",
]

# Query formulation templates strictly using canonical course slots
TEMPLATES = [
    # Single Intent: Fees
    ("{course} fees", ["fees"]),
    ("{course} fee structure", ["fees"]),
    ("What is the fee for {course}?", ["fees"]),
    ("{course} ka fees kitna hai?", ["fees"]),
    ("{course} re kete fee lage?", ["fees"]),
    ("How much tuition fee for {course}?", ["fees"]),
    ("{course} cost and annual amount", ["fees"]),
    ("{course} ka total kharcha kitna hai?", ["fees"]),
    # Single Intent: Course Information
    ("About {course}", ["course_information"]),
    ("Details of {course}", ["course_information"]),
    ("What is {course} program all about?", ["course_information"]),
    ("{course} ke bare me batao", ["course_information"]),
    ("{course} ra overview kana achhi?", ["course_information"]),
    ("Overview and curriculum of {course}", ["course_information"]),
    # Single Intent: Faculty
    ("Who are the faculty members in {course}?", ["faculty"]),
    ("{course} faculty list", ["faculty"]),
    ("{course} ke professors kaun hai?", ["faculty"]),
    ("HOD and teachers in {course}", ["faculty"]),
    ("Who teaches in {course} department?", ["faculty"]),
    # Single Intent: Hostel
    ("Is hostel facility available for {course} students?", ["hostel"]),
    ("{course} hostel and mess", ["hostel"]),
    ("{course} me hostel accommodation kaisa hai?", ["hostel"]),
    ("Hostel rooms near {course} campus", ["hostel"]),
    # Single Intent: Eligibility
    ("Eligibility criteria for {course}", ["eligibility"]),
    ("What is the qualification required for {course}?", ["eligibility"]),
    ("{course} ke liye 12th me kitna percentage chahiye?", ["eligibility"]),
    ("Minimum marks required to join {course}", ["eligibility"]),
    # Single Intent: Admission
    ("How to apply for {course} admission?", ["admission"]),
    ("Admission procedure for {course}", ["admission"]),
    ("{course} admission process and CUEE entrance", ["admission"]),
    ("{course} me direct admission kaise milega?", ["admission"]),
    # Multi-Intent: Fees + Hostel
    ("{course} fees aur hostel details batao", ["fees", "hostel"]),
    ("What is the fee for {course} and hostel accommodation?", ["fees", "hostel"]),
    ("{course} fee and room mess charges", ["fees", "hostel"]),
    # Multi-Intent: Fees + Eligibility
    ("{course} fees aur eligibility kya hai?", ["fees", "eligibility"]),
    ("Eligibility and fee structure for {course}", ["fees", "eligibility"]),
    # Multi-Intent: Faculty + Fees
    ("{course} faculty aur fees bataiye", ["faculty", "fees"]),
    # Multi-Intent: Admission + Fees
    ("Admission process and fees for {course}", ["admission", "fees"]),
    ("{course} me admission kaise le aur fees kitni hai?", ["admission", "fees"]),
]


def build_ann_dataset() -> List[Dict[str, Any]]:
    """Build multi-label training samples based strictly on CUTM courses."""
    if not DOC_LAYER_JSON.exists():
        raise FileNotFoundError(f"Knowledge records not found at {DOC_LAYER_JSON}")

    with open(DOC_LAYER_JSON, "r", encoding="utf-8") as f:
        records = json.load(f)

    # Sample top representative course names to avoid combinatorial explosion
    course_names = [r["course_name"] for r in records]

    samples = []
    sample_id = 0

    for course in course_names:
        for tmpl, intents in TEMPLATES:
            query = tmpl.format(course=course)
            sample_id += 1
            # Multi-hot vector for target intents
            labels = [1.0 if intent in intents else 0.0 for intent in TARGET_INTENTS]
            samples.append({
                "sample_id": sample_id,
                "text": query,
                "course": course,
                "intents": intents,
                "labels": labels,
            })

    output_dir = BASE_DIR / "dataset"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "ann_intent_dataset.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)

    return samples


if __name__ == "__main__":
    data = build_ann_dataset()
    print(f"Generated {len(data)} training samples for ANN intent classification.")
