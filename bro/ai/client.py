"""AI client abstraction — pluggable LLM backend."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod

from bro.config.defaults import DEFAULT_OPENROUTER_API_KEY
from bro.config.manager import get_config
from bro.utils.logger import get_logger

logger = get_logger(__name__)


class AIClient(ABC):
    """Abstract AI client interface."""

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], temperature: float = 0.7) -> str:
        """Send a chat completion request."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the client is properly configured."""
        ...


class OpenRouterClient(AIClient):
    """OpenRouter API client."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        cfg = get_config()
        self.api_key = (
            api_key
            or os.getenv("OPENROUTER_API_KEY")
            or os.getenv("BRO_OPENROUTER_API_KEY")
            or cfg.ai_api_key
            or DEFAULT_OPENROUTER_API_KEY
        )
        self.model = model or cfg.ai_model or "google/gemini-2.0-flash-lite-001"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.7) -> str:
        if not self.api_key:
            return "Error: OpenRouter API key is missing. Set it with: bro config"

        # Try OpenAI SDK if installed
        try:
            from openai import OpenAI

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
                default_headers={
                    "HTTP-Referer": "https://github.com/Sameetpatro/broz",
                    "X-Title": "Broz CLI",
                },
            )
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except ImportError:
            pass
        except Exception as e:
            logger.warning("OpenAI SDK failed for OpenRouter, falling back to httpx: %s", e)

        # Fallback to httpx (bundled dependency)
        try:
            import httpx

            http_resp = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://github.com/Sameetpatro/broz",
                    "X-Title": "Broz CLI",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                },
                timeout=30.0,
            )
            if http_resp.status_code == 200:
                data = http_resp.json()
                return str(data["choices"][0]["message"]["content"])
            return f"OpenRouter API error ({http_resp.status_code}): {http_resp.text}"
        except Exception as e:
            logger.error("OpenRouter API request failed: %s", e)
            return f"Error connecting to OpenRouter API: {e}"


class OpenAIClient(AIClient):
    """OpenAI API client."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o") -> None:
        self.api_key = api_key or get_config().ai_api_key
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.7) -> str:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except ImportError:
            logger.error("openai package not installed. Run: uv add openai")
            return "Error: openai package not installed."
        except Exception as e:
            logger.error("OpenAI API error: %s", e)
            return f"Error: {e}"


class MockAIClient(AIClient):
    """Mock AI client for offline mode."""

    def is_available(self) -> bool:
        return True

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.7) -> str:
        return "AI features require an API key. Set it with: bro config"


def get_ai_client() -> AIClient:
    """Get the configured AI client."""
    config = get_config()

    if config.ai_provider == "openrouter" or (not config.ai_provider and DEFAULT_OPENROUTER_API_KEY):
        client = OpenRouterClient()
        if client.is_available():
            return client

    if config.ai_provider == "openai" and config.ai_api_key:
        return OpenAIClient(api_key=config.ai_api_key, model=config.ai_model)

    # Default fallback to OpenRouter if default key or env var is present
    openrouter_client = OpenRouterClient()
    if openrouter_client.is_available():
        return openrouter_client

    return MockAIClient()
