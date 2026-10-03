"""
Comprehensive pytest tests for TCS Retail Sentiment Intelligence Platform.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ml.inference.inference_engine import inference_engine
from app.ml.datasets.dataset_generator import generate_retail_dataset

client = TestClient(app)

class TestDatasetGeneration:
    def test_generates_correct_count(self):
        df = generate_retail_dataset(100)
        assert len(df) == 100

    def test_required_columns_present(self):
        df = generate_retail_dataset(50)
        required = {"text", "sentiment", "intent", "emotion", "aspect"}
        assert required.issubset(set(df.columns))

    def test_sentiment_classes_valid(self):
        df = generate_retail_dataset(200)
        valid = {"Positive", "Neutral", "Negative"}
        assert set(df["sentiment"].unique()).issubset(valid)

class TestSentimentPrediction:
    def test_positive_text(self):
        result = inference_engine.predict("The product is excellent and delivery was super fast!")
        assert result["sentiment"] in ["Positive", "Neutral"]
        assert result["sentiment_score"] > 0.0

    def test_negative_text(self):
        result = inference_engine.predict("Terrible quality, broken on arrival, no refund after 2 weeks!")
        assert result["sentiment"] in ["Negative", "Neutral"]
        assert result["sentiment_score"] < 0.2

    def test_confidence_in_range(self):
        result = inference_engine.predict("Good product, would recommend.")
        assert 0.0 <= result["confidence"] <= 1.0

class TestAPIValidation:
    def test_root_endpoint(self):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_sentiment_analyze_endpoint(self):
        resp = client.post("/api/sentiment/analyze", json={"text": "The delivery was very good!"})
        assert resp.status_code == 200
        data = resp.json()
        assert "sentiment" in data

    def test_feedback_list(self):
        resp = client.get("/api/feedback")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_analytics_overview(self):
        resp = client.get("/api/analytics/overview")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_feedback" in data

    def test_escalations_list(self):
        resp = client.get("/api/escalations")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_model_metrics(self):
        resp = client.get("/api/model/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["loaded"] is True
