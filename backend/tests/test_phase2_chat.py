"""
Phase 2 / Chat Test Suite — Empathetic Chatbot, Sentiment Trajectory & Demo Scenarios.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestChatbotAPIRoutes:
    def test_session_creation(self):
        response = client.post("/api/v1/chat/sessions", json={"customer_name": "Test User"})
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data

    def test_chat_message_flow(self):
        sess_resp = client.post("/api/v1/chat/sessions", json={"customer_name": "Timeline User"})
        session_id = sess_resp.json()["session_id"]

        # Send turn 1
        msg1 = client.post("/api/v1/chat/message", json={"session_id": session_id, "message": "I love this store!"})
        assert msg1.status_code == 200

        # Send turn 2
        msg2 = client.post("/api/v1/chat/message", json={"session_id": session_id, "message": "My order is missing and delayed!"})
        assert msg2.status_code == 200
        assert "empathetic_response" in msg2.json()

class TestDemoScenarios:
    def test_scenario_1_positive(self):
        sess_resp = client.post("/api/v1/chat/sessions", json={"customer_name": "Scenario 1 Customer"})
        session_id = sess_resp.json()["session_id"]

        res = client.post(
            "/api/v1/chat/message",
            json={"session_id": session_id, "message": "I received my laptop today. Everything is perfect!"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["sentiment"] in ("Positive", "Neutral")

    def test_scenario_2_escalating(self):
        sess_resp = client.post("/api/v1/chat/sessions", json={"customer_name": "Scenario 2 Customer"})
        session_id = sess_resp.json()["session_id"]

        res = client.post(
            "/api/v1/chat/message",
            json={"session_id": session_id, "message": "I want to speak to a manager right now! This is fraud!"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["triggered_escalation"] is True
