"""Sound feedback module."""

from __future__ import annotations

import threading
from pathlib import Path

# Note: For Phase 5, we'll implement actual sound playback
# For now, this is a stub that can be enabled later


class SoundPlayer:
    """
    Plays sound feedback for recording start/stop.

    Note: Actual sound playback will be implemented in Phase 5.
    For now, this is a placeholder.
    """

    def __init__(
        self,
        enabled: bool = True,
        start_sound: str | Path | None = None,
        end_sound: str | Path | None = None,
    ):
        """
        Initialize sound player.

        Args:
            enabled: Whether sounds are enabled
            start_sound: Path to start recording sound
            end_sound: Path to end recording sound
        """
        self.enabled = enabled
        self.start_sound = Path(start_sound) if start_sound else None
        self.end_sound = Path(end_sound) if end_sound else None

    def play_start(self) -> None:
        """Play start recording sound."""
        if not self.enabled:
            return
        # TODO: Implement in Phase 5
        pass

    def play_end(self) -> None:
        """Play end recording sound."""
        if not self.enabled:
            return
        # TODO: Implement in Phase 5
        pass

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable sounds."""
        self.enabled = enabled
