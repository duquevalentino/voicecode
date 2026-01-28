"""Configuration loader with typed dataclasses."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml
from dotenv import load_dotenv

# Load .env file from project root
_project_root = Path(__file__).parent.parent.parent
load_dotenv(_project_root / ".env")


# === Dataclasses ===

@dataclass
class AudioConfig:
    """Audio configuration."""
    device: str | int | None = None  # Device name, index, or None for default


@dataclass
class HotkeyConfig:
    """Hotkey configuration."""
    activation_mode: Literal["push_to_talk", "toggle"] = "push_to_talk"
    main_key: str = "ctrl+shift+space"
    context_modifier: str = "alt"
    cycle_mode_key: str = "ctrl+shift+m"


@dataclass
class GroqTranscriptionConfig:
    """Groq transcription backend config."""
    api_key: str = ""
    model: str = "whisper-large-v3"


@dataclass
class LocalTranscriptionConfig:
    """Local transcription backend config."""
    model: str = "large-v3"
    device: Literal["cuda", "cpu"] = "cuda"


@dataclass
class TranscriptionConfig:
    """Transcription configuration."""
    backend: Literal["groq", "local"] = "groq"
    groq: GroqTranscriptionConfig = field(default_factory=GroqTranscriptionConfig)
    local: LocalTranscriptionConfig = field(default_factory=LocalTranscriptionConfig)


@dataclass
class GroqProcessingConfig:
    """Groq processing backend config."""
    model: str = "llama-3.1-8b-instant"


@dataclass
class LocalProcessingConfig:
    """Local processing backend config."""
    model: str = "llama3:8b"
    endpoint: str = "http://localhost:11434"


@dataclass
class ProcessingConfig:
    """Processing configuration."""
    backend: Literal["groq", "local"] = "groq"
    groq: GroqProcessingConfig = field(default_factory=GroqProcessingConfig)
    local: LocalProcessingConfig = field(default_factory=LocalProcessingConfig)


@dataclass
class OutputConfig:
    """Output configuration."""
    behavior: Literal["clipboard_only", "auto_paste"] = "auto_paste"


@dataclass
class HistoryConfig:
    """History configuration."""
    enabled: bool = True
    max_entries: int = 1000
    file: str = "history/history.jsonl"


@dataclass
class SoundsConfig:
    """Sounds configuration."""
    enabled: bool = True
    start: str = "sounds/start.wav"
    end: str = "sounds/end.wav"


@dataclass
class TrayConfig:
    """System tray configuration."""
    show_mode_tooltip: bool = True


@dataclass
class FeedbackConfig:
    """Feedback configuration."""
    sounds: SoundsConfig = field(default_factory=SoundsConfig)
    tray: TrayConfig = field(default_factory=TrayConfig)


@dataclass
class LanguageConfig:
    """Language configuration."""
    primary: str = "pt"
    secondary: str = "en"


@dataclass
class Config:
    """Main configuration."""
    audio: AudioConfig = field(default_factory=AudioConfig)
    hotkeys: HotkeyConfig = field(default_factory=HotkeyConfig)
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    mode: Literal["raw", "clean", "tech", "full"] = "full"
    vocabulary: list[str] = field(default_factory=list)
    output: OutputConfig = field(default_factory=OutputConfig)
    history: HistoryConfig = field(default_factory=HistoryConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    language: LanguageConfig = field(default_factory=LanguageConfig)


# === Helper Functions ===

def _expand_env_vars(value: str) -> str:
    """Expand environment variables in format ${VAR} or $VAR."""
    pattern = r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)'

    def replacer(match: re.Match) -> str:
        var_name = match.group(1) or match.group(2)
        return os.environ.get(var_name, "")

    return re.sub(pattern, replacer, value)


def _process_dict(data: dict) -> dict:
    """Recursively process dict, expanding env vars in string values."""
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = _process_dict(value)
        elif isinstance(value, str):
            result[key] = _expand_env_vars(value)
        elif isinstance(value, list):
            result[key] = [
                _expand_env_vars(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def _dict_to_dataclass(data: dict, cls: type) -> object:
    """Convert nested dict to dataclass instance."""
    if not hasattr(cls, "__dataclass_fields__"):
        return data

    field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}
    kwargs = {}

    for field_name, field_type in field_types.items():
        if field_name in data:
            value = data[field_name]

            # Handle nested dataclasses
            if hasattr(field_type, "__dataclass_fields__") and isinstance(value, dict):
                kwargs[field_name] = _dict_to_dataclass(value, field_type)
            else:
                kwargs[field_name] = value

    return cls(**kwargs)


# === Main Loader ===

def load_config(config_path: str | Path | None = None) -> Config:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, looks for config.yaml
                    in current directory or parent directories.

    Returns:
        Config object with all settings.

    Raises:
        FileNotFoundError: If config file not found.
        ValueError: If config file is invalid.
    """
    if config_path is None:
        # Look for config.yaml in current directory or project root
        search_paths = [
            Path.cwd() / "config.yaml",
            Path(__file__).parent.parent.parent / "config.yaml",
        ]
        for path in search_paths:
            if path.exists():
                config_path = path
                break
        else:
            raise FileNotFoundError(
                "config.yaml not found. Searched in:\n"
                + "\n".join(f"  - {p}" for p in search_paths)
            )

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        raw_data = yaml.safe_load(f) or {}

    # Expand environment variables
    data = _process_dict(raw_data)

    # Convert to dataclasses
    config = Config()

    if "audio" in data:
        config.audio = _dict_to_dataclass(data["audio"], AudioConfig)

    if "hotkeys" in data:
        config.hotkeys = _dict_to_dataclass(data["hotkeys"], HotkeyConfig)

    if "transcription" in data:
        trans_data = data["transcription"]
        config.transcription = TranscriptionConfig(
            backend=trans_data.get("backend", "groq"),
            groq=_dict_to_dataclass(trans_data.get("groq", {}), GroqTranscriptionConfig),
            local=_dict_to_dataclass(trans_data.get("local", {}), LocalTranscriptionConfig),
        )

    if "processing" in data:
        proc_data = data["processing"]
        config.processing = ProcessingConfig(
            backend=proc_data.get("backend", "groq"),
            groq=_dict_to_dataclass(proc_data.get("groq", {}), GroqProcessingConfig),
            local=_dict_to_dataclass(proc_data.get("local", {}), LocalProcessingConfig),
        )

    if "mode" in data:
        config.mode = data["mode"]

    if "vocabulary" in data:
        config.vocabulary = data["vocabulary"]

    if "output" in data:
        config.output = _dict_to_dataclass(data["output"], OutputConfig)

    if "history" in data:
        config.history = _dict_to_dataclass(data["history"], HistoryConfig)

    if "feedback" in data:
        feedback_data = data["feedback"]
        config.feedback = FeedbackConfig(
            sounds=_dict_to_dataclass(feedback_data.get("sounds", {}), SoundsConfig),
            tray=_dict_to_dataclass(feedback_data.get("tray", {}), TrayConfig),
        )

    if "language" in data:
        config.language = _dict_to_dataclass(data["language"], LanguageConfig)

    return config


def validate_config(config: Config) -> list[str]:
    """
    Validate configuration and return list of warnings/errors.

    Returns:
        List of warning/error messages. Empty list means valid.
    """
    issues = []

    # Check Groq API key if using Groq backend
    if config.transcription.backend == "groq":
        if not config.transcription.groq.api_key:
            issues.append(
                "Groq API key not set. Set GROQ_API_KEY environment variable "
                "or add it to config.yaml"
            )

    if config.processing.backend == "groq":
        if not config.transcription.groq.api_key:
            issues.append(
                "Groq API key required for processing but not set."
            )

    # Validate mode
    valid_modes = ["raw", "clean", "tech", "full"]
    if config.mode not in valid_modes:
        issues.append(f"Invalid mode '{config.mode}'. Must be one of: {valid_modes}")

    # Validate activation mode
    valid_activation = ["push_to_talk", "toggle"]
    if config.hotkeys.activation_mode not in valid_activation:
        issues.append(
            f"Invalid activation_mode '{config.hotkeys.activation_mode}'. "
            f"Must be one of: {valid_activation}"
        )

    return issues


def get_config_path() -> Path:
    """Get the default config file path."""
    return Path(__file__).parent.parent.parent / "config.yaml"
