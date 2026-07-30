"""AI client abstraction — pluggable LLM backend."""

from __future__ import annotations

from abc import ABC, abstractmethod

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

    if config.ai_provider == "openai" and config.ai_api_key:
        return OpenAIClient(api_key=config.ai_api_key, model=config.ai_model)

    return MockAIClient()
