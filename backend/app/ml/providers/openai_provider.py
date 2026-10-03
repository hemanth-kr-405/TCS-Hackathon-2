"""
OpenAI LLM Provider Driver.
"""
import json
import logging
import httpx
from typing import Dict, List, Optional, Tuple, Iterator
from app.config import settings
from app.ml.providers.base import LLMProvider

logger = logging.getLogger(__name__)

OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL or "gpt-4o-mini"

    def name(self) -> str:
        return f"OpenAI ({self.model})"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 350
    ) -> Tuple[Optional[str], Optional[str]]:
        if not self.is_configured():
            return None, "OpenAI API Key not configured"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                res = client.post(OPENAI_ENDPOINT, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    return content, None
                elif res.status_code == 429:
                    return None, "OpenAI Quota/Credit limit reached (429)"
                else:
                    return None, f"OpenAI Error ({res.status_code}): {res.text[:120]}"
        except Exception as e:
            logger.warning(f"OpenAI Driver Exception: {e}")
            return None, f"OpenAI Connection Error: {str(e)}"

    def stream_generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 350
    ) -> Iterator[str]:
        if not self.is_configured():
            yield "[OpenAI Key Not Configured]"
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                with client.stream("POST", OPENAI_ENDPOINT, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        yield f"[OpenAI Error {response.status_code}]"
                        return
                    for line in response.iter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue
        except Exception as e:
            logger.warning(f"OpenAI Streaming Exception: {e}")
            yield f"[OpenAI Stream Error: {str(e)}]"
