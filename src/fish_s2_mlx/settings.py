"""UI callbacks for saving application settings."""

from __future__ import annotations

from .config import CONFIG_PATH, load_config, save_config


def save_ui_config(
    text: str,
    generation_mode: str,
    model_choice: str,
    custom_model_id: str,
    temperature: float,
    top_p: float,
    max_chars: int,
    pause_sec: float,
    seed_value: int,
    use_random_seed: bool,
    cache_dir: str,
    server_name: str,
    server_port: int,
    inbrowser: bool,
) -> str:
    """Persist all user-editable settings from the Gradio interface."""
    config = load_config()
    config.update(
        {
            "text": text,
            "generation_mode": generation_mode,
            "model_choice": model_choice,
            "custom_model_id": custom_model_id,
            "temperature": float(temperature),
            "top_p": float(top_p),
            "max_chars": int(max_chars),
            "pause_sec": float(pause_sec),
            "seed_value": int(seed_value),
            "use_random_seed": bool(use_random_seed),
            "cache_dir": cache_dir.strip() if cache_dir else "",
            "server_name": server_name.strip() if server_name else "127.0.0.1",
            "server_port": int(server_port),
            "inbrowser": bool(inbrowser),
        }
    )
    save_config(config)
    return f"Config saved:\n{CONFIG_PATH}"
