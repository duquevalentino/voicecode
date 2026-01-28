"""VoiceCode entry point."""

from __future__ import annotations

import argparse
import sys
import time
import threading
from pathlib import Path

from .config import load_config, validate_config, Config
from .audio.recorder import AudioRecorder
from .transcription.groq_backend import GroqTranscriber
from .processing.groq_backend import GroqProcessor
from .hotkeys.listener import HotkeyListener, HotkeyCallbacks
from .output.clipboard import ClipboardOutput
from .ui.tray import SystemTray
from .ui.sounds import SoundPlayer
from .history import HistoryLogger


class VoiceCodeApp:
    """Main application orchestrator."""

    def __init__(self, config: Config):
        """Initialize the application with configuration."""
        self.config = config
        self._running = False

        # Initialize components
        self.recorder = AudioRecorder(
            sample_rate=16000,
            channels=1,
            device=config.audio.device,
            on_error=self._on_audio_error,
        )

        self.transcriber = GroqTranscriber(
            api_key=config.transcription.groq.api_key,
            model=config.transcription.groq.model,
        )

        self.processor = GroqProcessor(
            api_key=config.transcription.groq.api_key,
            model=config.processing.groq.model,
        )

        self.history = HistoryLogger(
            file_path=config.history.file,
            max_entries=config.history.max_entries,
            enabled=config.history.enabled,
        )

        self.output = ClipboardOutput(
            behavior=config.output.behavior,
        )

        self.tray = SystemTray(
            on_quit=self.stop,
            show_mode_tooltip=config.feedback.tray.show_mode_tooltip,
        )

        self.sounds = SoundPlayer(
            enabled=config.feedback.sounds.enabled,
            start_sound=config.feedback.sounds.start,
            end_sound=config.feedback.sounds.end,
        )

        # Setup hotkey callbacks
        callbacks = HotkeyCallbacks(
            on_activate=self._on_start_recording,
            on_deactivate=self._on_stop_recording,
            on_cycle_mode=self._on_cycle_mode,
            on_context_activate=self._on_start_recording_with_context,
            on_context_deactivate=self._on_stop_recording_with_context,
        )

        self.hotkeys = HotkeyListener(
            main_key=config.hotkeys.main_key,
            activation_mode=config.hotkeys.activation_mode,
            callbacks=callbacks,
            context_modifier=config.hotkeys.context_modifier,
            cycle_mode_key=config.hotkeys.cycle_mode_key,
        )

        # State
        self._context_mode = False
        self._clipboard_context: str = ""

    def _on_audio_error(self, error: Exception) -> None:
        """Handle audio recording errors."""
        print(f"[ERROR] Audio: {error}")
        self.tray.set_state("error")

    def _on_start_recording(self) -> None:
        """Called when user activates recording."""
        self._context_mode = False
        self._start_recording()

    def _on_start_recording_with_context(self) -> None:
        """Called when user activates recording with context modifier."""
        self._context_mode = True
        # Capture clipboard content for context
        self._clipboard_context = self.output.get_clipboard()
        self._start_recording()

    def _start_recording(self) -> None:
        """Start the recording process."""
        print("[Recording] Started...")
        self.sounds.play_start()
        self.tray.set_state("recording")
        self.recorder.start_recording()

    def _on_stop_recording(self) -> None:
        """Called when user deactivates recording."""
        self._stop_recording(use_context=False)

    def _on_stop_recording_with_context(self) -> None:
        """Called when user deactivates recording with context."""
        self._stop_recording(use_context=True)

    def _stop_recording(self, use_context: bool = False) -> None:
        """Stop recording and process audio."""
        print("[Recording] Stopped. Processing...")
        self.tray.set_state("processing")

        # Get audio data
        audio_data = self.recorder.stop_recording()

        if not audio_data:
            print("[WARNING] No audio recorded")
            self.tray.set_state("idle")
            return

        # Process in background thread to not block UI
        thread = threading.Thread(
            target=self._process_audio,
            args=(audio_data, use_context),
            daemon=True,
        )
        thread.start()

    def _process_audio(self, audio_data: bytes, use_context: bool) -> None:
        """Process recorded audio (runs in background thread)."""
        try:
            # Transcribe
            raw_text = self.transcriber.transcribe(
                audio_data,
                language=self.config.language.primary,
            )

            if not raw_text:
                print("[WARNING] No transcription returned")
                self.tray.set_state("idle")
                return

            print(f"[Transcribed] {raw_text}")

            # Process with LLM based on mode
            context = self._clipboard_context if use_context else None

            if use_context and context:
                print(f"[Context] Using clipboard ({len(context)} chars)")

            final_text = self.processor.process(
                text=raw_text,
                mode=self.config.mode,
                vocabulary=self.config.vocabulary,
                context=context,
            )

            if self.config.mode != "raw":
                print(f"[Processed] {final_text}")

            # Log to history
            self.history.log(
                raw=raw_text,
                processed=final_text,
                mode=self.config.mode,
                had_context=use_context and bool(context),
            )

            # Output
            self.output.send(final_text)
            self.sounds.play_end()

            # Show ready state briefly
            self.tray.set_state("ready")
            time.sleep(1)
            self.tray.set_state("idle")

            print("[Done] Text sent to clipboard/pasted")

        except Exception as e:
            print(f"[ERROR] Processing failed: {e}")
            self.tray.set_state("error")
            time.sleep(2)
            self.tray.set_state("idle")

    def _on_cycle_mode(self) -> None:
        """Cycle through processing modes."""
        modes = ["raw", "clean", "tech", "full"]
        current_index = modes.index(self.config.mode) if self.config.mode in modes else 0
        next_index = (current_index + 1) % len(modes)
        self.config.mode = modes[next_index]

        print(f"[Mode] Switched to: {self.config.mode}")
        self.tray.set_mode(self.config.mode)

    def start(self) -> None:
        """Start the application."""
        if self._running:
            return

        self._running = True

        print("VoiceCode Starting...")
        print(f"  Audio device: {self.config.audio.device or 'default'}")
        print(f"  Hotkey: {self.config.hotkeys.main_key}")
        print(f"  Activation: {self.config.hotkeys.activation_mode}")
        print(f"  Context modifier: +{self.config.hotkeys.context_modifier}")
        print(f"  Cycle mode key: {self.config.hotkeys.cycle_mode_key}")
        print(f"  Processing mode: {self.config.mode}")
        print()

        # Start components
        self.tray.start()
        self.tray.set_mode(self.config.mode)
        self.hotkeys.start()

        print("[READY] Press hotkey to record. Ctrl+C to quit.")
        print()

        # Keep main thread alive
        try:
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[Shutting down...]")
            self.stop()

    def stop(self) -> None:
        """Stop the application."""
        self._running = False
        self.hotkeys.stop()
        self.tray.stop()
        print("[Stopped]")


