"""LLM Provider Factory for dynamic runtime routing between Ollama, Claude, and OpenAI."""

import logging
from typing import Optional
from app.config import settings
from app.providers.base import BaseLLMProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import ClaudeProvider, OpenAIProvider, GeminiProvider

logger = logging.getLogger("lenny_assistant.providers.factory")


class LLMProviderFactory:
    @staticmethod
    def get_provider(
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> BaseLLMProvider:
        selected_provider = (provider or settings.DEFAULT_LLM_PROVIDER).lower().strip()

        if selected_provider in ["claude", "anthropic"]:
            return ClaudeProvider(api_key=api_key, model=model)
        elif selected_provider in ["openai", "gpt"]:
            return OpenAIProvider(api_key=api_key, model=model)
        elif selected_provider in ["gemini", "google"]:
            return GeminiProvider(api_key=api_key, model=model)
        elif selected_provider == "ollama":
            return OllamaProvider(model=model)
        else:
            logger.warning(f"Unknown provider '{selected_provider}'. Falling back to Ollama.")
            return OllamaProvider(model=model)
