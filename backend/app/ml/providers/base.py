"""
Abstract LLM Provider Base Class.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Iterator


class LLMProvider(ABC):
    """Abstract base class for LLM completion drivers."""

    @abstractmethod
    def name(self) -> str:
        """Return provider identifier (e.g. 'OpenAI', 'xAI Grok')."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True if required API keys are configured."""
        pass

    @abstractmethod
    def generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 350
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate completion response synchronously.
        Returns Tuple[response_text, error_message].
        """
        pass

    @abstractmethod
    def stream_generate(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 350
    ) -> Iterator[str]:
        """
        Yield completion text chunks as they arrive from the provider.
        Yields text deltas.
        """
        pass
