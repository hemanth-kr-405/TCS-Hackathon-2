"""
LLM Service Integration — OpenAI & xAI Grok API Support.

Provides seamless integration with OpenAI API and xAI Grok API for generating
empathetic retail customer support chat responses with automatic fallback logic.
"""
import logging
import httpx
from typing import Dict, List, Any, Optional, Tuple
from app.config import settings

logger = logging.getLogger(__name__)

OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"
GROK_ENDPOINT = "https://api.x.ai/v1/chat/completions"


class LLMService:
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.grok_key = settings.GROK_API_KEY
        self.openai_model = settings.OPENAI_MODEL
        self.grok_model = settings.GROK_MODEL

    def get_status(self) -> Dict[str, Any]:
        """Return configuration and key availability status for LLM providers."""
        return {
            "openai_configured": bool(settings.OPENAI_API_KEY),
            "grok_configured": bool(settings.GROK_API_KEY),
            "default_provider": settings.DEFAULT_LLM_PROVIDER,
            "openai_model": self.openai_model,
            "grok_model": self.grok_model,
        }

    def _build_system_prompt(
        self,
        sentiment: str,
        emotion: str,
        intent: str,
        issue: Optional[str],
        customer_name: str = "Customer",
    ) -> str:
        return (
            f"You are the official TCS Retail AI Customer Support Assistant.\n"
            f"Customer Name: {customer_name}\n"
            f"Detected Customer Emotion: {emotion}\n"
            f"Detected Customer Sentiment: {sentiment}\n"
            f"Customer Intent: {intent}\n"
            f"Specific Retail Issue: {issue or 'General Query'}\n\n"
            f"GUIDELINES:\n"
            f"1. Respond in a warm, highly empathetic, professional tone tailored to their emotion ({emotion}).\n"
            f"2. Keep response concise (2-4 sentences max).\n"
            f"3. STRICT SAFETY RULE: Do NOT invent fake order IDs, tracking numbers, or refund dates unless provided in context.\n"
            f"4. If customer is frustrated or angry, directly apologize and reassure them that TCS support is resolving their issue.\n"
            f"5. Maintain a helpful customer-centric attitude."
        )

    def _call_openai(
        self,
        messages: List[Dict[str, str]],
    ) -> Tuple[Optional[str], Optional[str]]:
        api_key = settings.OPENAI_API_KEY or self.openai_key
        if not api_key:
            return None, "OpenAI API Key not configured"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 250,
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(OPENAI_ENDPOINT, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    return content, None
                elif res.status_code == 429:
                    return None, "OpenAI Quota/Credit limit reached (429)"
                else:
                    return None, f"OpenAI API Error ({res.status_code}): {res.text[:100]}"
        except Exception as e:
            logger.warning(f"OpenAI API Call Exception: {e}")
            return None, f"OpenAI Connection Error: {str(e)}"

    def _call_grok(
        self,
        messages: List[Dict[str, str]],
    ) -> Tuple[Optional[str], Optional[str]]:
        api_key = settings.GROK_API_KEY or self.grok_key
        if not api_key:
            return None, "Grok API Key not configured"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        # Try primary model grok-2-latest then grok-beta
        models_to_try = [self.grok_model, "grok-beta", "grok-2"]
        last_error = "Unknown Grok error"

        for mod in models_to_try:
            payload = {
                "model": mod,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 250,
            }
            try:
                with httpx.Client(timeout=8.0) as client:
                    res = client.post(GROK_ENDPOINT, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        content = data["choices"][0]["message"]["content"].strip()
                        return content, None
                    elif res.status_code in (403, 429):
                        last_error = f"Grok Credit Limit / Permission Denied ({res.status_code})"
                        break
                    else:
                        last_error = f"Grok Error ({res.status_code}): {res.text[:100]}"
            except Exception as e:
                logger.warning(f"Grok API Call Exception for model {mod}: {e}")
                last_error = f"Grok Connection Error: {str(e)}"

        return None, last_error

    def generate_response(
        self,
        message: str,
        history: List[Dict[str, Any]],
        sentiment: str,
        emotion: str,
        intent: str,
        issue: Optional[str],
        fallback_template_response: str,
        preferred_provider: str = "auto",
        customer_name: str = "Customer",
    ) -> Tuple[str, str, str]:
        """
        Generates response using OpenAI or xAI Grok API with automatic fallback.

        Returns:
            Tuple[response_text, provider_used, status_details]
        """
        system_prompt = self._build_system_prompt(sentiment, emotion, intent, issue, customer_name)

        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-4:]:
            sender = h.get("sender")
            text = h.get("text") or h.get("message") or ""
            if text:
                role = "user" if sender == "user" else "assistant"
                messages.append({"role": role, "content": text})
        messages.append({"role": "user", "content": message})

        prov = preferred_provider.lower() if preferred_provider else "auto"

        # Direct OpenAI request
        if prov in ("openai", "gpt"):
            resp, err = self._call_openai(messages)
            if resp:
                return resp, f"OpenAI ({self.openai_model})", "Success"
            return (
                fallback_template_response,
                "Empathetic Engine (Fallback)",
                f"OpenAI requested but failed: {err}",
            )

        # Direct Grok request
        if prov in ("grok", "xai"):
            resp, err = self._call_grok(messages)
            if resp:
                return resp, f"xAI Grok ({self.grok_model})", "Success"
            return (
                fallback_template_response,
                "Empathetic Engine (Fallback)",
                f"Grok requested but failed: {err}",
            )

        # Auto Mode: OpenAI -> Grok -> Template Engine
        # 1. Try OpenAI
        if settings.OPENAI_API_KEY:
            resp, err_openai = self._call_openai(messages)
            if resp:
                return resp, f"OpenAI ({self.openai_model})", "Success"
        else:
            err_openai = "OpenAI key missing"

        # 2. Try Grok
        if settings.GROK_API_KEY:
            resp, err_grok = self._call_grok(messages)
            if resp:
                return resp, f"xAI Grok ({self.grok_model})", "Success"
        else:
            err_grok = "Grok key missing"

        # 3. Fallback to Empathetic Rule Engine
        status_msg = f"Auto fallback active. OpenAI: {err_openai} | Grok: {err_grok}"
        return fallback_template_response, "Empathetic Engine (Fallback)", status_msg

    def generate_general_response(
        self,
        message: str,
        history: List[Dict[str, Any]],
        fallback_template_response: str,
        preferred_provider: str = "auto",
        customer_name: str = "Customer",
    ) -> Tuple[str, str, str]:
        """Generates natural response for GENERAL_CHAT (greetings, intros, general Q&A) without retail complaint framing."""
        system_prompt = (
            "You are RetailAI, an intelligent conversational AI assistant for the TCS Retail Customer Sentiment Intelligence Platform.\n"
            f"Customer Name: {customer_name}\n"
            "GUIDELINES:\n"
            "1. Respond naturally, helpfully, and politely (2-3 sentences max) to general conversation, greetings, introductions, jokes, or general knowledge questions.\n"
            "2. If asked who you are or what you can do, explain that you are RetailAI and can answer general questions, help with retail support (orders, tracking, refunds, returns, policies), and analyze customer sentiment when support is needed.\n"
            "3. Do NOT invent customer support complaints, apologies, or order IDs for general conversation."
        )

        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-4:]:
            sender = h.get("sender")
            text = h.get("text") or h.get("message") or ""
            if text:
                role = "user" if sender == "user" else "assistant"
                messages.append({"role": role, "content": text})
        messages.append({"role": "user", "content": message})

        prov = preferred_provider.lower() if preferred_provider else "auto"

        if prov in ("openai", "gpt"):
            resp, err = self._call_openai(messages)
            if resp:
                return resp, f"OpenAI ({self.openai_model})", "Success"
            logger.info(f"LLM PROVIDER ERROR | provider=openai | reason={err}")
            return fallback_template_response, "Empathetic Engine (General Fallback)", f"OpenAI failed: {err}"

        if prov in ("grok", "xai"):
            resp, err = self._call_grok(messages)
            if resp:
                return resp, f"xAI Grok ({self.grok_model})", "Success"
            logger.info(f"LLM PROVIDER ERROR | provider=grok | reason={err}")
            return fallback_template_response, "Empathetic Engine (General Fallback)", f"Grok failed: {err}"

        # Auto mode: OpenAI -> Grok -> General Fallback
        if settings.OPENAI_API_KEY:
            resp, err_openai = self._call_openai(messages)
            if resp:
                return resp, f"OpenAI ({self.openai_model})", "Success"
            logger.info(f"LLM PROVIDER ERROR | provider=openai | reason={err_openai}")
        else:
            err_openai = "OpenAI key missing"

        if settings.GROK_API_KEY:
            resp, err_grok = self._call_grok(messages)
            if resp:
                return resp, f"xAI Grok ({self.grok_model})", "Success"
            logger.info(f"LLM PROVIDER ERROR | provider=grok | reason={err_grok}")
        else:
            err_grok = "Grok key missing"

        status_msg = f"Auto fallback active. OpenAI: {err_openai} | Grok: {err_grok}"
        return fallback_template_response, "Empathetic Engine (General Fallback)", status_msg


llm_service = LLMService()
