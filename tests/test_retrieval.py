import pytest

from rag.retrieve import INTENT_DOCUMENT_MAP, retrieve


@pytest.mark.parametrize(
	("query", "intent", "expected_source"),
	[
		("Where can I stay on campus?", "hostel", "hostel.txt"),
		("What is the refund policy?", "refund", "fee_structure.txt"),
		("application kab tak kar sakte hain?", "application_deadline", "deadlines.txt"),
		("How can I apply for financial aid?", "scholarship", "scholarship.txt"),
		("Who is eligible to apply?", "eligibility", "eligibility.txt"),
	],
)
def test_retrieve_routes_to_expected_document(query, intent, expected_source):
	results = retrieve(query, intent)

	assert results
	assert all(result["source"] == expected_source for result in results)
	assert all(result["text"].strip() for result in results)
	assert all(result["chunk_id"] is not None for result in results)
	assert all("similarity_score" in result for result in results)


def test_other_intent_has_no_knowledge_source():
	assert INTENT_DOCUMENT_MAP["other"] is None
	assert retrieve("Are there any music clubs?", "other") == []
