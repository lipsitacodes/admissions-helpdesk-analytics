import re
import sqlite3

import pytest

from backend import logger, main
from rag.generate_answer import UNAVAILABLE_MESSAGE


@pytest.fixture()
def client(tmp_path, monkeypatch):
	"""Use the real API while redirecting interaction logs to a temp database."""
	database_path = tmp_path / "test_interactions.db"

	def isolated_logger(**kwargs):
		return logger.log_interaction(database_path=database_path, **kwargs)

	monkeypatch.setattr(main, "log_interaction", isolated_logger)
	return main.create_app().test_client()


def test_health_endpoint(client):
	response = client.get("/health")

	assert response.status_code == 200
	assert response.get_json() == {"status": "ok"}


@pytest.mark.parametrize(
	("query", "expected_intent"),
	[
		("What is the refund policy?", "refund"),
		("hostel ka fees kitna hai?", "hostel"),
		("application kab tak kar sakte hain?", "application_deadline"),
	],
)
def test_valid_queries_return_expected_api_schema(client, query, expected_intent):
	response = client.post("/query", json={"query": query})
	body = response.get_json()

	assert response.status_code == 200
	assert body["predicted_intent"] == expected_intent
	assert body["answer"]
	assert isinstance(body["escalated"], bool)
	assert isinstance(body["escalation_reasons"], list)
	assert 0.0 <= body["classifier_confidence"] <= 1.0


@pytest.mark.parametrize(
	"payload",
	[{}, {"query": ""}, {"query": 123}],
)
def test_invalid_query_payloads_return_bad_request(client, payload):
	response = client.post("/query", json=payload)

	assert response.status_code == 400
	assert response.get_json()["error"]


@pytest.mark.parametrize(
	"query",
	[
		"Who can I contact for admission help?",
		"What courses are offered?",
		"What is the admissions phone number?",
	],
)
def test_unsupported_information_returns_safe_unavailable_answer(client, query):
	response = client.post("/query", json={"query": query})
	body = response.get_json()

	assert response.status_code == 200
	assert body["answer"] == UNAVAILABLE_MESSAGE
	assert body["escalated"] is True
	assert not re.search(r"(?:phone|email|@|\$|\b(?:rs|inr)\.?\s*\d)", body["answer"], re.I)


def test_other_intent_returns_safe_escalation(client):
	response = client.post("/query", json={"query": "Are there any music clubs?"})
	body = response.get_json()

	assert response.status_code == 200
	assert body["predicted_intent"] == "other"
	assert body["retrieved_chunks"] == []
	assert body["answer"] == UNAVAILABLE_MESSAGE
	assert body["escalated"] is True


def test_exact_fee_query_does_not_invent_a_specific_amount(client):
	response = client.post("/query", json={"query": "How much is the exact tuition fee?"})
	body = response.get_json()

	assert response.status_code == 200
	assert not re.search(r"(?:₹|\$|\b(?:rs|inr)\.?\s*\d)", body["answer"], re.I)


def test_valid_request_is_logged_in_isolated_database(client, tmp_path):
	response = client.post("/query", json={"query": "What is the refund policy?"})
	assert response.status_code == 200

	database_path = next(tmp_path.glob("test_interactions.db"))
	with sqlite3.connect(database_path) as connection:
		columns = [row[1] for row in connection.execute("PRAGMA table_info(helpdesk_interactions)")]
		row = connection.execute(
			"SELECT query, predicted_intent, source_document, escalated "
			"FROM helpdesk_interactions"
		).fetchone()

	assert columns == [
		"id",
		"timestamp",
		"query",
		"predicted_intent",
		"classifier_confidence",
		"source_document",
		"retrieval_similarity",
		"escalated",
		"escalation_reason",
	]
	assert row[0] == "What is the refund policy?"
	assert row[1] == "refund"
	assert row[2] == "fee_structure.txt"
	assert row[3] in (0, 1)
