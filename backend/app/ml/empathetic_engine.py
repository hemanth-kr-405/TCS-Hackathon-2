"""
Empathetic Chat Engine — Phase 2 Upgrade for TCS Retail Platform.

Integrates:
- ConversationContextService for context window & FSM state
- Safe empathetic responses tailored by emotion (Frustrated, Angry, Confused, Positive, Neutral)
- Strict safety rules (never invent order status, delivery dates, refund amounts)
- Granular escalation reasoning with specific triggers
"""
import re
from typing import Dict, List, Any, Optional, Tuple

from app.ml.inference.inference_engine import inference_engine
from app.ml.context_service import context_service, MAX_CONTEXT_MESSAGES


# ─── Response Templates by Intent & Emotion ────────────────────────────────────

_EMOTION_TONES = {
    "Frustration": "I completely understand your frustration. ",
    "Anger": "I sincerely apologise for this experience. ",
    "Disappointment": "I'm sorry this did not meet your expectations. ",
    "Confused": "Let me clarify this for you step by step. ",
    "Joy": "That's wonderful to hear! ",
    "Satisfaction": "Thank you for sharing your feedback! ",
    "Neutral": "",
}

_SAFE_FALLBACK = (
    "I can assist with your retail inquiry. Please provide your order or product details."
)

_ESCALATION_KEYWORDS = [
    "human", "agent", "real person", "speak to human", "manager", "supervisor",
    "legal action", "lawsuit", "police", "stolen", "fraud", "scam",
    "nobody is helping", "worst ever", "horrible", "unacceptable", "frustrating"
]


def _build_safe_response(
    intent: str,
    sentiment: str,
    emotion: str,
    issue: Optional[str],
    message: str,
    should_escalate: bool,
) -> str:
    """Build empathetic response ensuring safety (no fake order dates or tracking numbers)."""
    tone_prefix = _EMOTION_TONES.get(emotion, _EMOTION_TONES.get(sentiment, ""))
    msg_lower = message.lower()

    # Resolution confirmation
    if any(kw in msg_lower for kw in ["thank you", "thanks", "resolved", "fixed", "all good"]):
        return (
            "You're very welcome! Is there anything else I can assist you with today?"
        )

    # Specific retail issue responses
    if issue == "delivery_delay" or intent == "Order Tracking":
        if should_escalate:
            return (
                f"{tone_prefix}I see that your delivery has been delayed. "
                "I am escalating this to our logistics specialist team to investigate your shipment status immediately."
            )
        return (
            f"{tone_prefix}I can help check your delivery status. "
            "Please provide your order number (e.g., #45821) so I can query live carrier tracking data."
        )

    if issue == "refund_problem" or intent == "Refund / Return":
        if should_escalate:
            return (
                f"{tone_prefix}I apologize for the delay with your refund. "
                "I am raising a priority escalation to our finance team to ensure your refund is processed promptly."
            )
        return (
            f"{tone_prefix}Under TCS Retail policy, refunds process within 3-5 business days upon carrier scan. "
            "Please provide your order or transaction number to trace refund status."
        )

    if issue in ("product_quality", "damaged_product"):
        if should_escalate:
            return (
                f"{tone_prefix}I am deeply sorry that your item arrived damaged. "
                "I'm escalating this to our quality team to issue a replacement or return."
            )
        return (
            f"{tone_prefix}I can help process a replacement or return. "
            "Could you share your order number and product model?"
        )

    if issue == "customer_service":
        return (
            f"{tone_prefix}I apologize for the inconvenience you've experienced with our support. "
            "I'm escalating your case directly to a senior customer experience manager right now."
        )

    # General intent responses
    if intent == "Praise" or sentiment == "Positive":
        return (
            f"{tone_prefix}We really appreciate your kind words! Have a fantastic day!"
        )

    if intent == "Complaint" or sentiment == "Negative":
        if should_escalate:
            return (
                f"{tone_prefix}I understand how important this issue is. "
                "Because your experience hasn't been satisfactory, I am referring your case to a human support supervisor."
            )
        return (
            f"{tone_prefix}I can assist with your issue. "
            "Please share a few more details or your order number so I can help."
        )

    # Default neutral helpful response
    return (
        "How can I best assist you with your purchase, order, or service today?"
    )


