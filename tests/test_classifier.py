import pytest

from app.main import get_classifier_artifacts
from preprocessing.clean_text import clean_text


@pytest.fixture(scope="module")
def classifier_artifacts():
	"""Load the approved bilingual v2 artifacts without retraining."""
	return get_classifier_artifacts()


def predict_with_v2(query, classifier_artifacts):
	model, vectorizer = classifier_artifacts
	query_vector = vectorizer.transform([clean_text(query)])
	predicted_intent = model.predict(query_vector)[0]
	confidence = float(model.predict_proba(query_vector)[0].max())
	return predicted_intent, confidence


@pytest.mark.parametrize(
	("query", "expected_intent"),
	[
		("What is the refund policy?", "refund"),
		("hostel ka fees kitna hai?", "hostel"),
		("What documents do I need?", "documents_required"),
		("application kab tak kar sakte hain?", "application_deadline"),
		("Who can I contact for admission help?", "contact_admission"),
	],
)
def test_bilingual_v2_intent_predictions(query, expected_intent, classifier_artifacts):
	predicted_intent, confidence = predict_with_v2(query, classifier_artifacts)

	assert predicted_intent == expected_intent
	assert 0.0 <= confidence <= 1.0


def test_bilingual_v2_prediction_exposes_confidence(classifier_artifacts):
	predicted_intent, confidence = predict_with_v2(
		"hostel ka fees kitna hai?", classifier_artifacts
	)

	assert isinstance(predicted_intent, str)
	assert isinstance(confidence, float)
