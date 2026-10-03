"""
Behavioral tests for the Interaction Router and AI Orchestrator pipeline.

Tests assert ACTUAL response routing, not just that pytest passes.
These validate that the correct interaction_mode is selected and that
retail complaint responses NEVER appear for general chat messages.
"""
import pytest
import sys
import os

# Ensure backend module path is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ml.interaction_router import interaction_router, get_general_chat_fallback


# ─── Interaction Router Routing Tests ─────────────────────────────────────────

class TestInteractionRouterGeneral:
    """Messages that MUST classify as GENERAL_CHAT."""

    GENERAL_CHAT_MESSAGES = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "how are you",
        "introduce yourself",
        "introduce ur self",
        "tell me about yourself",
        "who are you",
        "what is your name",
        "what can you do",
        "who created you",
        "tell me a joke",
        "explain artificial intelligence",
        "explain machine learning",
        "what is machine learning",
        "thank you",
        "thanks",
        "bye",
    ]

    @pytest.mark.parametrize("message", GENERAL_CHAT_MESSAGES)
    def test_general_chat_routing(self, message):
        result = interaction_router.classify(message)
        assert result["mode"] == "GENERAL_CHAT", (
            f"ROUTING FAILURE: '{message}' classified as {result['mode']} instead of GENERAL_CHAT"
        )
        assert result["is_general_chat"] is True, (
            f"is_general_chat should be True for: '{message}'"
        )

    @pytest.mark.parametrize("message", GENERAL_CHAT_MESSAGES)
    def test_general_chat_fallback_never_contains_retail_apology(self, message):
        route = interaction_router.classify(message)
        fallback = get_general_chat_fallback(route["category"], message)

        # These phrases must NEVER appear in a GENERAL_CHAT fallback response
        retail_phrases = [
            "Thank you for contacting TCS Retail Support",
            "I'm sorry you're facing this problem",
            "Please give me a few more details so I can assist you",
            "direct you to the right department",
            "order number",
            "order or product details",
            "retail inquiry",
        ]
        for phrase in retail_phrases:
            assert phrase.lower() not in fallback.lower(), (
                f"RETAIL PHRASE found in GENERAL_CHAT fallback!\n"
                f"  Message: '{message}'\n"
                f"  Phrase: '{phrase}'\n"
                f"  Fallback: '{fallback}'"
            )

        # Fallback must not be empty
        assert fallback and fallback.strip(), f"Empty fallback for: '{message}'"


class TestInteractionRouterRetail:
    """Messages that MUST classify as RETAIL_SUPPORT."""

    RETAIL_MESSAGES = [
        ("my order is late", "RETAIL_SUPPORT"),
        ("my package hasn't arrived", "RETAIL_SUPPORT"),
        ("I want a refund", "RETAIL_SUPPORT"),
        ("the product is broken", "RETAIL_SUPPORT"),
        ("I want to return this item", "RETAIL_SUPPORT"),
        ("I was charged twice", "RETAIL_SUPPORT"),
        ("my delivery is delayed", "RETAIL_SUPPORT"),
    ]

    DATA_REQUEST_MESSAGES = [
        "where is order #45821",
        "track order 12345",
        "my order number is 99001",
    ]

    ESCALATION_MESSAGES = [
        "nobody is helping me",
        "I want to speak to a manager",
        "I need a real person",
    ]

    @pytest.mark.parametrize("message,expected_mode", RETAIL_MESSAGES)
    def test_retail_support_routing(self, message, expected_mode):
        result = interaction_router.classify(message)
        assert result["mode"] == expected_mode, (
            f"ROUTING FAILURE: '{message}' classified as {result['mode']} instead of {expected_mode}"
        )
        assert result["is_general_chat"] is False

    @pytest.mark.parametrize("message", DATA_REQUEST_MESSAGES)
    def test_retail_data_request_routing(self, message):
        result = interaction_router.classify(message)
        assert result["mode"] == "RETAIL_DATA_REQUEST", (
            f"ROUTING FAILURE: '{message}' classified as {result['mode']} instead of RETAIL_DATA_REQUEST"
        )
        assert result["is_general_chat"] is False

    @pytest.mark.parametrize("message", ESCALATION_MESSAGES)
    def test_escalation_routing(self, message):
        result = interaction_router.classify(message)
        # Escalation messages can be ESCALATION or RETAIL_SUPPORT (both are non-general)
        assert result["is_general_chat"] is False, (
            f"Escalation message incorrectly classified as GENERAL_CHAT: '{message}'"
        )