def _evaluate_escalation(
    sentiment: str,
    sentiment_score: float,
    intent: str,
    emotion: str,
    issue: Optional[str],
    message: str,
    history: List[Dict[str, Any]],
    prev_escalation_score: float = 0.0,
) -> Tuple[bool, float, str, List[str]]:
    """
    Granular escalation assessment returning (should_escalate, score, severity, reasons).
    """
    reasons = []
    score = prev_escalation_score
    msg_lower = message.lower()

    # 1. Explicit human request or critical language
    if any(kw in msg_lower for kw in ["human", "agent", "real person", "manager", "supervisor", "speak to human"]):
        score += 0.50
        reasons.append("Customer explicitly requested human agent assistance")
    elif any(kw in msg_lower for kw in ["nobody is helping", "frustrating", "frustration", "worst", "horrible", "unacceptable"]):
        score += 0.40
        reasons.append("Customer expressed severe dissatisfaction with service")

    # 2. Strong negative sentiment
    if sentiment_score < -0.65:
        score += 0.30
        reasons.append(f"Strong negative sentiment detected (score: {sentiment_score:.2f})")

    # 3. Emotion / Intent triggers
    if emotion in ("Anger", "Frustration") and intent in ("Complaint", "Order Tracking", "Refund / Return"):
        score += 0.25
        reasons.append(f"High-friction emotion ({emotion}) on {intent}")

    # 4. Repeated negative messages
    neg_turns = [
        h for h in history[-MAX_CONTEXT_MESSAGES:]
        if h.get("sender") == "user" and (h.get("sentiment_score") or 0.0) < -0.30
    ]
    if len(neg_turns) >= 2:
        score += 0.25
        reasons.append(f"Persistent negative sentiment ({len(neg_turns)} negative turns in session)")

    # 5. Delivery or refund issue combined with frustration
    if issue in ("delivery_delay", "refund_problem", "customer_service") and sentiment == "Negative":
        score += 0.20
        reasons.append(f"Unresolved critical issue category: {issue}")

    score = min(round(score, 2), 1.0)
    should_escalate = score >= 0.50

    severity = "high" if score >= 0.75 or "Anger" in emotion else "medium" if score >= 0.50 else "low"

    return should_escalate, score, severity, reasons


