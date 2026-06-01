"""Application constants used by the Fish S2 MLX UI and backend."""

MODEL_OPTIONS: dict[str, str] = {
    "Fish S2 Pro": "fish-s2-pro",
    "Fish S2 Pro 8-bit MLX": "mlx-community/fishaudio-s2-pro-8bit-mlx",
    "Fish S2 Lite": "fish-s2",
    "Custom model / Hugging Face ID": "__custom__",
}

CUSTOM_MODEL_LABEL = "Custom model / Hugging Face ID"

GENERATION_MODE_STANDARD = "Standard TTS"
GENERATION_MODE_CLONE = "Voice cloning from reference"

GENERATION_MODES = [
    GENERATION_MODE_STANDARD,
    GENERATION_MODE_CLONE,
]

STYLE_TAGS = [
    "[angry]",
    "[sad]",
    "[excited]",
    "[surprised]",
    "[satisfied]",
    "[delighted]",
    "[scared]",
    "[worried]",
    "[upset]",
    "[nervous]",
    "[frustrated]",
    "[depressed]",
    "[empathetic]",
    "[embarrassed]",
    "[disgusted]",
    "[moved]",
    "[proud]",
    "[relaxed]",
    "[grateful]",
    "[confident]",
    "[interested]",
    "[curious]",
    "[confused]",
    "[joyful]",
    "[whispering]",
    "[shouting]",
    "[screaming]",
    "[laughing]",
    "[chuckling]",
    "[sobbing]",
    "[crying loudly]",
    "[sighing]",
    "[panting]",
    "[groaning]",
    "[crowd laughing]",
    "[background laughter]",
    "[audience laughing]",
    "[clears throat]",
]
