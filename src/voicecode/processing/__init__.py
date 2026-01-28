"""Text processing module."""

from .base import BaseProcessor, Mode
from .groq_backend import GroqProcessor, ProcessingError
from .local_backend import LocalProcessor


def create_processor(config) -> BaseProcessor:
    """
    Factory function to create the appropriate processor.

    Args:
        config: Application config object

    Returns:
        Processor instance based on config
    """
    if config.processing.backend == "local":
        return LocalProcessor(
            model=config.processing.local.model,
            endpoint=config.processing.local.endpoint,
        )
    else:
        return GroqProcessor(
            api_key=config.transcription.groq.api_key,
            model=config.processing.groq.model,
        )


__all__ = [
    "BaseProcessor",
    "Mode",
    "GroqProcessor",
    "LocalProcessor",
    "ProcessingError",
    "create_processor",
]
