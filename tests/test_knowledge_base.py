import json
from pathlib import Path

import pytest

from rag.generate_answer import compose_answer
from rag.retrieve import retrieve

ROOT_DIR = Path(__file__).resolve().parents[1]
RECORDS_FILE = ROOT_DIR / "data" / "knowledge_base_records.json"


@pytest.fixture(scope="module")
def records():
    return json.loads(RECORDS_FILE.read_text(encoding="utf-8"))["records"]


def test_structured_knowledge_base_has_required_coverage(records):
    assert len(records) == 49
    assert sum(len(record["question_variations"]) for record in records) == 164
    assert {record["source_status"] for record in records} == {"DEMO", "SYNTHETIC_DEMO", "UNKNOWN"}
    assert sum(record["domain"] == "program" for record in records) == 10
    assert sum(record["domain"] == "fees" for record in records) == 19
    assert {record["source_document"] for record in records} >= {
        "programs.txt",
        "admission_documents.txt",
        "academic_information.txt",
        "examination_fees.txt",
    }


def test_every_program_has_eligibility_and_route_fields(records):
    programs = [record for record in records if record["domain"] == "program"]
    assert all(record.get("eligibility") for record in programs)
    assert all(record.get("admission_route") for record in programs)


@pytest.mark.parametrize(
    ("query", "intent", "expected_branch"),
    [
        ("What is CSE?", "course_information", "Computer Science and Engineering"),
        ("CSE AI ML kya hai?", "course_information", "Artificial Intelligence and Machine Learning"),
        ("What is ECE?", "course_information", "Electronics and Communication"),
        ("Mechanical engineering me kya padhte hain?", "course_information", "Mechanical"),
        ("Civil engineering ka scope kya hai?", "course_information", "Civil"),
        ("What is EEE?", "course_information", "Electrical and Electronics"),
        ("Agricultural Engineering kya hai?", "course_information", "Agricultural"),
        ("Dairy Technology kya hai?", "course_information", "Dairy"),
        ("Drone Technology kya hai?", "course_information", "Drone"),
        ("Aeronautical Engineering kya hai?", "course_information", "Aeronautical"),
    ],
)
def test_branch_queries_retrieve_branch_specific_records(query, intent, expected_branch):
    results = retrieve(query, intent)
    assert results
    assert results[0]["source"] == "programs.txt"
    assert expected_branch.lower() in results[0]["branch"].lower()
    assert results[0]["source_status"] in {"DEMO", "UNKNOWN"}


def test_fee_and_exam_queries_use_distinct_sources():
    academic = retrieve("B.Tech fees kya hai?", "fee_structure")
    examination = retrieve("Exam fee kitni hai?", "fee_structure")

    assert academic[0]["source"] == "fee_structure.txt"
    assert academic[0]["topic"] == "academic tuition"
    assert examination[0]["source"] == "examination_fees.txt"
    assert examination[0]["topic"] == "examination fee"


@pytest.mark.parametrize(
    ("query", "intent", "record_id", "amount_text"),
    [
        ("cse ka fees kya hei?", "fee_structure", "fee-cse-academic", "INR 160,000"),
        ("cse ai ml ka fee kitna hai?", "fee_structure", "fee-ai-ml-academic", "INR 175,000"),
        ("hostel ka fees kitna hai?", "hostel", "fee-hostel", "INR 90,000"),
        ("exam fee kya hei?", "fee_structure", "fee-examination", "INR 3,000"),
    ],
)
def test_synthetic_fee_records_return_demo_amounts(query, intent, record_id, amount_text):
    results = retrieve(query, intent)

    assert results[0]["record_id"] == record_id
    assert results[0]["source_status"] == "SYNTHETIC_DEMO"
    assert amount_text in results[0]["amount"]


def test_retrieved_context_produces_grounded_branch_answer():
    chunks = retrieve("What is ECE?", "course_information")
    answer = compose_answer("What is ECE?", "course_information", chunks)

    assert answer["grounded"] is True
    assert answer["source"] == "programs.txt"
    assert "Electronics and Communication Engineering" in answer["answer"]
