"""Clipboard output module."""

from __future__ import annotations

import time
from typing import Literal

import pyperclip
import pyautogui


class ClipboardOutput:
    """
    Handles output of transcribed text to clipboard and auto-paste.

    Usage:
        output = ClipboardOutput(behavior="auto_paste")
        output.send("Hello, world!")
    """

    def __init__(
        self,
        behavior: Literal["clipboard_only", "auto_paste"] = "auto_paste",
        paste_delay: float = 0.1,
    ):
        """
        Initialize clipboard output.

        Args:
            behavior: "clipboard_only" or "auto_paste"
            paste_delay: Delay in seconds before pasting (for UI to catch up)
        """
        self.behavior = behavior
        self.paste_delay = paste_delay

        # Configure pyautogui
        pyautogui.PAUSE = 0.02  # Small pause between actions

    def send(self, text: str) -> None:
        """
        Send text to clipboard and optionally paste.

        Args:
            text: Text to send
        """
        if not text:
            return

        # Always copy to clipboard
        pyperclip.copy(text)

        # Auto-paste if configured
        if self.behavior == "auto_paste":
            time.sleep(self.paste_delay)
            # Use pyautogui for more reliable paste
            pyautogui.hotkey('ctrl', 'v')

    def get_clipboard(self) -> str:
        """
        Get current clipboard content.

        Returns:
            Current clipboard text
        """
        try:
            return pyperclip.paste() or ""
        except Exception:
            return ""

    def set_behavior(self, behavior: Literal["clipboard_only", "auto_paste"]) -> None:
        """Change output behavior."""
        self.behavior = behavior
