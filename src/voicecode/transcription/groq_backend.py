"""Groq transcription backend using Whisper."""

from __future__ import annotations

import io
from pathlib import Path

from groq import Groq

from .base import BaseTranscriber


class GroqTranscriber(BaseTranscriber):
    """
    Transcription using Groq API with Whisper model.

    This is the fastest cloud-based transcription option.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "whisper-large-v3",
    ):
        """
        Initialize the Groq transcriber.

        Args:
            api_key: Groq API key
            model: Whisper model to use (whisper-large-v3 recommended)
        """
        self.api_key = api_key
        self.model = model
        self._client: Groq | None = None

    def _get_client(self) -> Groq:
        """Get or create Groq client."""
        if self._client is None:
            self._client = Groq(api_key=self.api_key)
        return self._client

    def transcribe(self, audio: bytes, language: str = "pt") -> str:
        """
        Transcribe audio using Groq Whisper API.

        Args:
            audio: WAV audio bytes
            language: Language code (e.g., "pt" for Portuguese, "en" for English)

        Returns:
            Transcribed text
        """
        if not audio:
            return ""

        client = self._get_client()

        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio)
        audio_file.name = "audio.wav"

        try:
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio_file, "audio/wav"),
                model=self.model,
                language=language,
                response_format="text",
                prompt="Transcrição de instruções de programação em português. Termos técnicos: Python, TypeScript, React, API, função, variável, código, Claude, Gemini, commit, push, pull request.",
            )

            # The response is the transcribed text directly
            return transcription.strip() if isinstance(transcription, str) else str(transcription).strip()

        except Exception as e:
            raise TranscriptionError(f"Groq transcription failed: {e}") from e

    def is_available(self) -> bool:
        """Check if Groq API is available."""
        if not self.api_key:
            return False

        try:
            # Just check if we can create a client
            self._get_client()
            return True
        except Exception:
            return False


class TranscriptionError(Exception):
    """Error during transcription."""
    pass
