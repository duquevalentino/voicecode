"""Sound feedback module using Windows native API."""

from __future__ import annotations

import threading
from pathlib import Path

# Windows native sound
try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


class SoundPlayer:
    """
    Plays sound feedback for recording start/stop.

    Uses Windows native winsound for reliable playback.
    Falls back to system beeps if custom sounds not found.
    """

    # Default beep frequencies (Hz) and duration (ms)
    BEEP_START = (800, 100)   # Higher pitch, short
    BEEP_END = (600, 150)     # Lower pitch, slightly longer
    BEEP_MODE = (1000, 50)    # High pitch, very short

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
            start_sound: Path to start recording sound (WAV)
            end_sound: Path to end recording sound (WAV)
        """
        self.enabled = enabled
        self.start_sound = Path(start_sound) if start_sound else None
        self.end_sound = Path(end_sound) if end_sound else None

    def _play_async(self, func, *args) -> None:
        """Play sound in background thread to not block."""
        if not self.enabled or not HAS_WINSOUND:
            return
        thread = threading.Thread(target=func, args=args, daemon=True)
        thread.start()

    def _play_wav(self, path: Path) -> None:
        """Play a WAV file."""
        if path and path.exists():
            try:
                winsound.PlaySound(str(path), winsound.SND_FILENAME)
            except Exception:
                pass

    def _play_beep(self, frequency: int, duration: int) -> None:
        """Play a system beep."""
        try:
            winsound.Beep(frequency, duration)
        except Exception:
            pass

    def play_start(self) -> None:
        """Play start recording sound."""
        if not self.enabled:
            return

        if self.start_sound and self.start_sound.exists():
            self._play_async(self._play_wav, self.start_sound)
        else:
            # Use system beep
            self._play_async(self._play_beep, *self.BEEP_START)

    def play_end(self) -> None:
        """Play end recording sound."""
        if not self.enabled:
            return

        if self.end_sound and self.end_sound.exists():
            self._play_async(self._play_wav, self.end_sound)
        else:
            # Use system beep
            self._play_async(self._play_beep, *self.BEEP_END)

    def play_mode_change(self) -> None:
        """Play mode change sound."""
        if not self.enabled:
            return
        self._play_async(self._play_beep, *self.BEEP_MODE)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable sounds."""
        self.enabled = enabled
