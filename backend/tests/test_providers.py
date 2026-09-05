"""Automated tests for LLM provider routing, skills, and fallback behaviors."""

import pytest
from app.providers.factory import LLMProviderFactory
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import ClaudeProvider, OpenAIProvider
from app.skills.ship30_writer import build_ship30_prompt, SHIP_30_SYSTEM_PROMPT
from app.skills.artifact_generator import extract_artifacts


def test_provider_factory_routing():
    ollama = LLMProviderFactory.get_provider("ollama", model="llama3.1:8b")
    assert isinstance(ollama, OllamaProvider)
    assert ollama.model == "llama3.1:8b"

    claude = LLMProviderFactory.get_provider("claude", model="claude-3-5-sonnet-20241022")
    assert isinstance(claude, ClaudeProvider)
    assert claude.model == "claude-3-5-sonnet-20241022"

    openai = LLMProviderFactory.get_provider("openai", model="gpt-4o")
    assert isinstance(openai, OpenAIProvider)
    assert openai.model == "gpt-4o"

    # Unknown falls back to Ollama
    fallback = LLMProviderFactory.get_provider("unknown-ai-model")
    assert isinstance(fallback, OllamaProvider)


@pytest.mark.asyncio
async def test_cloud_providers_missing_key_graceful_error():
    claude_no_key = ClaudeProvider(api_key="")
    tokens = [t async for t in claude_no_key.generate_response([], "system")]
    assert any("ANTHROPIC_API_KEY is not configured" in t for t in tokens)

    openai_no_key = OpenAIProvider(api_key="")
    tokens = [t async for t in openai_no_key.generate_response([], "system")]
    assert any("OPENAI_API_KEY is not configured" in t for t in tokens)


def test_ship30_prompt_construction():
    mock_chunks = [
        {
            "slug": "adam-fishman",
            "episode": "How to build a high-performing growth team",
            "guest": "Adam Fishman",
            "timestamp": "00:12:30",
            "score": 0.85,
            "text": "Onboarding is the only part of your product that 100% of users see.",
        }
    ]
    prompt = build_ship30_prompt("Write about onboarding", mock_chunks)
    assert "Adam Fishman" in prompt
    assert "00:12:30" in prompt
    assert "Onboarding is the only part" in prompt
    assert "1,250-word" in prompt or "1250" in prompt
    assert "HOOK" in SHIP_30_SYSTEM_PROMPT.upper()
    assert "SKIMMABILITY" in SHIP_30_SYSTEM_PROMPT.upper()


def test_artifact_extraction_and_cleaning():
    sample_llm_output = (
        "Here is the interactive simulator you requested.\n\n"
        '<artifact identifier="growth-calc" type="html" title="Growth Loop Calculator">\n'
        "<!DOCTYPE html><html><body><h1>Calculator</h1></body></html>\n"
        "</artifact>\n\n"
        "Let me know if you want to tweak any formulas!"
    )

    clean_text, artifacts = extract_artifacts(sample_llm_output)

    assert len(artifacts) == 1
    art = artifacts[0]
    assert art["identifier"] == "growth-calc"
    assert art["artifact_type"] == "html"
    assert art["title"] == "Growth Loop Calculator"
    assert "<!DOCTYPE html>" in art["content"]

    # Raw artifact tags should be cleanly replaced in conversational text
    assert "<artifact" not in clean_text
    assert "Growth Loop Calculator" in clean_text
    assert "Let me know if you want to tweak any formulas!" in clean_text
