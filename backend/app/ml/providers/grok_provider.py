"""
xAI Grok LLM Provider Driver.
"""
import json
import logging
import httpx
from typing import Dict, List, Optional, Tuple, Iterator
from app.config import settings
from app.ml.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class GrokProvider(LLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or settings.XAI_API_KEY or settings.GROK_API_KEY
        self.model = model or settings.XAI_MODEL or settings.GROK_MODEL or "grok-2-latest"
        base = base_url or settings.XAI_BASE_URL or "https://api.x.ai"
        self.endpoint = f"{base.rstrip('/')}/v1/chat/completions"

    def name(self) -> str:
        return f"xAI Grok ({self.model})"

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 350
    ) -> Tuple[Optional[str], Optional[str]]:
        if not self.is_configured():
            return None, "xAI Grok API Key not configured"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        models_to_try = [self.model, "grok-2-latest", "grok-beta"]
        last_err = "Unknown Grok Error"

        for mod in models_to_try:
            payload = {
                "model": mod,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            try:
                with httpx.Client(timeout=10.0) as client:
                    res = client.post(self.endpoint, headers=headers, json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        content = data["choices"][0]["message"]["content"].strip()
                        return content, None
                    elif res.status_code in (403, 429):
                        last_err = f"Grok Credit Limit / Permission Denied ({res.status_code})"
                        break
                    else:
                        last_err = f"Grok Error ({res.status_code}): {res.text[:120]}"
            except Exception as e:
                logger.warning(f"Grok Driver Exception for model {mod}: {e}")
                last_err = f"Grok Connection Error: {str(e)}"

        return None, last_err

    def stream_generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 350
    ) -> Iterator[str]:
        if not self.is_configured():
            yield "[Grok Key Not Configured]"
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
                with client.stream("POST", self.endpoint, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        yield f"[Grok Error {response.status_code}]"
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
            logger.warning(f"Grok Streaming Exception: {e}")
            yield f"[Grok Stream Error: {str(e)}]"
