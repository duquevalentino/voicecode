# VoiceCode

Voice-to-text transcription tool for coding, similar to Wispr Flow/Superwhisper but open-source and DIY.

Dictate instructions to AI coding assistants (Claude Code, Gemini CLI) instead of typing.

## Features

- **Push-to-talk** or **toggle** recording modes
- **4 processing modes**: raw, clean, tech, full
- **Context injection**: include clipboard content as context
- **Dual backend support**: Groq API (cloud) or local (Whisper + Ollama)
- **System tray** with visual state feedback
- **Sound feedback** on recording start/stop
- **Configurable hotkeys**
- **History logging**

## Requirements

- Windows 10/11
- Python 3.10+
- NVIDIA GPU (optional, for local backend)
- Microphone

## Installation

### 1. Clone and setup environment

```bash
git clone <repo-url>
cd voicecode

# Create conda environment
conda create -n voicecode python=3.11
conda activate voicecode

# Install package
pip install -e .
```

### 2. Configure API key (for Groq backend)

Create a `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

Get your API key at: https://console.groq.com

### 3. (Optional) Install local backend

For offline usage with local Whisper + Ollama:

```bash
# Install Ollama: https://ollama.ai
ollama pull llama3:8b

# faster-whisper is already included
```

## Usage

### Start the application

```bash
python -m voicecode
```

### Hotkeys

| Hotkey | Action |
|--------|--------|
| `Ctrl+Shift+Space` | Start/stop recording |
| `Alt+Ctrl+Shift+Space` | Record with context (clipboard) |
| `Ctrl+Shift+M` | Cycle processing modes |

### Processing Modes

| Mode | Description |
|------|-------------|
| `raw` | No processing, just transcription |
| `clean` | Remove filler words (hm, uh, tipo, então) |
| `tech` | Format technical terms (camelCase, React, etc.) |
| `full` | Clean + Tech combined |

### System Tray

| Color | State |
|-------|-------|
| Gray | Idle, ready |
| Red | Recording |
| Yellow | Processing |
| Green | Done |

## Configuration

Edit `config.yaml`:

```yaml
# Audio device (null = Windows default)
audio:
  device: null  # or "Fifine", or device index

# Hotkeys
hotkeys:
  activation_mode: "push_to_talk"  # or "toggle"
  main_key: "ctrl+shift+space"
  context_modifier: "alt"
  cycle_mode_key: "ctrl+shift+m"

# Backend: "groq" (cloud) or "local" (offline)
transcription:
  backend: "groq"

processing:
  backend: "groq"

# Processing mode
mode: "full"

# Output behavior
output:
  behavior: "auto_paste"  # or "clipboard_only"
```

## Backend Comparison

| Feature | Groq (Cloud) | Local |
|---------|--------------|-------|
| Speed | ~1s | ~2-3s |
| Privacy | Data sent to API | 100% offline |
| Cost | Free tier available | Free (your GPU) |
| Requirements | Internet | NVIDIA GPU + Ollama |

## Troubleshooting

### Microphone not working

1. Check Windows Settings > System > Sound > Input
2. Set correct default microphone
3. Or specify device in `config.yaml`:
   ```yaml
   audio:
     device: "Fifine"  # Part of device name
   ```

### Groq API errors

1. Verify API key in `.env`
2. Check internet connection
3. Verify at https://console.groq.com

### Ollama timeout

First run loads the model (~30s). Subsequent runs are faster.

If still slow:
```yaml
processing:
  local:
    model: "llama3.2:3b"  # Smaller, faster model
```

### Hotkey not working

Run as Administrator (required for global hotkeys on Windows).

## Project Structure

```
voicecode/
├── src/voicecode/
│   ├── __main__.py      # Entry point
│   ├── config.py        # Configuration
│   ├── audio/           # Recording
│   ├── transcription/   # Whisper (Groq/local)
│   ├── processing/      # LLM (Groq/Ollama)
│   ├── output/          # Clipboard
│   ├── ui/              # Tray + sounds
│   └── hotkeys/         # Key listener
├── config.yaml          # User config
├── .env                 # API keys
└── history/             # Transcription logs
```

## License

MIT
