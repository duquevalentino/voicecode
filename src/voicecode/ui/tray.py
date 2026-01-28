"""System tray icon module."""

from __future__ import annotations

import threading
from typing import Callable, Literal

from PIL import Image, ImageDraw
import pystray


State = Literal["idle", "recording", "processing", "ready", "error"]


class SystemTray:
    """
    System tray icon with state indication.

    States:
        - idle: Gray icon, waiting for activation
        - recording: Red icon, recording audio
        - processing: Yellow icon, transcribing/processing
        - ready: Green icon (briefly), text ready
        - error: Red blinking icon
    """

    # Colors for each state
    COLORS = {
        "idle": "#808080",      # Gray
        "recording": "#FF4444",  # Red
        "processing": "#FFB800", # Yellow/Orange
        "ready": "#44BB44",      # Green
        "error": "#FF0000",      # Bright Red
    }

    def __init__(
        self,
        on_quit: Callable[[], None] | None = None,
        show_mode_tooltip: bool = True,
    ):
        """
        Initialize system tray.

        Args:
            on_quit: Callback when user clicks Quit
            show_mode_tooltip: Whether to show current mode in tooltip
        """
        self.on_quit = on_quit
        self.show_mode_tooltip = show_mode_tooltip

        self._state: State = "idle"
        self._mode: str = "full"
        self._icon: pystray.Icon | None = None
        self._thread: threading.Thread | None = None

    def _create_icon_image(self, color: str, size: int = 64) -> Image.Image:
        """Create a colored circle icon."""
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Draw filled circle
        margin = 4
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=color,
            outline=None,
        )

        return image

    def _get_tooltip(self) -> str:
        """Get tooltip text based on current state and mode."""
        state_text = {
            "idle": "VoiceCode - Ready",
            "recording": "VoiceCode - Recording...",
            "processing": "VoiceCode - Processing...",
            "ready": "VoiceCode - Done!",
            "error": "VoiceCode - Error",
        }

        tooltip = state_text.get(self._state, "VoiceCode")

        if self.show_mode_tooltip and self._state == "idle":
            tooltip += f" [{self._mode}]"

        return tooltip

    def _create_menu(self) -> pystray.Menu:
        """Create the tray menu."""
        items = [
            pystray.MenuItem(
                f"Mode: {self._mode}",
                None,
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Quit",
                self._on_quit_click,
            ),
        ]
        return pystray.Menu(*items)

    def _on_quit_click(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        """Handle quit menu click."""
        if self.on_quit:
            self.on_quit()
        self.stop()

    def start(self) -> None:
        """Start the system tray icon in a background thread."""
        if self._icon is not None:
            return

        image = self._create_icon_image(self.COLORS["idle"])

        self._icon = pystray.Icon(
            name="voicecode",
            icon=image,
            title=self._get_tooltip(),
            menu=self._create_menu(),
        )

        # Run in background thread
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop and remove the system tray icon."""
        if self._icon:
            self._icon.stop()
            self._icon = None

    def set_state(self, state: State) -> None:
        """
        Update the tray icon state.

        Args:
            state: New state (idle, recording, processing, ready, error)
        """
        self._state = state

        if self._icon:
            color = self.COLORS.get(state, self.COLORS["idle"])
            self._icon.icon = self._create_icon_image(color)
            self._icon.title = self._get_tooltip()

    def set_mode(self, mode: str) -> None:
        """
        Update the current mode displayed in tooltip/menu.

        Args:
            mode: Mode name (raw, clean, tech, full)
        """
        self._mode = mode

        if self._icon:
            self._icon.title = self._get_tooltip()
            self._icon.menu = self._create_menu()

    def get_state(self) -> State:
        """Get current state."""
        return self._state