class EmphaticChatEngine:
    """Phase 2 Empathetic Chatbot Engine with OpenAI & Grok LLM integration."""

    def _build_rule_based_response(
        self,
        message: str,
        sentiment: str,
        emotion: str,
        intent: str,
        issue: Optional[str] = None,
        customer_name: str = "Customer",
        should_escalate: bool = False,
    ) -> str:
        """Build safe rule-based fallback response."""
        resp = _build_safe_response(intent, sentiment, emotion, issue, message, should_escalate)
        if customer_name and customer_name != "Customer" and not resp.startswith("Hello"):
            resp = f"Hello {customer_name}! " + resp
        return resp

    def process_user_message(self, message: str) -> Dict[str, Any]:
        """Backward-compatible helper for single message processing."""
        return self.process(message=message, history=[])

    def process(
        self,
        message: str,
        history: List[Dict[str, Any]],
        session_state: str = "NEW",
        session_escalation_score: float = 0.0,
        preferred_provider: str = "auto",
        customer_name: str = "Customer",
    ) -> Dict[str, Any]:
        """
        Process user message with full context window and produce structured Phase 2 payload.
        """
        from app.ml.llm_service import llm_service

        # Context window extraction (MAX_CONTEXT_MESSAGES = 10)
        recent_history = context_service.extract_recent_context(history)

        # Context enrichment for inference
        user_texts = [
            h.get("text") or h.get("message") or ""
            for h in recent_history[-3:]
            if h.get("sender") == "user"
        ]
        enriched_input = " ".join(user_texts + [message]).strip()

        # ML Inference
        if inference_engine.is_loaded:
            prediction = inference_engine.predict(enriched_input)
        else:
            prediction = {
                "sentiment": "Neutral", "sentiment_score": 0.0, "confidence": 0.85,
                "intent": "General Inquiry", "emotion": "Neutral", "aspect": "General Experience",
            }

        sentiment = prediction["sentiment"]
        sentiment_score = round(float(prediction["sentiment_score"]), 4)
        confidence = round(float(prediction.get("confidence", 0.85)), 4)
        intent = prediction["intent"]
        emotion = prediction["emotion"]

        # Detect Issue
        issue_info = context_service.detect_issue(message, recent_history)
        issue = issue_info["issue"] if issue_info else None

        # Sentiment shift calculation
        sentiment_change, sentiment_dir, shift_alert = context_service.analyze_sentiment_shift(
            sentiment, sentiment_score, history
        )

        # Escalation check
        should_escalate, esc_score, severity, reasons = _evaluate_escalation(
            sentiment, sentiment_score, intent, emotion, issue, message, history, session_escalation_score
        )

        # Rule-based fallback safe response
        fallback_response = _build_safe_response(intent, sentiment, emotion, issue, message, should_escalate)

        # Generate response using OpenAI / Grok LLM Service or fallback
        assistant_response, llm_provider_used, llm_status_details = llm_service.generate_response(
            message=message,
            history=history,
            sentiment=sentiment,
            emotion=emotion,
            intent=intent,
            issue=issue,
            fallback_template_response=fallback_response,
            preferred_provider=preferred_provider,
            customer_name=customer_name,
        )

        # State transition
        is_escalated = session_state in ("ESCALATED", "Escalated")
        history_len = len([h for h in history if h.get("sender") == "user"]) + 1
        new_state = context_service.determine_conversation_state(
            session_state, message, sentiment, should_escalate, is_escalated, bool(issue), history_len
        )

        # Previous sentiment lookup
        user_msgs = [h for h in history if h.get("sender") == "user"]
        prev_sentiment = user_msgs[-1].get("sentiment", "Neutral") if user_msgs else "Neutral"

        return {
            # Backward-compatible fields
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "confidence": confidence,
            "intent": intent,
            "emotion": emotion,
            "issue": issue,
            "empathetic_response": assistant_response,
            "assistant_response": assistant_response,
            "triggered_escalation": should_escalate,
            "escalation_score": esc_score,
            "escalation_reason": "; ".join(reasons) if reasons else "Normal conversation flow",
            "sentiment_trajectory": "Declining" if sentiment_dir == "worsened" else "Improving" if sentiment_dir == "improved" else "Stable",
            "llm_provider": llm_provider_used,
            "llm_status": llm_status_details,
            # Phase 2 Structured blocks
            "analysis": {
                "sentiment": sentiment,
                "confidence": confidence,
                "intent": intent,
                "emotion": emotion,
                "issue": issue or "General Query",
                "llm_provider": llm_provider_used,
                "llm_status": llm_status_details,
            },
            "context": {
                "previous_sentiment": prev_sentiment,
                "current_sentiment": sentiment,
                "sentiment_change": sentiment_change,
                "sentiment_direction": sentiment_dir,
                "conversation_state": new_state,
                "shift_alert": shift_alert,
            },
            "escalation": {
                "should_escalate": should_escalate,
                "score": esc_score,
                "severity": severity,
                "reasons": reasons,
            },
        }



empathetic_chat_engine = EmphaticChatEngine()
EmpatheticChatEngine = EmphaticChatEngine

