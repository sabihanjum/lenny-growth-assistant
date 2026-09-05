"""Cloud LLM Providers: Anthropic Claude and OpenAI with streaming support."""

import json
import logging
from typing import AsyncGenerator, Dict, Any, List
import httpx
from app.config import settings
from app.providers.base import BaseLLMProvider

logger = logging.getLogger("lenny_assistant.providers.cloud")


class ClaudeProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or "claude-3-5-sonnet-20241022"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            yield "Error: ANTHROPIC_API_KEY is not configured. Please supply an API key in .env or switch to the local Ollama provider."
            return

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        # Convert messages format if needed (Anthropic expects role: user/assistant)
        anthropic_messages = []
        for m in messages:
            if m["role"] in ["user", "assistant"]:
                anthropic_messages.append({"role": m["role"], "content": m["content"]})

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": anthropic_messages,
            "temperature": temperature,
            "stream": True,
        }

        url = "https://api.anthropic.com/v1/messages"
        logger.info(f"Connecting to Anthropic Messages API using model '{self.model}'")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        err = await response.aread()
                        logger.error(f"Anthropic error {response.status_code}: {err.decode('utf-8')}")
                        yield f"Error from Anthropic ({response.status_code}): {err.decode('utf-8')}"
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            raw_data = line[6:].strip()
                            if raw_data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(raw_data)
                                event_type = chunk.get("type")
                                if event_type == "content_block_delta":
                                    text_val = chunk.get("delta", {}).get("text", "")
                                    if text_val:
                                        yield text_val
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Anthropic API exception: {e}")
            yield f"Error calling Anthropic API: {str(e)}"


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or "gpt-4o"

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        if not self.api_key:
            yield "Error: OPENAI_API_KEY is not configured. Please supply an API key in .env or switch to the local Ollama provider."
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        openai_messages = [{"role": "system", "content": system_prompt}] + messages

        payload = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            "stream": True,
        }

        url = "https://api.openai.com/v1/chat/completions"
        logger.info(f"Connecting to OpenAI Chat API using model '{self.model}'")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        err = await response.aread()
                        logger.error(f"OpenAI error {response.status_code}: {err.decode('utf-8')}")
                        yield f"Error from OpenAI ({response.status_code}): {err.decode('utf-8')}"
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            raw_data = line[6:].strip()
                            if raw_data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(raw_data)
                                choices = chunk.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"OpenAI API exception: {e}")
            yield f"Error calling OpenAI API: {str(e)}"
