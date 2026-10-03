"""
Agentic Decision Engine for TCS Retail Intelligence Platform.

Evaluates user message, interaction mode, intent, and customer memory
to generate a structured AIDecision object BEFORE executing tools or LLM calls.
"""
import logging
from typing import Dict, Any, Optional, List
from app.ml.customer_memory import customer_memory

logger = logging.getLogger(__name__)


class AIDecisionEngine:
    """Evaluates context & message to decide Agent execution path."""

    def evaluate_decision(
        self,
        message: str,
        interaction_mode: str,
        intent: str,
        sentiment: str,
        sentiment_score: float,
        customer_id: str = "DEMO-1024",
        extracted_entities: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        extracted_entities = extracted_entities or {}
        order_id = extracted_entities.get("order_id")
        action = extracted_entities.get("requested_action")
        clean_msg = message.lower()

        is_general_chat = (interaction_mode == "GENERAL_CHAT")

        # Compute Customer Risk Score
        risk_score, risk_reasons = customer_memory.calculate_customer_risk(
            customer_id=customer_id,
            current_sentiment=sentiment,
            current_score=sentiment_score,
        )

        # General Chat Branch -> No retail tool or memory overhead
        if is_general_chat:
            return {
                "interaction_mode": "GENERAL_CHAT",
                "response_mode": "GENERAL_CONVERSATION",
                "sentiment_required": False,
                "rag_required": False,
                "tool_required": False,
                "memory_required": False,
                "escalation_required": False,
                "selected_tool": None,
                "selected_sources": [],
                "customer_risk_score": 0.10,
                "risk_reasons": [],
                "reasoning": "General conversation detected — skipping retail tool and RAG pipeline.",
                "confidence": 0.98,
            }

        # Retail Branch Tool Selection Logic
        selected_tool = None
        rag_required = False
        tool_required = False
        response_mode = "DIRECT_EMPATHETIC"
        selected_sources = []

        # 1. Order Status / Delivery Tool
        if order_id or "order" in clean_msg or "track" in clean_msg or "delivery" in clean_msg or intent in ("Order_Tracking", "Shipping_Delay"):
            tool_required = True
            selected_tool = "get_order_status"
            response_mode = "TOOL_EXECUTION"

        # 2. Refund Check Tool
        if action == "refund" or "refund" in clean_msg or intent in ("Refund_Request", "Billing_Issue"):
            tool_required = True
            selected_tool = "check_refund_eligibility"
            response_mode = "TOOL_EXECUTION"

        # 3. Policy RAG Query
        if "policy" in clean_msg or "return" in clean_msg or "warranty" in clean_msg or "sla" in clean_msg or intent in ("Return_Policy", "Policy_Query"):
            rag_required = True
            response_mode = "RAG_RETRIEVAL" if not tool_required else "TOOL_AND_RAG"
            selected_sources = ["return_policy.md", "refund_policy.md"]

        # 4. Escalation Trigger Check
        escalation_required = (risk_score >= 0.75 or interaction_mode == "ESCALATION" or "manager" in clean_msg or "supervisor" in clean_msg)
        if escalation_required:
            selected_tool = "escalate_to_agent"
            response_mode = "HUMAN_HANDOFF"

        reasoning = (
            f"Evaluated mode {interaction_mode} with intent {intent}. "
            f"Tool: {selected_tool or 'None'}, RAG: {rag_required}, Risk: {risk_score}."
        )

        decision = {
            "interaction_mode": interaction_mode,
            "response_mode": response_mode,
            "sentiment_required": True,
            "rag_required": rag_required,
            "tool_required": tool_required,
            "memory_required": True,
            "escalation_required": escalation_required,
            "selected_tool": selected_tool,
            "selected_sources": selected_sources,
            "customer_risk_score": risk_score,
            "risk_reasons": risk_reasons,
            "reasoning": reasoning,
            "confidence": 0.94,
        }

        logger.info(f"AI DECISION GENERATED | mode={interaction_mode} | tool={selected_tool} | risk={risk_score}")
        return decision


decision_engine = AIDecisionEngine()
