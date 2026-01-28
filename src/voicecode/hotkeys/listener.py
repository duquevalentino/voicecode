"""Global hotkey listener."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Callable, Literal

import keyboard


@dataclass
class HotkeyCallbacks:
    """Callbacks for hotkey events."""
    on_activate: Callable[[], None]
    on_deactivate: Callable[[], None]
    on_cycle_mode: Callable[[], None] | None = None
    on_context_activate: Callable[[], None] | None = None
    on_context_deactivate: Callable[[], None] | None = None


class HotkeyListener:
    """
    Global hotkey listener supporting push-to-talk and toggle modes.

    Usage:
        callbacks = HotkeyCallbacks(
            on_activate=start_recording,
            on_deactivate=stop_recording,
        )
        listener = HotkeyListener(
            main_key="ctrl+shift+space",
            activation_mode="push_to_talk",
            callbacks=callbacks,
        )
        listener.start()
    """

    def __init__(
        self,
        main_key: str,
        activation_mode: Literal["push_to_talk", "toggle"],
        callbacks: HotkeyCallbacks,
        context_modifier: str | None = None,
        cycle_mode_key: str | None = None,
    ):
        """
        Initialize the hotkey listener.

        Args:
            main_key: Main activation key (e.g., "ctrl+shift+space")
            activation_mode: "push_to_talk" or "toggle"
            callbacks: Callback functions for events
            context_modifier: Modifier key for context injection (e.g., "alt")
            cycle_mode_key: Key to cycle between modes
        """
        self.main_key = main_key.lower()
        self.activation_mode = activation_mode
        self.callbacks = callbacks
        self.context_modifier = context_modifier.lower() if context_modifier else None
        self.cycle_mode_key = cycle_mode_key.lower() if cycle_mode_key else None

        self._active = False
        self._context_active = False
        self._running = False
        self._toggle_state = False  # For toggle mode
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start listening for hotkeys."""
        if self._running:
            return

        self._running = True

        if self.activation_mode == "push_to_talk":
            self._setup_push_to_talk()
        else:
            self._setup_toggle()

        # Setup cycle mode key if provided
        if self.cycle_mode_key and self.callbacks.on_cycle_mode:
            keyboard.add_hotkey(
                self.cycle_mode_key,
                self._on_cycle_mode,
                suppress=True,
            )

    def stop(self) -> None:
        """Stop listening for hotkeys."""
        if not self._running:
            return

        self._running = False
        keyboard.unhook_all()

    def _setup_push_to_talk(self) -> None:
        """Setup push-to-talk mode (hold to record)."""
        self._last_key = self._get_last_key(self.main_key)

        # Register context hotkey first (more specific, with Alt)
        if self.context_modifier:
            context_hotkey = f"{self.context_modifier}+{self.main_key}"
            keyboard.add_hotkey(
                context_hotkey,
                self._on_context_hotkey_press,
                suppress=True,
                trigger_on_release=False,
            )

        # Register main hotkey
        keyboard.add_hotkey(
            self.main_key,
            self._on_hotkey_press,
            suppress=True,
            trigger_on_release=False,
        )

        # Track key release for the last key in combination
        keyboard.on_release_key(
            self._last_key,
            self._on_key_up_check,
            suppress=False,
        )

    def _setup_toggle(self) -> None:
        """Setup toggle mode (press to start/stop)."""
        # Register context hotkey first (with Alt)
        if self.context_modifier:
            context_hotkey = f"{self.context_modifier}+{self.main_key}"
            keyboard.add_hotkey(
                context_hotkey,
                lambda: self._on_toggle(with_context=True),
                suppress=True,
            )

        # Register main hotkey
        keyboard.add_hotkey(
            self.main_key,
            lambda: self._on_toggle(with_context=False),
            suppress=True,
        )

    def _get_last_key(self, hotkey: str) -> str:
        """Get the last key from a hotkey combination."""
        parts = hotkey.replace(" ", "").split("+")
        return parts[-1] if parts else hotkey

    def _check_modifiers(self) -> bool:
        """Check if required modifier keys are pressed."""
        parts = self.main_key.replace(" ", "").split("+")
        modifiers = parts[:-1]  # All parts except the last key

        for mod in modifiers:
            if not keyboard.is_pressed(mod):
                return False
        return True

    def _is_context_modifier_pressed(self) -> bool:
        """Check if context modifier is pressed."""
        if not self.context_modifier:
            return False
        return keyboard.is_pressed(self.context_modifier)

    def _on_hotkey_press(self) -> None:
        """Handle main hotkey press in push-to-talk mode."""
        with self._lock:
            if self._active:
                return
            self._active = True
            self._context_active = False

        self.callbacks.on_activate()

    def _on_context_hotkey_press(self) -> None:
        """Handle context hotkey press (main + context modifier)."""
        with self._lock:
            if self._active:
                return
            self._active = True
            self._context_active = True

        if self.callbacks.on_context_activate:
            self.callbacks.on_context_activate()
        else:
            self.callbacks.on_activate()

    def _on_key_up_check(self, event: keyboard.KeyboardEvent) -> None:
        """Handle key up - only trigger if we were active."""
        with self._lock:
            if not self._active:
                return
            self._active = False
            was_context = self._context_active
            self._context_active = False

        if was_context and self.callbacks.on_context_deactivate:
            self.callbacks.on_context_deactivate()
        else:
            self.callbacks.on_deactivate()

    def _on_toggle(self, with_context: bool = False) -> None:
        """Handle toggle activation."""
        with self._lock:
            self._toggle_state = not self._toggle_state
            is_active = self._toggle_state
            self._context_active = with_context if is_active else False

        if is_active:
            if self._context_active and self.callbacks.on_context_activate:
                self.callbacks.on_context_activate()
            else:
                self.callbacks.on_activate()
        else:
            if self._context_active and self.callbacks.on_context_deactivate:
                self.callbacks.on_context_deactivate()
            else:
                self.callbacks.on_deactivate()
            self._context_active = False

    def _on_cycle_mode(self) -> None:
        """Handle cycle mode key press."""
        if self.callbacks.on_cycle_mode:
            self.callbacks.on_cycle_mode()

    def is_active(self) -> bool:
        """Check if recording is currently active."""
        return self._active or self._toggle_state
