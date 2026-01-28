"""Configuration GUI for VoiceCode."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Callable

import yaml


class ConfigGUI:
    """Simple configuration GUI for VoiceCode."""

    def __init__(
        self,
        config_path: Path,
        on_config_change: Callable[[], None] | None = None,
    ):
        self.config_path = Path(config_path)
        self.on_config_change = on_config_change
        self.config_data = {}
        self._load_config()
        self._create_window()

    def _load_config(self) -> None:
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config_data = yaml.safe_load(f) or {}

    def _save_config(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)
        if self.on_config_change:
            self.on_config_change()

    def _create_window(self) -> None:
        self.root = tk.Tk()
        self.root.title("VoiceCode - Settings")
        self.root.geometry("420x580")
        self.root.resizable(False, False)

        # Main container
        container = ttk.Frame(self.root, padding=10)
        container.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        row = 0

        # === AUDIO ===
        lf = ttk.LabelFrame(container, text="Audio", padding=8)
        lf.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        row += 1

        ttk.Label(lf, text="Device:").grid(row=0, column=0, sticky="w")
        self.audio_device_var = tk.StringVar(value=self.config_data.get("audio", {}).get("device") or "")
        ttk.Entry(lf, textvariable=self.audio_device_var, width=25).grid(row=0, column=1, padx=5)
        ttk.Label(lf, text="(vazio=padrão)", font=("", 8)).grid(row=0, column=2)

        # === HOTKEYS ===
        lf = ttk.LabelFrame(container, text="Hotkeys", padding=8)
        lf.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        row += 1

        hotkeys = self.config_data.get("hotkeys", {})

        ttk.Label(lf, text="Modo:").grid(row=0, column=0, sticky="w")
        self.activation_mode_var = tk.StringVar(value=hotkeys.get("activation_mode", "push_to_talk"))
        ttk.Combobox(lf, textvariable=self.activation_mode_var, values=["push_to_talk", "toggle"],
                     state="readonly", width=15).grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(lf, text="Tecla:").grid(row=1, column=0, sticky="w", pady=(5,0))
        self.main_key_var = tk.StringVar(value=hotkeys.get("main_key", "ctrl+shift+space"))
        ttk.Entry(lf, textvariable=self.main_key_var, width=20).grid(row=1, column=1, padx=5, pady=(5,0), sticky="w")

        ttk.Label(lf, text="Contexto:").grid(row=2, column=0, sticky="w", pady=(5,0))
        self.context_mod_var = tk.StringVar(value=hotkeys.get("context_modifier", "alt"))
        ttk.Entry(lf, textvariable=self.context_mod_var, width=10).grid(row=2, column=1, padx=5, pady=(5,0), sticky="w")

        # === BACKEND ===
        lf = ttk.LabelFrame(container, text="Backend", padding=8)
        lf.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        row += 1

        ttk.Label(lf, text="Transcrição:").grid(row=0, column=0, sticky="w")
        self.trans_backend_var = tk.StringVar(value=self.config_data.get("transcription", {}).get("backend", "groq"))
        ttk.Combobox(lf, textvariable=self.trans_backend_var, values=["groq", "local"],
                     state="readonly", width=10).grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(lf, text="Processamento:").grid(row=1, column=0, sticky="w", pady=(5,0))
        self.proc_backend_var = tk.StringVar(value=self.config_data.get("processing", {}).get("backend", "groq"))
        ttk.Combobox(lf, textvariable=self.proc_backend_var, values=["groq", "local"],
                     state="readonly", width=10).grid(row=1, column=1, padx=5, pady=(5,0), sticky="w")

        ttk.Label(lf, text="Whisper local:").grid(row=2, column=0, sticky="w", pady=(5,0))
        self.whisper_model_var = tk.StringVar(value=self.config_data.get("transcription", {}).get("local", {}).get("model", "large-v3"))
        ttk.Combobox(lf, textvariable=self.whisper_model_var, values=["tiny", "base", "small", "medium", "large-v3"],
                     state="readonly", width=10).grid(row=2, column=1, padx=5, pady=(5,0), sticky="w")

        ttk.Label(lf, text="Ollama:").grid(row=3, column=0, sticky="w", pady=(5,0))
        self.ollama_model_var = tk.StringVar(value=self.config_data.get("processing", {}).get("local", {}).get("model", "llama3:8b"))
        ttk.Entry(lf, textvariable=self.ollama_model_var, width=15).grid(row=3, column=1, padx=5, pady=(5,0), sticky="w")

        # === PROCESSING ===
        lf = ttk.LabelFrame(container, text="Processamento", padding=8)
        lf.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        row += 1

        ttk.Label(lf, text="Modo:").grid(row=0, column=0, sticky="w")
        self.mode_var = tk.StringVar(value=self.config_data.get("mode", "full"))
        ttk.Combobox(lf, textvariable=self.mode_var, values=["raw", "clean", "tech", "full"],
                     state="readonly", width=10).grid(row=0, column=1, padx=5, sticky="w")

        mode_desc = {"raw": "Sem processamento", "clean": "Remove hesitações", "tech": "Formata termos", "full": "Clean + Tech"}
        self.mode_label = ttk.Label(lf, text=f"({mode_desc.get(self.mode_var.get(), '')})", font=("", 8))
        self.mode_label.grid(row=0, column=2, padx=5)
        self.mode_var.trace_add("write", lambda *a: self.mode_label.config(text=f"({mode_desc.get(self.mode_var.get(), '')})"))

        # === OUTPUT ===
        lf = ttk.LabelFrame(container, text="Saída", padding=8)
        lf.grid(row=row, column=0, sticky="ew", pady=(0, 8))
        row += 1

        ttk.Label(lf, text="Comportamento:").grid(row=0, column=0, sticky="w")
        self.output_var = tk.StringVar(value=self.config_data.get("output", {}).get("behavior", "auto_paste"))
        ttk.Combobox(lf, textvariable=self.output_var, values=["auto_paste", "clipboard_only"],
                     state="readonly", width=15).grid(row=0, column=1, padx=5, sticky="w")

        self.sounds_var = tk.BooleanVar(value=self.config_data.get("feedback", {}).get("sounds", {}).get("enabled", True))
        ttk.Checkbutton(lf, text="Sons ativados", variable=self.sounds_var).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5,0))

        self.history_var = tk.BooleanVar(value=self.config_data.get("history", {}).get("enabled", True))
        ttk.Checkbutton(lf, text="Histórico ativado", variable=self.history_var).grid(row=2, column=0, columnspan=2, sticky="w")

        # === BUTTONS ===
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=row, column=0, sticky="ew", pady=(15, 0))
        row += 1

        ttk.Button(btn_frame, text="Resetar", command=self._on_reset).pack(side="left")
        ttk.Button(btn_frame, text="Cancelar", command=self._on_cancel).pack(side="right", padx=(10, 0))
        ttk.Button(btn_frame, text="Salvar", command=self._on_save).pack(side="right")

    def _collect_values(self) -> dict:
        config = self.config_data.copy()

        if "audio" not in config:
            config["audio"] = {}
        device = self.audio_device_var.get().strip()
        config["audio"]["device"] = device if device else None

        if "hotkeys" not in config:
            config["hotkeys"] = {}
        config["hotkeys"]["activation_mode"] = self.activation_mode_var.get()
        config["hotkeys"]["main_key"] = self.main_key_var.get()
        config["hotkeys"]["context_modifier"] = self.context_mod_var.get()

        if "transcription" not in config:
            config["transcription"] = {}
        config["transcription"]["backend"] = self.trans_backend_var.get()
        if "local" not in config["transcription"]:
            config["transcription"]["local"] = {}
        config["transcription"]["local"]["model"] = self.whisper_model_var.get()

        if "processing" not in config:
            config["processing"] = {}
        config["processing"]["backend"] = self.proc_backend_var.get()
        if "local" not in config["processing"]:
            config["processing"]["local"] = {}
        config["processing"]["local"]["model"] = self.ollama_model_var.get()

        config["mode"] = self.mode_var.get()

        if "output" not in config:
            config["output"] = {}
        config["output"]["behavior"] = self.output_var.get()

        if "feedback" not in config:
            config["feedback"] = {}
        if "sounds" not in config["feedback"]:
            config["feedback"]["sounds"] = {}
        config["feedback"]["sounds"]["enabled"] = self.sounds_var.get()

        if "history" not in config:
            config["history"] = {}
        config["history"]["enabled"] = self.history_var.get()

        return config

    def _on_save(self) -> None:
        self.config_data = self._collect_values()
        self._save_config()
        messagebox.showinfo("Configurações", "Configuração salva!\n\nReinicie o VoiceCode para aplicar.")
        self.root.destroy()

    def _on_cancel(self) -> None:
        self.root.destroy()

    def _on_reset(self) -> None:
        if messagebox.askyesno("Resetar", "Restaurar valores salvos?"):
            self._load_config()
            self.root.destroy()
            self._create_window()
            self.run()

    def run(self) -> None:
        self.root.mainloop()


def open_config_gui(config_path: Path | str | None = None) -> None:
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent.parent / "config.yaml"
    gui = ConfigGUI(Path(config_path))
    gui.run()


if __name__ == "__main__":
    open_config_gui()
