from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DOCS_DIR = DATA_DIR / "institutional_docs"
TRAINING_FILE = DATA_DIR / "training_queries.csv"
EVALUATION_FILE = DATA_DIR / "evaluation_queries.csv"
METADATA_FILE = DATA_DIR / "document_metadata.csv"
EXPECTED_QUERY_COLUMNS = ["query", "intent", "language", "topic", "expected_document"]
EXPECTED_METADATA_COLUMNS = [
    "document_id",
    "title",
    "category",
    "source_file",
    "topic_tags",
    "summary",
]
INTENT_LABELS = [
    "admission_process",
    "eligibility",
    "fee_structure",
    "scholarship",
    "hostel",
    "course_information",
    "documents_required",
    "application_deadline",
    "refund",
    "contact_admission",
    "other",
]
EXPECTED_DOCUMENTS = {
    "admission_process": "admission_process.txt",
    "eligibility": "eligibility.txt",
    "fee_structure": "fee_structure.txt",
    "scholarship": "scholarship.txt",
    "hostel": "hostel.txt",
    "course_information": "admission_process.txt",
    "documents_required": "admission_process.txt",
    "application_deadline": "deadlines.txt",
    "refund": "fee_structure.txt",
    "contact_admission": "admission_process.txt",
    "other": "",
}


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [row for row in reader if any(value.strip() for value in row.values())]
    return rows


def validate_headers(path: Path, expected_columns: List[str]) -> None:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        headers = next(reader, [])
    if headers != expected_columns:
        raise ValueError(
            f"{path.name} header mismatch. Expected {expected_columns}, got {headers}"
        )


def validate_query_rows(rows: List[Dict[str, str]], dataset_name: str, require_counts: bool = False) -> None:
    missing = []
    counts = {label: 0 for label in INTENT_LABELS}
    duplicates = {}
    seen = set()
    for row in rows:
        query = row.get("query", "").strip()
        intent = row.get("intent", "").strip()
        language = row.get("language", "").strip()
        topic = row.get("topic", "").strip()
        expected_document = row.get("expected_document", "").strip()

        if not query:
            raise ValueError(f"{dataset_name} contains an empty query.")
        if not intent:
            raise ValueError(f"{dataset_name} contains a missing intent for query: {query}")
        if intent not in INTENT_LABELS:
            raise ValueError(f"{dataset_name} contains unsupported intent: {intent}")
        if not language:
            raise ValueError(f"{dataset_name} contains a missing language for query: {query}")
        if topic != intent:
            raise ValueError(
                f"{dataset_name} query topic must match intent. Query: {query}, intent: {intent}, topic: {topic}"
            )
        expected = EXPECTED_DOCUMENTS[intent]
        if intent == "other":
            if expected_document:
                raise ValueError(
                    f"{dataset_name} other intent should not have expected_document: {query}"
                )
        else:
            if expected_document != expected:
                raise ValueError(
                    f"{dataset_name} query expected_document mismatch for intent {intent}: {query}. Expected {expected}, got {expected_document}"
                )

        counts[intent] += 1
        if query in seen:
            duplicates[query] = duplicates.get(query, 1) + 1
        else:
            seen.add(query)

    if duplicates:
        raise ValueError(f"{dataset_name} contains duplicate queries: {sorted(duplicates.items())}")
    if require_counts:
        for label in INTENT_LABELS:
            limit = (2, 3) if dataset_name == "evaluation" else (8, 10)
            if not (limit[0] <= counts[label] <= limit[1]):
                raise ValueError(
                    f"{dataset_name} intent {label} has {counts[label]} examples; expected between {limit[0]} and {limit[1]}"
                )


def validate_cross_dataset_overlap(training_rows: List[Dict[str, str]], evaluation_rows: List[Dict[str, str]]) -> None:
    training_queries = {row["query"].strip() for row in training_rows}
    evaluation_queries = {row["query"].strip() for row in evaluation_rows}
    overlap = training_queries & evaluation_queries
    if overlap:
        raise ValueError(f"Training and evaluation queries overlap: {sorted(overlap)}")


