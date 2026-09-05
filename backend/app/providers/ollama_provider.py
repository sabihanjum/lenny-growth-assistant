"""Ollama Local LLM Provider implementation with streaming support."""

import json
import logging
from typing import AsyncGenerator, Dict, Any, List
import httpx
from app.config import settings
from app.providers.base import BaseLLMProvider

logger = logging.getLogger("lenny_assistant.providers.ollama")


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.DEFAULT_OLLAMA_MODEL

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_ctx": 8192,
            }
        }

        url = f"{self.base_url}/api/chat"
        logger.info(f"Connecting to Ollama at {url} using model '{self.model}'")

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        logger.error(f"Ollama error {response.status_code}: {error_text.decode('utf-8', errors='ignore')}")
                        yield f"Error: Ollama service returned HTTP {response.status_code}. Please verify the model '{self.model}' is installed (`ollama pull {self.model}`)."
                        return

                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                content = chunk.get("message", {}).get("content", "")
                                if content:
                                    yield content
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
        except httpx.ConnectError:
            msg = f"Cannot connect to Ollama at {self.base_url}. Please ensure Ollama is running (`ollama serve`)."
            logger.error(msg)
            yield f"Error: {msg}"
        except httpx.TimeoutException:
            msg = f"Ollama request timed out after 180s on model {self.model}."
            logger.error(msg)
            yield f"Error: {msg}"
        except Exception as e:
            logger.error(f"Unexpected Ollama exception: {e}")
            yield f"Error generating response from Ollama: {str(e)}"
