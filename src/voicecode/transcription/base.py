"""Base transcriber interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseTranscriber(ABC):
    """Abstract base class for transcription backends."""

    @abstractmethod
    def transcribe(self, audio: bytes, language: str = "pt") -> str:
        """
        Transcribe audio to text.

        Args:
            audio: WAV audio bytes
            language: Language code (e.g., "pt", "en")

        Returns:
            Transcribed text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the transcription backend is available."""
        pass
