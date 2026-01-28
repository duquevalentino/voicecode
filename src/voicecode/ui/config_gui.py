"""Configuration GUI for VoiceCode."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Callable

import yaml


class ConfigGUI:
    """
    Simple configuration GUI for VoiceCode.

    Allows real-time configuration changes.
    """

    def __init__(
        self,
        config_path: Path,
        on_config_change: Callable[[], None] | None = None,
    ):
        """
        Initialize the configuration GUI.

        Args:
            config_path: Path to config.yaml
            on_config_change: Callback when config changes
        """
        self.config_path = Path(config_path)
        self.on_config_change = on_config_change
        self.config_data = {}

        self._load_config()
        self._create_window()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config_data = yaml.safe_load(f) or {}

    def _save_config(self) -> None:
        """Save configuration to YAML file."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)

        if self.on_config_change:
            self.on_config_change()

    def _create_window(self) -> None:
        """Create the main window."""
        self.root = tk.Tk()
        self.root.title("VoiceCode - Settings")
        self.root.geometry("450x620")
        self.root.resizable(False, False)

        # Style
        style = ttk.Style()
        style.configure("TLabel", padding=5)
        style.configure("TButton", padding=5)
        style.configure("Header.TLabel", font=("Segoe UI", 10, "bold"))

        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create sections
        self._create_audio_section(main_frame)
        self._create_hotkeys_section(main_frame)
        self._create_backend_section(main_frame)
        self._create_processing_section(main_frame)
        self._create_output_section(main_frame)
        self._create_buttons(main_frame)

    def _create_audio_section(self, parent: ttk.Frame) -> None:
        """Create audio settings section."""
        frame = ttk.LabelFrame(parent, text="Audio", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        # Device
        ttk.Label(frame, text="Device:").grid(row=0, column=0, sticky=tk.W)
        self.audio_device_var = tk.StringVar(
            value=self.config_data.get("audio", {}).get("device") or ""
        )
        device_entry = ttk.Entry(frame, textvariable=self.audio_device_var, width=30)
        device_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        ttk.Label(frame, text="(empty = default)", font=("Segoe UI", 8)).grid(
            row=0, column=2, padx=(5, 0)
        )

    def _create_hotkeys_section(self, parent: ttk.Frame) -> None:
        """Create hotkeys settings section."""
        frame = ttk.LabelFrame(parent, text="Hotkeys", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        hotkeys = self.config_data.get("hotkeys", {})

        # Activation mode
        ttk.Label(frame, text="Mode:").grid(row=0, column=0, sticky=tk.W)
        self.activation_mode_var = tk.StringVar(
            value=hotkeys.get("activation_mode", "push_to_talk")
        )
        mode_combo = ttk.Combobox(
            frame,
            textvariable=self.activation_mode_var,
            values=["push_to_talk", "toggle"],
            state="readonly",
            width=15,
        )
        mode_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Main key
        ttk.Label(frame, text="Main Key:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.main_key_var = tk.StringVar(
            value=hotkeys.get("main_key", "ctrl+shift+space")
        )
        key_entry = ttk.Entry(frame, textvariable=self.main_key_var, width=20)
        key_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))

        # Context modifier
        ttk.Label(frame, text="Context Modifier:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.context_mod_var = tk.StringVar(
            value=hotkeys.get("context_modifier", "alt")
        )
        mod_entry = ttk.Entry(frame, textvariable=self.context_mod_var, width=10)
        mod_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))

    def _create_backend_section(self, parent: ttk.Frame) -> None:
        """Create backend settings section."""
        frame = ttk.LabelFrame(parent, text="Backend", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        # Transcription backend
        ttk.Label(frame, text="Transcription:").grid(row=0, column=0, sticky=tk.W)
        self.trans_backend_var = tk.StringVar(
            value=self.config_data.get("transcription", {}).get("backend", "groq")
        )
        trans_combo = ttk.Combobox(
            frame,
            textvariable=self.trans_backend_var,
            values=["groq", "local"],
            state="readonly",
            width=10,
        )
        trans_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Processing backend
        ttk.Label(frame, text="Processing:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.proc_backend_var = tk.StringVar(
            value=self.config_data.get("processing", {}).get("backend", "groq")
        )
        proc_combo = ttk.Combobox(
            frame,
            textvariable=self.proc_backend_var,
            values=["groq", "local"],
            state="readonly",
            width=10,
        )
        proc_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))

        # Local model (Whisper)
        ttk.Label(frame, text="Local Whisper:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.whisper_model_var = tk.StringVar(
            value=self.config_data.get("transcription", {}).get("local", {}).get("model", "large-v3")
        )
        whisper_combo = ttk.Combobox(
            frame,
            textvariable=self.whisper_model_var,
            values=["tiny", "base", "small", "medium", "large-v3"],
            state="readonly",
            width=10,
        )
        whisper_combo.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))

        # Local model (Ollama)
        ttk.Label(frame, text="Local LLM:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.ollama_model_var = tk.StringVar(
            value=self.config_data.get("processing", {}).get("local", {}).get("model", "llama3:8b")
        )
        ollama_entry = ttk.Entry(frame, textvariable=self.ollama_model_var, width=15)
        ollama_entry.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 0))

    def _create_processing_section(self, parent: ttk.Frame) -> None:
        """Create processing settings section."""
        frame = ttk.LabelFrame(parent, text="Processing", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        # Mode
        ttk.Label(frame, text="Mode:").grid(row=0, column=0, sticky=tk.W)
        self.mode_var = tk.StringVar(
            value=self.config_data.get("mode", "full")
        )
        mode_combo = ttk.Combobox(
            frame,
            textvariable=self.mode_var,
            values=["raw", "clean", "tech", "full"],
            state="readonly",
            width=10,
        )
        mode_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Mode descriptions
        descriptions = {
            "raw": "No processing",
            "clean": "Remove filler words",
            "tech": "Format tech terms",
            "full": "Clean + Tech",
        }
        self.mode_desc_label = ttk.Label(
            frame,
            text=f"({descriptions.get(self.mode_var.get(), '')})",
            font=("Segoe UI", 8),
        )
        self.mode_desc_label.grid(row=0, column=2, padx=(10, 0))

        def update_desc(*args):
            self.mode_desc_label.config(
                text=f"({descriptions.get(self.mode_var.get(), '')})"
            )
        self.mode_var.trace_add("write", update_desc)

    def _create_output_section(self, parent: ttk.Frame) -> None:
        """Create output settings section."""
        frame = ttk.LabelFrame(parent, text="Output", padding=10)
        frame.pack(fill=tk.X, pady=(0, 10))

        # Output behavior
        ttk.Label(frame, text="Behavior:").grid(row=0, column=0, sticky=tk.W)
        self.output_var = tk.StringVar(
            value=self.config_data.get("output", {}).get("behavior", "auto_paste")
        )
        output_combo = ttk.Combobox(
            frame,
            textvariable=self.output_var,
            values=["auto_paste", "clipboard_only"],
            state="readonly",
            width=15,
        )
        output_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Sounds enabled
        self.sounds_var = tk.BooleanVar(
            value=self.config_data.get("feedback", {}).get("sounds", {}).get("enabled", True)
        )
        sounds_check = ttk.Checkbutton(
            frame, text="Enable sounds", variable=self.sounds_var
        )
        sounds_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        # History enabled
        self.history_var = tk.BooleanVar(
            value=self.config_data.get("history", {}).get("enabled", True)
        )
        history_check = ttk.Checkbutton(
            frame, text="Enable history logging", variable=self.history_var
        )
        history_check.grid(row=2, column=0, columnspan=2, sticky=tk.W)

    def _create_buttons(self, parent: ttk.Frame) -> None:
        """Create action buttons."""
        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(15, 10))

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(0, 5))

        save_btn = ttk.Button(frame, text="Save & Apply", command=self._on_save, width=12)
        save_btn.pack(side=tk.RIGHT)

        cancel_btn = ttk.Button(frame, text="Cancel", command=self._on_cancel, width=10)
        cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))

        reset_btn = ttk.Button(frame, text="Reset", command=self._on_reset, width=10)
        reset_btn.pack(side=tk.LEFT)

    def _collect_values(self) -> dict:
        """Collect all values from GUI into config dict."""
        config = self.config_data.copy()

        # Audio
        if "audio" not in config:
            config["audio"] = {}
        device = self.audio_device_var.get().strip()
        config["audio"]["device"] = device if device else None

        # Hotkeys
        if "hotkeys" not in config:
            config["hotkeys"] = {}
        config["hotkeys"]["activation_mode"] = self.activation_mode_var.get()
        config["hotkeys"]["main_key"] = self.main_key_var.get()
        config["hotkeys"]["context_modifier"] = self.context_mod_var.get()

        # Transcription
        if "transcription" not in config:
            config["transcription"] = {}
        config["transcription"]["backend"] = self.trans_backend_var.get()
        if "local" not in config["transcription"]:
            config["transcription"]["local"] = {}
        config["transcription"]["local"]["model"] = self.whisper_model_var.get()

        # Processing
        if "processing" not in config:
            config["processing"] = {}
        config["processing"]["backend"] = self.proc_backend_var.get()
        if "local" not in config["processing"]:
            config["processing"]["local"] = {}
        config["processing"]["local"]["model"] = self.ollama_model_var.get()

        # Mode
        config["mode"] = self.mode_var.get()

        # Output
        if "output" not in config:
            config["output"] = {}
        config["output"]["behavior"] = self.output_var.get()

        # Feedback
        if "feedback" not in config:
            config["feedback"] = {}
        if "sounds" not in config["feedback"]:
            config["feedback"]["sounds"] = {}
        config["feedback"]["sounds"]["enabled"] = self.sounds_var.get()

        # History
        if "history" not in config:
            config["history"] = {}
        config["history"]["enabled"] = self.history_var.get()

        return config

    def _on_save(self) -> None:
        """Handle save button click."""
        self.config_data = self._collect_values()
        self._save_config()
        messagebox.showinfo("Settings", "Configuration saved!\n\nRestart VoiceCode to apply changes.")

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.root.destroy()

    def _on_reset(self) -> None:
        """Handle reset button click."""
        if messagebox.askyesno("Reset", "Reset all settings to current saved values?"):
            self._load_config()
            self.root.destroy()
            self._create_window()
            self.run()

    def run(self) -> None:
        """Run the GUI main loop."""
        self.root.mainloop()


def open_config_gui(config_path: Path | str | None = None) -> None:
    """
    Open the configuration GUI.

    Args:
        config_path: Path to config.yaml (default: project root)
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent.parent / "config.yaml"

    gui = ConfigGUI(Path(config_path))
    gui.run()


if __name__ == "__main__":
    open_config_gui()
