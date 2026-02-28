"""
LLM Wrapper Skill - Unified interface for multiple LLM providers.

Purpose:
    Provides a single interface to call different LLM providers.
    Supports: Ollama (local), OpenAI, Anthropic, Google Gemini.

Usage:
    from skills.llm_wrapper.skill import complete, provider_info
    
    # Check current provider
    print(provider_info())
    
    # Make a completion
    response = complete(
        prompt="Classify this text...",
        system="You are a classifier.",
        json_mode=True
    )
"""

import os
import time
import logging
from typing import Dict, Any

try:
    from litellm import completion
    HAS_LITELLM = True
except ImportError:
    HAS_LITELLM = False
    import requests

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import (
    LLM_PROVIDER,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
    OPENAI_API_KEY, OPENAI_MODEL,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL,
    GOOGLE_API_KEY, GOOGLE_MODEL,
    TEMPERATURE, MAX_TOKENS,
    RETRY_ATTEMPTS, RETRY_DELAY_BASE,
)

logger = logging.getLogger(__name__)


def provider_info() -> Dict[str, Any]:
    """Return current provider and model info."""
    models = {
        "ollama": OLLAMA_MODEL,
        "openai": OPENAI_MODEL,
        "anthropic": ANTHROPIC_MODEL,
        "google": GOOGLE_MODEL,
    }
    return {
        "provider": LLM_PROVIDER,
        "model": models.get(LLM_PROVIDER, "unknown"),
        "litellm": HAS_LITELLM,
    }


def _model_string() -> str:
    """Convert to litellm format."""
    prefixes = {
        "ollama": "ollama",
        "openai": "openai",
        "anthropic": "anthropic",
        "google": "gemini",
    }
    models = {
        "ollama": OLLAMA_MODEL,
        "openai": OPENAI_MODEL,
        "anthropic": ANTHROPIC_MODEL,
        "google": GOOGLE_MODEL,
    }
    return f"{prefixes[LLM_PROVIDER]}/{models[LLM_PROVIDER]}"


def _ollama_direct(prompt: str, system: str = None) -> str:
    """Direct HTTP call to Ollama."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": MAX_TOKENS,
        }
    }
    if system:
        payload["system"] = system

    response = requests.post(url, json=payload, timeout=120)
    response.raise_for_status()
    return response.json().get("response", "")


def complete(
    prompt: str,
    system: str = None,
    json_mode: bool = True
) -> str:
    """
    Send completion request to LLM.
    
    Args:
        prompt: User message / input
        system: System instructions
        json_mode: If True, request JSON output
        
    Returns:
        Model response as string
    """
    messages = []
    if system:
        if json_mode:
            system = system + "\n\nRespond with valid JSON only. No markdown, no extra text."
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    for attempt in range(RETRY_ATTEMPTS):
        try:
            start = time.time()

            if HAS_LITELLM:
                # Set API keys
                if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
                    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
                elif LLM_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
                    os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY
                elif LLM_PROVIDER == "google" and GOOGLE_API_KEY:
                    os.environ["GEMINI_API_KEY"] = GOOGLE_API_KEY

                response = completion(
                    model=_model_string(),
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                )
                content = response.choices[0].message.content

            else:
                if LLM_PROVIDER != "ollama":
                    raise ImportError(f"litellm required for {LLM_PROVIDER}")

                system_text = None
                user_text = ""
                for msg in messages:
                    if msg["role"] == "system":
                        system_text = msg["content"]
                    elif msg["role"] == "user":
                        user_text = msg["content"]

                content = _ollama_direct(user_text, system_text)

            latency = (time.time() - start) * 1000
            logger.debug(f"Response in {latency:.0f}ms")

            return content

        except Exception as e:
            delay = RETRY_DELAY_BASE ** attempt
            logger.warning(f"Attempt {attempt + 1}/{RETRY_ATTEMPTS} failed: {e}")
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(delay)

    raise RuntimeError(f"All {RETRY_ATTEMPTS} attempts failed")
