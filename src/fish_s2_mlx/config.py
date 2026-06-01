"""Configuration loading, saving, and Hugging Face cache setup."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

APP_DIR = Path.home() / ".fish_s2_mlx"
CONFIG_PATH = APP_DIR / "config.json"
DEFAULT_HF_CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub"

DEFAULT_CONFIG: dict[str, Any] = {
    "text": "",
    "generation_mode": "Standard TTS",
    "model_choice": "Fish S2 Pro",
    "custom_model_id": "",
    "temperature": 0.7,
    "top_p": 0.9,
    "max_chars": 220,
    "pause_sec": 0.25,
    "seed_value": 123456,
    "use_random_seed": True,
    "cache_dir": "",
    "server_name": "127.0.0.1",
    "server_port": 7860,
    "inbrowser": True,
}


def load_config() -> dict[str, Any]:
    """Load the persisted app configuration and merge it with defaults."""
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as file:
            loaded = json.load(file)
    except (OSError, json.JSONDecodeError):
        return DEFAULT_CONFIG.copy()

    config = DEFAULT_CONFIG.copy()
    config.update(loaded)
    return config


def save_config(config: dict[str, Any]) -> None:
    """Persist the app configuration as readable JSON."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=2)


def get_hf_cache_dir(config: dict[str, Any] | None = None) -> Path:
    """Return the configured Hugging Face cache directory."""
    config = config or load_config()
    configured_path = str(config.get("cache_dir", "")).strip()
    if configured_path:
        return Path(configured_path).expanduser()
    return DEFAULT_HF_CACHE_DIR


def set_cache_env_from_config(config: dict[str, Any] | None = None) -> None:
    """Set Hugging Face cache environment variables before model libraries import."""
    cache_dir = get_hf_cache_dir(config)
    os.environ["HF_HOME"] = str(cache_dir.parent)
    os.environ["HF_HUB_CACHE"] = str(cache_dir)


def format_size(size_bytes: int) -> str:
    """Format a byte count using compact binary units."""
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size_bytes)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} {unit}"
        value /= 1024
    return f"{value:.1f} TB"
