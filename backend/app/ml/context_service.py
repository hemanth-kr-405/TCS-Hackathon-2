"""
Conversation Context Service — Phase 2 Context-Aware Intelligence for TCS Retail Platform.

Provides:
- Configurable MAX_CONTEXT_MESSAGES window (default 10)
- Context-aware product & intent history resolution
- Retail Issue Recognition (delivery_delay, refund_problem, damaged_product, etc.)
- Conversation State Machine (NEW -> ACTIVE -> ISSUE_IDENTIFIED -> RESOLUTION_IN_PROGRESS -> ESCALATION_RECOMMENDED -> ESCALATED -> RESOLVED -> CLOSED)
- Sentiment trajectory & shift analysis (improved, worsened, stable)
"""
import re
from typing import Dict, List, Any, Optional, Tuple

MAX_CONTEXT_MESSAGES = 10

# Supported Retail Issue Definitions
_ISSUE_PATTERNS = [
    {
        "issue": "delivery_delay",
        "category": "Shipping & Delivery",
        "severity": "High",
        "keywords": ["arrive", "arrived", "delay", "delayed", "late", "shipping", "delivery", "where is my", "order status", "three days ago", "days overdue", "transit"],
    },
    {
        "issue": "refund_problem",
        "category": "Billing & Refunds",
        "severity": "High",
        "keywords": ["refund", "money back", "return money", "charged twice", "reimbursement", "cash back", "chargeback"],
    },
    {
        "issue": "damaged_product",
        "category": "Electronics & Products",
        "severity": "High",
        "keywords": ["damaged", "broken", "scratched", "cracked", "shattered", "dented", "smashed"],
    },
    {
        "issue": "product_quality",
        "category": "Electronics & Products",
        "severity": "Medium",
        "keywords": ["battery", "draining", "quality", "poor", "faulty", "defective", "not working", "glitch", "stopped working", "hardware"],
    },
    {
        "issue": "payment_problem",
        "category": "Billing & Refunds",
        "severity": "High",
        "keywords": ["payment", "card", "billing", "invoice", "double charged", "payment failed", "checkout error"],
    },
    {
        "issue": "technical_problem",
        "category": "Customer Support",
        "severity": "Medium",
        "keywords": ["bug", "crash", "app error", "website down", "error code", "login error", "account locked"],
    },
    {
        "issue": "customer_service",
        "category": "Customer Support",
        "severity": "High",
        "keywords": ["nobody is helping", "unhelpful", "no response", "ignoring me", "worst service", "horrible support", "rude agent"],
    },
]

_RESOLUTION_KEYWORDS = ["thank you", "thanks", "resolved", "fixed", "all good", "solved", "working now", "perfect"]
_ESCALATION_KEYWORDS = ["human", "agent", "person", "manager", "supervisor", "nobody is helping", "frustrating", "terrible", "horrible", "lawsuit", "legal"]


class ConversationContextService:
    def __init__(self, max_context_messages: int = MAX_CONTEXT_MESSAGES):
        self.max_context_messages = max_context_messages

    def extract_recent_context(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Limit history to configurable MAX_CONTEXT_MESSAGES window."""
        return history[-self.max_context_messages:]

    def detect_issue(self, message: str, history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Identify retail issue based on current message and recent conversation context."""
        text_corpus = message.lower()
        # Include previous user messages for context enrichment
        for h in reversed(history[-4:]):
            if h.get("sender") == "user":
                text_corpus += " " + (h.get("text") or h.get("message") or "").lower()

        for pat in _ISSUE_PATTERNS:
            if any(kw in text_corpus for kw in pat["keywords"]):
                return {
                    "issue": pat["issue"],
                    "category": pat["category"],
                    "severity": pat["severity"],
                }
        return None

    def analyze_sentiment_shift(
        self,
        current_sentiment: str,
        current_score: float,
        history: List[Dict[str, Any]],
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Compare current sentiment score with previous user sentiment.
        Returns (sentiment_change, sentiment_direction, alert_message).
        sentiment_direction: 'improved' | 'worsened' | 'stable'
        """
        user_history = [
            h for h in history
            if h.get("sender") == "user" and h.get("sentiment_score") is not None
        ]
        if not user_history:
            return False, "stable", None

        prev_msg = user_history[-1]
        prev_score = float(prev_msg.get("sentiment_score", 0.0))
        prev_sentiment = prev_msg.get("sentiment", "Neutral")

        score_diff = current_score - prev_score

        # Meaningful shift thresholds
        if score_diff < -0.20 or (prev_sentiment in ("Positive", "Neutral") and current_sentiment == "Negative"):
            return True, "worsened", "Customer sentiment is worsening"

        if score_diff > 0.20 or (prev_sentiment == "Negative" and current_sentiment in ("Positive", "Neutral")):
            return True, "improved", "Customer sentiment has improved"

        return False, "stable", None

    def determine_conversation_state(
        self,
        current_state: str,
        current_message: str,
        sentiment: str,
        should_escalate: bool,
        is_escalated: bool,
        issue_detected: bool,
        history_length: int,
    ) -> str:
        """FSM to determine conversation state."""
        msg_lower = current_message.lower()

        if is_escalated or current_state == "ESCALATED":
            return "ESCALATED"

        if any(kw in msg_lower for kw in _RESOLUTION_KEYWORDS):
            return "RESOLVED"

        if should_escalate:
            return "ESCALATION_RECOMMENDED"

        if issue_detected:
            return "ISSUE_IDENTIFIED" if history_length <= 2 else "RESOLUTION_IN_PROGRESS"

        if history_length > 1:
            return "ACTIVE"

        return "NEW"


context_service = ConversationContextService()
