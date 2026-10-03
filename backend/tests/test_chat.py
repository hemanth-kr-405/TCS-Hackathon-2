import pytest
from app.ml.empathetic_engine import EmpatheticChatEngine

def test_empathetic_chat_engine_responses():
    chat_engine = EmpatheticChatEngine()

    res_pos = chat_engine.process_user_message("I am really happy with my purchase!")
    assert res_pos["sentiment"] in ["Positive", "Neutral"]
    assert len(res_pos["empathetic_response"]) > 10

    res_neg = chat_engine.process_user_message("I am furious about my delayed refund and broken item. Connect me to a manager!")
    assert res_neg["triggered_escalation"] is True
    assert "escalat" in res_neg["empathetic_response"].lower() or "apologize" in res_neg["empathetic_response"].lower()
