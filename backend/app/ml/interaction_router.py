"""
Interaction Router — First-Stage Classifier separating GENERAL_CHAT from RETAIL_SUPPORT.
"""
import re
from typing import Dict, Any, Tuple


class InteractionRouter:
    """Classifies incoming user messages into interaction modes BEFORE ML sentiment/intent processing."""

    GREETINGS = {
        "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
        "howdy", "how are you", "what's up", "greetings", "hey there", "hi there",
        "yo", "sup", "morning", "afternoon", "evening",
    }

    INTRO_KEYWORDS = [
        "introduce yourself", "introduce ur self", "who are you", "tell me about yourself",
        "what is your name", "who created you", "what are you", "what's your name",
        "tell me who you are", "identify yourself",
    ]

    CAPABILITY_KEYWORDS = [
        "what can you do", "how can you help", "what are your capabilities",
        "what do you do", "help me", "what can i ask you", "what functions",
    ]

    GENERAL_QA_KEYWORDS = [
        "tell me a joke", "explain artificial intelligence", "explain ai",
        "explain machine learning", "what is machine learning", "what is ai",
        "what year is it", "tell a joke", "say a joke", "make me laugh",
    ]

    COURTESY_KEYWORDS = [
        "thank you", "thanks", "thanks a lot", "thank you very much",
        "bye", "goodbye", "see you", "have a nice day", "ok", "cool", "awesome", "great",
    ]

    RETAIL_INDICATORS = [
        "order", "shipping", "delivery", "track", "tracking", "package", "parcel",
        "refund", "return", "exchange", "cancel", "cancellation", "product", "sku",
        "price", "cost", "warranty", "broken", "damaged", "defective", "charged",
        "billing", "payment", "invoice", "receipt", "laptop", "headphones", "glassware",
        "item", "store", "buy", "purchase", "item arrived", "shipment",
    ]

    ESCALATION_INDICATORS = [
        "human", "agent", "real person", "manager", "supervisor",
        "lawsuit", "legal action", "sue", "police", "stolen", "fraud",
        "scam", "nobody is helping", "worst service", "demand to speak",
    ]

    def classify(self, message: str) -> Dict[str, Any]:
        """Classifies message into interaction mode and determines if it is GENERAL_CHAT."""
        text = message.strip()
        lower = text.lower()
        clean = re.sub(r'[^a-z0-9\s#]', '', lower).strip()

        # 1. Check explicit escalation triggers first
        if any(kw in lower for kw in self.ESCALATION_INDICATORS):
            return {
                "mode": "ESCALATION",
                "category": "escalation",
                "is_general_chat": False,
            }

        # 2. Check for order IDs or specific retail indicators
        has_order_id = bool(re.search(r'#?\b\d{4,6}\b', lower))
        has_retail_indicator = any(kw in lower for kw in self.RETAIL_INDICATORS)

        if has_order_id:
            return {
                "mode": "RETAIL_DATA_REQUEST",
                "category": "order_data",
                "is_general_chat": False,
            }

        if any(kw in lower for kw in ["return policy", "refund policy", "warranty duration", "policy"]):
            return {
                "mode": "RETAIL_POLICY_QUERY",
                "category": "policy_query",
                "is_general_chat": False,
            }

        # 3. If strong retail keywords exist, route to RETAIL_SUPPORT
        if has_retail_indicator:
            return {
                "mode": "RETAIL_SUPPORT",
                "category": "retail_support",
                "is_general_chat": False,
            }

        # 4. Check GENERAL_CHAT patterns
        is_greeting = clean in self.GREETINGS or any(clean.startswith(g) for g in ["hi ", "hello ", "hey ", "hi!", "hello!"])
        is_intro = any(kw in lower for kw in self.INTRO_KEYWORDS)
        is_capability = any(kw in lower for kw in self.CAPABILITY_KEYWORDS)
        is_general_qa = any(kw in lower for kw in self.GENERAL_QA_KEYWORDS)
        is_courtesy = any(kw in lower for kw in self.COURTESY_KEYWORDS)

        if is_greeting or is_intro or is_capability or is_general_qa or is_courtesy or len(clean.split()) <= 3:
            sub_cat = (
                "greeting" if is_greeting else
                "introduction" if is_intro else
                "capability" if is_capability else
                "general_qa" if is_general_qa else
                "courtesy" if is_courtesy else "general_conversation"
            )
            return {
                "mode": "GENERAL_CHAT",
                "category": sub_cat,
                "is_general_chat": True,
            }

        # 5. Default fallback for non-retail queries
        return {
            "mode": "GENERAL_CHAT",
            "category": "general_conversation",
            "is_general_chat": True,
        }


def get_general_chat_fallback(category: str, message: str) -> str:
    """Provides natural local general conversational responses when LLMs are offline."""
    clean = message.lower().strip()
    if category == "greeting" or clean in ("hi", "hello", "hey", "hi!", "hello!"):
        return "Hi! 👋 How can I help you today?"
    if category == "introduction" or "introduce" in clean or "who are you" in clean:
        return (
            "Sure! I'm RetailAI, an AI-powered conversational assistant for the TCS Retail "
            "Customer Sentiment Intelligence Platform. I can answer general questions, help with "
            "retail support such as orders, returns and refunds, and analyze customer sentiment, "
            "intent, and emotion when support is needed."
        )
    if category == "capability" or "what can you do" in clean or "help" in clean:
        return (
            "I can help with general questions and retail support, including orders, returns, "
            "refunds, product issues, policies, and customer feedback. I can also analyze "
            "sentiment, intent, and emotion when a support conversation requires it."
        )
    if "joke" in clean:
        return "Why don't scientists trust atoms? Because they make up everything! 😄 How else can I help you today?"
    if "machine learning" in clean:
        return (
            "Machine learning is a branch of artificial intelligence where algorithms learn patterns from data "
            "to make predictions or decisions without explicit programming. In this platform, ML powers sentiment analysis, "
            "intent classification, and empathetic responses!"
        )
    if "artificial intelligence" in clean or "ai" in clean:
        return (
            "Artificial Intelligence (AI) enables computer systems to simulate human intelligence tasks "
            "such as natural language processing, visual perception, decision-making, and conversation."
        )
    if category == "courtesy" or "thank" in clean:
        return "You're very welcome! Let me know if there's anything else I can assist with."
    return "Hi! 👋 How can I help you today?"


interaction_router = InteractionRouter()