def check_config(config_path: Path | None = None) -> int:
    """Check configuration and print status."""
    print("VoiceCode - Configuration Check")
    print("=" * 40)

    try:
        config = load_config(config_path)
        print("[OK] Config file loaded successfully")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Failed to parse config: {e}")
        return 1

    issues = validate_config(config)

    if issues:
        print("\n[WARNINGS]")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("[OK] Configuration valid")

    print("\n" + "-" * 40)
    print("Configuration Summary:")
    print("-" * 40)
    print(f"  Hotkey Mode:       {config.hotkeys.activation_mode}")
    print(f"  Main Key:          {config.hotkeys.main_key}")
    print(f"  Context Modifier:  {config.hotkeys.context_modifier}")
    print(f"  Cycle Mode Key:    {config.hotkeys.cycle_mode_key}")
    print()
    print(f"  Transcription:     {config.transcription.backend}")
    print(f"  Processing:        {config.processing.backend}")
    print(f"  Mode:              {config.mode}")
    print()
    print(f"  Output:            {config.output.behavior}")
    print(f"  History:           {'enabled' if config.history.enabled else 'disabled'}")
    print(f"  Sounds:            {'enabled' if config.feedback.sounds.enabled else 'disabled'}")
    print()
    print(f"  Vocabulary Terms:  {len(config.vocabulary)}")
    print("-" * 40)

    if issues:
        print("\n[WARNING] Configuration has issues. Please fix before running.")
        return 1

    print("\n[READY] Configuration valid. Ready to start.")
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="voicecode",
        description="Voice-to-text transcription for coding",
    )

    parser.add_argument(
        "--check-config",
        action="store_true",
        help="Check configuration and exit",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.yaml file",
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit",
    )

    args = parser.parse_args()

    if args.version:
        from . import __version__
        print(f"VoiceCode v{__version__}")
        return 0

    if args.check_config:
        return check_config(args.config)

    # Normal execution
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return 1

    issues = validate_config(config)
    if issues:
        print("[ERROR] Configuration issues:")
        for issue in issues:
            print(f"  - {issue}")
        return 1

    # Run the application
    app = VoiceCodeApp(config)

    try:
        app.start()
    except Exception as e:
        print(f"[ERROR] Application error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