def validate_document_files(rows: List[Dict[str, str]]) -> None:
    missing = set()
    for row in rows:
        expected_document = row["expected_document"].strip()
        if expected_document:
            path = DOCS_DIR / expected_document
            if not path.exists():
                missing.add(expected_document)
    if missing:
        raise FileNotFoundError(
            f"Query references missing document files: {sorted(missing)}"
        )


def validate_documents_exist() -> None:
    missing = [path.name for path in DOCS_DIR.glob("*.txt") if path.stat().st_size == 0]
    if missing:
        raise ValueError(
            f"Institutional document files are empty: {sorted(missing)}"
        )


def validate_document_disclaimers() -> None:
    missing = []
    for path in DOCS_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        if "SYNTHETIC DEVELOPMENT DATA — NOT ACTUAL UNIVERSITY POLICY" not in text.splitlines()[0]:
            missing.append(path.name)
    if missing:
        raise ValueError(
            f"Institutional document files are missing the required disclaimer: {sorted(missing)}"
        )


def validate_metadata(rows: List[Dict[str, str]]) -> None:
    seen_ids = set()
    seen_sources = set()

    for row in rows:
        missing_fields = [key for key in EXPECTED_METADATA_COLUMNS if not row.get(key, "").strip()]
        if missing_fields:
            raise ValueError(
                f"Metadata row is missing required fields: {missing_fields}"
            )
        document_id = row["document_id"].strip()
        source_file = row["source_file"].strip()
        if document_id in seen_ids:
            raise ValueError(f"Duplicate document_id found: {document_id}")
        if source_file in seen_sources:
            raise ValueError(f"Duplicate source_file found: {source_file}")
        seen_ids.add(document_id)
        seen_sources.add(source_file)

    if len(rows) != len(seen_ids) or len(rows) != len(seen_sources):
        raise ValueError("Metadata contains duplicate document rows.")


def validate_metadata_document_coverage(metadata_rows: List[Dict[str, str]], query_rows: List[Dict[str, str]]) -> None:
    metadata_files = {row["source_file"].strip() for row in metadata_rows}
    query_docs = {row["expected_document"].strip() for row in query_rows if row["expected_document"].strip()}
    missing_in_metadata = query_docs - metadata_files
    if missing_in_metadata:
        raise ValueError(
            f"Documents referenced by queries are missing from metadata: {sorted(missing_in_metadata)}"
        )

    missing_in_docs = metadata_files - {path.name for path in DOCS_DIR.glob("*.txt")}
    if missing_in_docs:
        raise ValueError(
            f"Metadata references missing document files: {sorted(missing_in_docs)}"
        )


def validate_topic_tags_consistency(metadata_rows: List[Dict[str, str]]) -> None:
    for row in metadata_rows:
        tags = [tag.strip() for tag in row["topic_tags"].replace(";", ",").split(",") if tag.strip()]
        if not tags:
            raise ValueError(f"Metadata row {row['document_id']} has no topic tags.")


def main() -> int:
    for path, expected in [
        (TRAINING_FILE, EXPECTED_QUERY_COLUMNS),
        (EVALUATION_FILE, EXPECTED_QUERY_COLUMNS),
        (METADATA_FILE, EXPECTED_METADATA_COLUMNS),
    ]:
        if not path.exists():
            raise FileNotFoundError(f"Required data file is missing: {path}")
        validate_headers(path, expected)

    training_rows = read_csv_rows(TRAINING_FILE)
    evaluation_rows = read_csv_rows(EVALUATION_FILE)
    metadata_rows = read_csv_rows(METADATA_FILE)

    validate_query_rows(training_rows, "training", require_counts=True)
    validate_query_rows(evaluation_rows, "evaluation", require_counts=True)
    validate_cross_dataset_overlap(training_rows, evaluation_rows)
    validate_document_files(training_rows + evaluation_rows)
    validate_documents_exist()
    validate_document_disclaimers()
    validate_metadata(metadata_rows)
    validate_metadata_document_coverage(metadata_rows, training_rows + evaluation_rows)
    validate_topic_tags_consistency(metadata_rows)

    print("Data validation completed successfully.")
    print(f"Training queries: {len(training_rows)}")
    print(f"Evaluation queries: {len(evaluation_rows)}")
    print(f"Institutional documents: {len(list(DOCS_DIR.glob('*.txt')))}")
    print(f"Document metadata rows: {len(metadata_rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
