"""History logging module."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TypedDict


class HistoryEntry(TypedDict):
    """History entry structure."""
    timestamp: str
    mode: str
    raw: str
    processed: str
    had_context: bool


class HistoryLogger:
    """
    Logs transcriptions to a JSONL file with sliding window.

    Each line in the file is a JSON object with:
    - timestamp: ISO format datetime
    - mode: Processing mode used
    - raw: Original transcription
    - processed: Processed text
    - had_context: Whether context injection was used
    """

    def __init__(
        self,
        file_path: str | Path,
        max_entries: int = 1000,
        enabled: bool = True,
    ):
        """
        Initialize history logger.

        Args:
            file_path: Path to JSONL file
            max_entries: Maximum entries before rotation
            enabled: Whether logging is enabled
        """
        self.file_path = Path(file_path)
        self.max_entries = max_entries
        self.enabled = enabled

        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        raw: str,
        processed: str,
        mode: str,
        had_context: bool = False,
    ) -> None:
        """
        Log a transcription entry.

        Args:
            raw: Original transcription
            processed: Processed text
            mode: Processing mode used
            had_context: Whether context injection was used
        """
        if not self.enabled:
            return

        entry: HistoryEntry = {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "raw": raw,
            "processed": processed,
            "had_context": had_context,
        }

        # Append to file
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # Check if rotation needed
        self._rotate_if_needed()

    def _rotate_if_needed(self) -> None:
        """Rotate file if it exceeds max_entries."""
        if not self.file_path.exists():
            return

        # Count lines
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) <= self.max_entries:
            return

        # Keep only the last max_entries
        keep_lines = lines[-self.max_entries:]

        with open(self.file_path, "w", encoding="utf-8") as f:
            f.writelines(keep_lines)

    def get_recent(self, count: int = 10) -> list[HistoryEntry]:
        """
        Get recent history entries.

        Args:
            count: Number of entries to return

        Returns:
            List of recent entries (newest first)
        """
        if not self.file_path.exists():
            return []

        entries = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        # Return newest first
        return entries[-count:][::-1]

    def clear(self) -> None:
        """Clear all history."""
        if self.file_path.exists():
            self.file_path.unlink()
