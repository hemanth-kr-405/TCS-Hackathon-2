"""
Comprehensive Test Suite for Demo Scenarios, Decision Trace, Provider Fallback, and Reset Demo API.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ml.ai_orchestrator import ai_orchestrator
from app.ml.rag.knowledge_base import knowledge_base

client = TestClient(app)


def test_demo_reset_api():
    """Test POST /api/v1/chat/reset-demo clears state and creates baseline session."""
    response = client.post("/api/v1/chat/reset-demo")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "demo_session_id" in data
    assert data["demo_session_id"] == "demo_session_1024"


def test_scenario_a_happy_customer():
    """Scenario A: Happy customer praise -> Positive sentiment, no escalation."""
    res = ai_orchestrator.orchestrate(
        message="I received my dress today! It fits perfectly and delivery was super fast.",
        history=[],
    )
    assert res["sentiment"] == "Positive"
    assert res["sentiment_score"] > 0
    assert res["escalation"]["should_escalate"] is False
    assert res["interaction_mode"] in ("RETAIL_SUPPORT", "GENERAL_CHAT")


def test_scenario_b_delivery_complaint():
    """Scenario B: Delivery delay complaint -> Negative sentiment, tracking intent, entities extracted."""
    res = ai_orchestrator.orchestrate(
        message="My order #45821 is 3 days late and tracking hasn't updated in 48 hours!",
        history=[],
    )
    assert res["sentiment"] == "Negative"
    assert res["sentiment_score"] < 0
    assert res["intent"] in ("Order Tracking", "Complaint", "Delivery SLA Query")
    assert res["entities"].get("order_id") == "45821" or "45821" in str(res["entities"])


def test_scenario_c_angry_customer_escalation():
    """Scenario C: Angry customer demand -> High escalation score, escalation triggered."""
    res = ai_orchestrator.orchestrate(
        message="Charged twice for a broken item! I demand a refund and manager immediately!",
        history=[],
        session_escalation_score=0.4,
    )
    assert res["sentiment"] == "Negative"
    assert res["escalation"]["should_escalate"] is True
    assert res["escalation"]["severity"] in ("High", "Critical")


def test_scenario_d_refund_policy_rag():
    """Scenario D: Policy inquiry -> RAG documents retrieved from knowledge base."""
    rag_section, docs = knowledge_base.build_rag_prompt_section("What is your return policy and refund timeline?")
    assert len(docs) > 0
    assert any("policy" in d["filename"].lower() or "return" in d["title"].lower() for d in docs)


def test_scenario_e_sentiment_recovery():
    """Scenario E: Resolution praise -> Positive sentiment recovery."""
    res = ai_orchestrator.orchestrate(
        message="Thank you for tracking my replacement! That resolves my concern completely.",
        history=[
            {"sender": "user", "text": "My package is delayed", "sentiment": "Negative", "sentiment_score": -0.6}
        ],
    )
    assert res["sentiment"] == "Positive"
    assert res["context"]["sentiment_direction"] == "improved"


def test_customer_analysis_endpoint():
    """Test POST /api/v1/chat/sessions/{session_id}/analyze-customer."""
    # Reset demo first
    reset_res = client.post("/api/v1/chat/reset-demo")
    demo_id = reset_res.json()["demo_session_id"]

    res = client.post(f"/api/v1/chat/sessions/{demo_id}/analyze-customer")
    assert res.status_code == 200
    data = res.json()
    assert "customer_id" in data
    assert "main_issue" in data
    assert "recommended_action" in data
