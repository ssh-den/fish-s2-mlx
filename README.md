# Fish S2 MLX Tool

A minimal local text-to-speech and voice cloning interface powered by MLX Speech and Gradio.

The project is designed mainly for macOS with Apple Silicon, where MLX is supported. It may also run on other systems supported by the underlying libraries, but MLX Speech compatibility is the real limit.

This is an unofficial community tool and is not affiliated with Fish Audio.

## Features

- Local text-to-speech generation.
- Voice cloning from reference audio and transcript.
- Fish S2 / S2 Pro model selection.
- Custom Hugging Face model ID or local model path.
- Automatic text chunking for long input.
- Seed control for repeatable generation.
- Hugging Face cache path configuration.
- Fish model cache listing and cleanup.

## Project structure

```text
fish-s2-mlx/
├── app.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── NOTICE
└── src/
    └── fish_s2_mlx/
        ├── app.py
        ├── audio.py
        ├── cache.py
        ├── config.py
        ├── constants.py
        ├── generator.py
        ├── memory.py
        ├── model_manager.py
        ├── settings.py
        ├── text.py
        └── ui.py
```

## Installation

Use Python 3.11 or newer.

```bash
git clone <https://github.com/ssh-den/fish-s2-mlx>
cd fish-s2-mlx
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

On Apple Silicon macOS, make sure your Python environment is running natively on arm64, not through Rosetta.

## Run

Development launcher:

```bash
python app.py
```

Module launcher:

```bash
python -m fish_s2_mlx.app
```

The app opens Gradio at the configured host and port. By default:

```text
http://127.0.0.1:7860
```

## Configuration

The config file is stored at:

```text
~/.fish_s2_mlx/config.json
```

The app saves generation settings automatically before each run. You can also save settings manually from the UI.

## Hugging Face cache

By default, models are stored in:

```text
~/.cache/huggingface/hub
```

You can set a custom cache path in the UI. Restart the app after changing it so `HF_HOME` and `HF_HUB_CACHE` are applied before model loading.

## Voice cloning workflow

1. Choose **Voice cloning from reference**.
2. Upload or record reference audio.
3. Paste the exact transcript of the reference audio.
4. Enter the target text.
5. Generate speech.

Reference transcript quality matters. The transcript should match the spoken reference audio as closely as possible.

## Notes

- First generation can be slow because the model may need to download and initialize.
- Long text is split into chunks, generated separately, then joined with a configurable pause.
- Cache cleanup deletes local model files. Deleted models will be downloaded again when needed.
- The tool does not bypass model licensing or usage restrictions. Check the model license before publishing generated audio.

## License / Credits

This project's source code is licensed under the MIT License.

This project does not include Fish Audio model weights. Fish Audio / Fish Speech / S2 / S2 Pro models are licensed separately under the Fish Audio Research License. Research and non-commercial use is permitted free of charge; commercial use requires a separate license from Fish Audio. Check the current license terms before publishing, redistributing, or using generated audio in a commercial context.

Built with Fish Audio.

Required Fish Audio notice:

```text
This model is licensed under the Fish Audio Research License, Copyright © 39 AI, INC. All Rights Reserved.
```

Relevant upstream resources:

- Fish Speech repository license: https://github.com/fishaudio/fish-speech/blob/main/LICENSE
- Fish Audio S2 Pro model page: https://huggingface.co/fishaudio/s2-pro
- Fish Audio terms: https://fish.audio/terms/

Users are responsible for complying with applicable law, model licenses, consent requirements for voice cloning, and Fish Audio usage policies. Do not clone a voice unless you have the right to do so.
