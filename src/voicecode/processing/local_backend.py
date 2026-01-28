"""Local LLM processing backend using Ollama."""

from __future__ import annotations

import httpx

from .base import BaseProcessor, Mode
from .groq_backend import SYSTEM_PROMPTS


class LocalProcessor(BaseProcessor):
    """
    Local text processing using Ollama.

    Requires Ollama to be installed and running locally.
    Install: https://ollama.ai
    Run: ollama run llama3:8b
    """

    def __init__(
        self,
        model: str = "llama3:8b",
        endpoint: str = "http://localhost:11434",
        timeout: float = 120.0,  # 2 minutos para primeira carga do modelo
    ):
        """
        Initialize local processor.

        Args:
            model: Ollama model name
            endpoint: Ollama API endpoint
            timeout: Request timeout in seconds
        """
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout

    def process(
        self,
        text: str,
        mode: Mode,
        vocabulary: list[str] | None = None,
        context: str | None = None,
    ) -> str:
        """
        Process text using local Ollama LLM.

        Args:
            text: Raw transcribed text
            mode: Processing mode
            vocabulary: Custom vocabulary terms
            context: Optional context from clipboard

        Returns:
            Processed text
        """
        if not text:
            return ""

        # Raw mode - no processing
        if mode == "raw":
            return text

        # If context is provided, use context mode
        if context:
            return self._process_with_context(text, context, vocabulary)

        # Get appropriate system prompt
        system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["full"])

        # Format vocabulary into prompt
        vocab_str = ", ".join(vocabulary) if vocabulary else "N/A"
        system_prompt = system_prompt.format(vocabulary=vocab_str)

        return self._call_ollama(system_prompt, text)

    def _process_with_context(
        self,
        text: str,
        context: str,
        vocabulary: list[str] | None = None,
    ) -> str:
        """Process text with context injection."""
        system_prompt = SYSTEM_PROMPTS["context"].format(
            context=context[:2000],
            text=text,
        )
        return self._call_ollama(system_prompt, "Reescreva a instrução de forma clara.")

    def _call_ollama(self, system_prompt: str, user_message: str) -> str:
        """Call Ollama API."""
        url = f"{self.endpoint}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1024,
            },
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()

                data = response.json()
                content = data.get("message", {}).get("content", "")
                return content.strip()

        except httpx.ConnectError:
            raise ProcessingError(
                "Cannot connect to Ollama. Make sure Ollama is running:\n"
                "  1. Install from https://ollama.ai\n"
                "  2. Run: ollama serve\n"
                "  3. Pull model: ollama pull llama3:8b"
            )
        except httpx.TimeoutException:
            raise ProcessingError(f"Ollama request timed out after {self.timeout}s")
        except Exception as e:
            raise ProcessingError(f"Ollama processing failed: {e}")

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.endpoint}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """List available Ollama models."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.endpoint}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []


class ProcessingError(Exception):
    """Error during local processing."""
    pass
