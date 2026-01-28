"""Transcription backends module."""

from .base import BaseTranscriber
from .groq_backend import GroqTranscriber, TranscriptionError
from .local_backend import LocalTranscriber


def create_transcriber(config) -> BaseTranscriber:
    """
    Factory function to create the appropriate transcriber.

    Args:
        config: Application config object

    Returns:
        Transcriber instance based on config
    """
    if config.transcription.backend == "local":
        return LocalTranscriber(
            model=config.transcription.local.model,
            device=config.transcription.local.device,
        )
    else:
        return GroqTranscriber(
            api_key=config.transcription.groq.api_key,
            model=config.transcription.groq.model,
        )


__all__ = [
    "BaseTranscriber",
    "GroqTranscriber",
    "LocalTranscriber",
    "TranscriptionError",
    "create_transcriber",
]