class TestGeneralChatFallbackQuality:
    """The general fallback responses must be appropriate for general chat."""

    def test_greeting_fallback(self):
        fb = get_general_chat_fallback("greeting", "hi")
        assert "hi" in fb.lower() or "hello" in fb.lower() or "help" in fb.lower()

    def test_introduction_fallback(self):
        fb = get_general_chat_fallback("introduction", "introduce yourself")
        lower = fb.lower()
        # Must contain identity/capability information
        assert any(word in lower for word in ["retailai", "ai", "assistant", "help", "platform"])

    def test_capability_fallback(self):
        fb = get_general_chat_fallback("capability", "what can you do")
        lower = fb.lower()
        assert any(word in lower for word in ["help", "can", "support", "order", "sentiment"])

    def test_joke_fallback(self):
        fb = get_general_chat_fallback("general_qa", "tell me a joke")
        assert fb and len(fb) > 10

    def test_machine_learning_fallback(self):
        fb = get_general_chat_fallback("general_qa", "explain machine learning")
        lower = fb.lower()
        assert "machine learning" in lower or "ai" in lower or "algorithm" in lower


class TestOrchestratorImport:
    """Verify the orchestrator imports the interaction router correctly."""

    def test_orchestrator_imports_interaction_router(self):
        """Verifies the new orchestrator correctly imports and uses interaction_router."""
        import inspect
        import app.ml.ai_orchestrator as orch_module
        source = inspect.getsource(orch_module)
        assert "interaction_router" in source, (
            "CRITICAL: ai_orchestrator.py must import and use interaction_router!"
        )
        assert "_handle_general_chat" in source, (
            "CRITICAL: ai_orchestrator.py must have _handle_general_chat handler!"
        )
        assert "_handle_retail_support" in source, (
            "CRITICAL: ai_orchestrator.py must have _handle_retail_support handler!"
        )
        assert "generate_general_response" in source, (
            "CRITICAL: ai_orchestrator.py must call generate_general_response for general chat!"
        )

    def test_general_chat_returns_neutral_sentiment(self):
        """General chat orchestrate() must return Neutral sentiment, not retail ML values."""
        from unittest.mock import patch, MagicMock
        from app.ml.ai_orchestrator import ai_orchestrator

        # Mock the LLM to return a simple response
        with patch("app.ml.ai_orchestrator.llm_service") as mock_llm:
            mock_llm.generate_general_response.return_value = (
                "Hi! How can I help you?", "MockLLM", "Success"
            )
            result = ai_orchestrator.orchestrate(
                message="hi",
                history=[],
                session_state="NEW",
            )

        assert result["sentiment"] == "Neutral", (
            f"FAIL: 'hi' must have Neutral sentiment, got {result['sentiment']}"
        )
        assert result["intent"] == "General Conversation", (
            f"FAIL: 'hi' must have General Conversation intent, got {result['intent']}"
        )
        assert result["interaction_mode"] == "GENERAL_CHAT", (
            f"FAIL: 'hi' must have GENERAL_CHAT mode, got {result['interaction_mode']}"
        )
        assert result["escalation"]["should_escalate"] is False, (
            f"FAIL: 'hi' must not trigger escalation"
        )
        # The response must NOT contain retail apology
        response_lower = result["response"].lower()
        assert "thank you for contacting tcs retail support" not in response_lower
        assert "i'm sorry you're facing this problem" not in response_lower

    def test_retail_message_runs_ml_pipeline(self):
        """Retail support messages must have mode RETAIL_SUPPORT."""
        from unittest.mock import patch
        from app.ml.ai_orchestrator import ai_orchestrator

        with patch("app.ml.ai_orchestrator.llm_service") as mock_llm, \
             patch("app.ml.ai_orchestrator.inference_engine") as mock_inf, \
             patch("app.ml.ai_orchestrator.entity_extractor") as mock_ent, \
             patch("app.ml.ai_orchestrator.knowledge_base") as mock_kb, \
             patch("app.ml.ai_orchestrator.execute_tools_for_request") as mock_tools, \
             patch("app.ml.ai_orchestrator.empathetic_chat_engine") as mock_emp:

            # Setup mocks
            mock_inf.predict_sentiment.return_value = {
                "sentiment": "Negative", "sentiment_score": -0.7, "confidence": 0.9
            }
            mock_inf.predict_intent.return_value = "Order Tracking"
            mock_inf.predict_emotion.return_value = "Frustration"
            mock_ent.extract.return_value = {"issue": "delivery_delay"}
            mock_kb.build_rag_prompt_section.return_value = ("", [])
            mock_tools.return_value = ([], "")
            mock_emp._build_rule_based_response.return_value = "I can help with that."
            mock_llm.generate_response.return_value = (
                "I can help check your delivery.", "MockLLM", "Success"
            )

            result = ai_orchestrator.orchestrate(
                message="my order is late",
                history=[],
                session_state="NEW",
            )

        assert result["interaction_mode"] == "RETAIL_SUPPORT", (
            f"FAIL: 'my order is late' must be RETAIL_SUPPORT, got {result['interaction_mode']}"
        )
        assert result["sentiment"] == "Negative", (
            f"FAIL: late order should have Negative sentiment"
        )
