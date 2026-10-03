"""
Comprehensive Pytest Suite for Agentic AI Core — 12 Agentic Behavioral Tests.
"""
import pytest
from app.ml.ai_orchestrator import ai_orchestrator
from app.ml.tool_registry import tool_registry
from app.ml.customer_memory import customer_memory
from app.ml.decision_engine import decision_engine
from app.ml.rag.knowledge_base import knowledge_base, UNSUPPORTED_POLICY_FALLBACK


def test_1_general_chat_no_retail_tools():
    """1. General conversation -> no retail tool execution."""
    res = ai_orchestrator.orchestrate(message="Hello! How are you doing today?", history=[])
    assert res["interaction_mode"] == "GENERAL_CHAT"
    assert res["ai_decision"]["tool_required"] is False
    assert len(res["tools_executed"]) == 0


def test_2_retail_policy_rag():
    """2. Retail policy query -> RAG retrieval."""
    res = ai_orchestrator.orchestrate(message="What is your 30-day return policy and rules?", history=[])
    assert res["ai_decision"]["rag_required"] is True
    assert len(res["rag_sources"]) > 0


def test_3_order_query_tool():
    """3. Order tracking query -> get_order_status tool."""
    res = ai_orchestrator.orchestrate(message="Where is my order #45821?", history=[])
    assert res["ai_decision"]["tool_required"] is True
    assert res["ai_decision"]["selected_tool"] in ("get_order_status", "get_delivery_eta")
    assert any(t.get("tool") == "get_order_status" for t in res["tools_executed"])


def test_4_refund_eligibility_tool():
    """4. Refund eligibility query -> check_refund_eligibility tool."""
    tool_res = tool_registry.execute_tool("check_refund_eligibility", order_id="45821")
    assert tool_res["status"] == "SUCCESS"
    assert tool_res["eligible"] is True


def test_5_angry_customer_escalation():
    """5. Angry customer -> escalation analysis triggered."""
    res = ai_orchestrator.orchestrate(
        message="Charged twice for broken item! I demand a refund and manager now!",
        history=[],
        session_escalation_score=0.4,
    )
    assert res["escalation"]["should_escalate"] is True
    assert res["ai_decision"]["escalation_required"] is True


def test_6_repeated_complaint_increased_risk():
    """6. Repeated complaint -> increased customer risk score."""
    risk_1, _ = customer_memory.calculate_customer_risk("DEMO-1024", "Neutral", 0.0)
    customer_memory.update_memory("DEMO-1024", {"sentiment": "Negative", "issue": "Late delivery"})
    risk_2, reasons = customer_memory.calculate_customer_risk("DEMO-1024", "Negative", -0.7)
    assert risk_2 > risk_1
    assert len(reasons) > 0


def test_7_unknown_policy_refusal():
    """7. Unknown policy -> grounding validation score check."""
    docs = knowledge_base.retrieve("Can I get a 95% cash refund for radioactive space equipment after 360 days?")
    high_confidence_docs = [d for d in docs if d.get("score", 0) > 0.25]
    assert len(high_confidence_docs) == 0


def test_8_tool_failure_fallback():
    """8. Tool failure -> graceful error message."""
    res = tool_registry.execute_tool("get_order_status", order_id="NON_EXISTENT_999")
    assert res["status"] == "NOT_FOUND"
    assert "not found" in res["message"].lower()


def test_9_rag_failure_fallback():
    """9. RAG failure -> empty document list returned gracefully."""
    docs = knowledge_base.retrieve("")
    assert docs == []


def test_10_llm_failure_local_fallback():
    """10. LLM failure -> local empathetic fallback."""
    res = ai_orchestrator.orchestrate(message="My order is delayed", history=[], preferred_provider="invalid_provider")
    assert "response" in res
    assert res["response"] is not None


def test_11_customer_memory_retrieval():
    """11. Customer memory retrieval test."""
    mem = customer_memory.get_memory("DEMO-1024")
    assert mem["customer_id"] == "DEMO-1024"
    assert mem["customer_name"] == "Sarah Jenkins"


def test_12_decision_trace_correctness():
    """12. Decision trace structure correctness."""
    decision = decision_engine.evaluate_decision(
        message="Track order #45821",
        interaction_mode="RETAIL_SUPPORT",
        intent="Order_Tracking",
        sentiment="Negative",
        sentiment_score=-0.65,
        customer_id="DEMO-1024",
    )
    assert "interaction_mode" in decision
    assert "response_mode" in decision
    assert "customer_risk_score" in decision
    assert "reasoning" in decision
    assert decision["confidence"] > 0
