"""Base processor interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Literal


Mode = Literal["raw", "clean", "tech", "full"]


class BaseProcessor(ABC):
    """Abstract base class for text processing backends."""

    @abstractmethod
    def process(
        self,
        text: str,
        mode: Mode,
        vocabulary: list[str] | None = None,
        context: str | None = None,
    ) -> str:
        """
        Process transcribed text.

        Args:
            text: Raw transcribed text
            mode: Processing mode (raw, clean, tech, full)
            vocabulary: Custom vocabulary terms
            context: Optional context (e.g., clipboard content)

        Returns:
            Processed text
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the processing backend is available."""
        pass
