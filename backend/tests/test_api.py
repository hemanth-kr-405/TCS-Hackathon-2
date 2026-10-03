import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()

def test_sentiment_api():
    response = client.post("/api/sentiment/analyze", json={
        "text": "The delivery was quick and packaging was neat."
    })
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "sentiment_score" in data

def test_analytics_overview():
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_feedback" in data

def test_model_metrics():
    response = client.get("/api/model/status")
    assert response.status_code == 200
    data = response.json()
    assert data["loaded"] is True
