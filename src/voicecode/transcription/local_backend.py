"""Local transcription backend using faster-whisper."""

from __future__ import annotations

import io
import tempfile
import os
from pathlib import Path

from .base import BaseTranscriber


class LocalTranscriber(BaseTranscriber):
    """
    Local transcription using faster-whisper.

    Runs entirely offline using your GPU (CUDA) or CPU.
    First run will download the model (~3GB for large-v3).
    """

    def __init__(
        self,
        model: str = "large-v3",
        device: str = "cuda",
        compute_type: str = "float16",
    ):
        """
        Initialize local transcriber.

        Args:
            model: Whisper model size (tiny, base, small, medium, large-v3)
            device: Device to use (cuda, cpu)
            compute_type: Computation type (float16, int8, float32)
        """
        self.model_name = model
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _get_model(self):
        """Lazy load the model."""
        if self._model is None:
            from faster_whisper import WhisperModel

            print(f"[LocalTranscriber] Loading model '{self.model_name}' on {self.device}...")

            # Adjust compute type for CPU
            compute_type = self.compute_type
            if self.device == "cpu" and compute_type == "float16":
                compute_type = "int8"

            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=compute_type,
            )
            print(f"[LocalTranscriber] Model loaded successfully")

        return self._model

    def transcribe(self, audio: bytes, language: str = "pt") -> str:
        """
        Transcribe audio locally.

        Args:
            audio: WAV audio bytes
            language: Language code

        Returns:
            Transcribed text
        """
        if not audio:
            return ""

        model = self._get_model()

        # Save audio to temp file (faster-whisper needs a file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio)
            temp_path = f.name

        try:
            segments, info = model.transcribe(
                temp_path,
                language=language,
                beam_size=5,
                vad_filter=True,  # Filter out silence
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                ),
            )

            # Combine all segments
            text = " ".join(segment.text.strip() for segment in segments)
            return text.strip()

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception:
                pass

    def is_available(self) -> bool:
        """Check if local transcription is available."""
        try:
            import faster_whisper
            return True
        except ImportError:
            return False

    def check_cuda(self) -> bool:
        """Check if CUDA is available."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            # Try ctranslate2 check
            try:
                import ctranslate2
                return "cuda" in ctranslate2.get_supported_compute_types()
            except Exception:
                return False
