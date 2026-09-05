"""Abstract base class for LLM providers (Ollama, Anthropic, OpenAI)."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        """Stream generated tokens from the LLM provider."""
        pass

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> str:
        """Non-streaming generation returning the full response string."""
        tokens = []
        async for token in self.generate_response(messages, system_prompt, temperature):
            tokens.append(token)
        return "".join(tokens)
