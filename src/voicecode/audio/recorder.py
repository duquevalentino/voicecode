"""Audio recorder using sounddevice."""

from __future__ import annotations

import io
import threading
from typing import Callable

import numpy as np
import sounddevice as sd
from scipy.io import wavfile


class AudioRecorder:
    """
    Records audio from a microphone.

    Usage:
        recorder = AudioRecorder(device="Fifine")
        recorder.start_recording()
        # ... user speaks ...
        audio_bytes = recorder.stop_recording()  # Returns WAV bytes
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = "int16",
        device: str | int | None = None,
        on_error: Callable[[Exception], None] | None = None,
    ):
        """
        Initialize the audio recorder.

        Args:
            sample_rate: Sample rate in Hz (16000 is good for speech)
            channels: Number of audio channels (1 = mono)
            dtype: Audio data type
            device: Device name (partial match), index, or None for default
            on_error: Callback for errors during recording
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.on_error = on_error

        # Resolve device
        self._device_id = self._resolve_device(device)

        self._recording = False
        self._audio_data: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    def _resolve_device(self, device: str | int | None) -> int | None:
        """Resolve device name or index to device ID."""
        if device is None:
            return None

        if isinstance(device, int):
            return device

        # Search by name (partial match, case-insensitive)
        device_lower = device.lower()
        devices = sd.query_devices()

        for i, d in enumerate(devices):
            if d['max_input_channels'] > 0 and device_lower in d['name'].lower():
                return i

        # Not found, return None to use default
        return None

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags,
    ) -> None:
        """Callback called by sounddevice for each audio block."""
        if status and self.on_error:
            self.on_error(Exception(f"Audio callback status: {status}"))

        if self._recording:
            with self._lock:
                self._audio_data.append(indata.copy())

    def start_recording(self) -> None:
        """Start recording audio from the microphone."""
        if self._recording:
            return

        with self._lock:
            self._audio_data = []

        self._recording = True

        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                device=self._device_id,
                callback=self._audio_callback,
            )
            self._stream.start()
        except Exception as e:
            self._recording = False
            if self.on_error:
                self.on_error(e)
            raise

    def stop_recording(self) -> bytes:
        """
        Stop recording and return the audio as WAV bytes.

        Returns:
            WAV file as bytes, ready to send to transcription API.
        """
        if not self._recording:
            return b""

        self._recording = False

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            if not self._audio_data:
                return b""

            # Concatenate all audio chunks
            audio_array = np.concatenate(self._audio_data, axis=0)
            self._audio_data = []

        # Convert to WAV bytes
        return self._array_to_wav_bytes(audio_array)

    def _array_to_wav_bytes(self, audio_array: np.ndarray) -> bytes:
        """Convert numpy array to WAV bytes."""
        buffer = io.BytesIO()
        wavfile.write(buffer, self.sample_rate, audio_array)
        buffer.seek(0)
        return buffer.read()

    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._recording

    def cancel_recording(self) -> None:
        """Cancel recording without returning data."""
        self._recording = False

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        with self._lock:
            self._audio_data = []


def get_audio_devices() -> list[dict]:
    """Get list of available audio input devices."""
    devices = sd.query_devices()
    input_devices = []

    for i, device in enumerate(devices):
        if device["max_input_channels"] > 0:
            input_devices.append({
                "index": i,
                "name": device["name"],
                "channels": device["max_input_channels"],
                "sample_rate": device["default_samplerate"],
            })

    return input_devices


def get_default_input_device() -> dict | None:
    """Get the default audio input device."""
    try:
        device_index = sd.default.device[0]
        if device_index is None:
            return None

        device = sd.query_devices(device_index)
        return {
            "index": device_index,
            "name": device["name"],
            "channels": device["max_input_channels"],
            "sample_rate": device["default_samplerate"],
        }
    except Exception:
        return None
