"""Application entry point."""

from __future__ import annotations

# Cache variables must be set before importing the UI, because the UI imports MLX Speech.
from .config import load_config, set_cache_env_from_config

config = load_config()
set_cache_env_from_config(config)

from .ui import build_demo  # noqa: E402


def main() -> None:
    """Launch the Gradio app."""
    latest_config = load_config()
    demo = build_demo()
    demo.launch(
        server_name=latest_config.get("server_name", "127.0.0.1"),
        server_port=int(latest_config.get("server_port", 7860)),
        share=False,
        inbrowser=bool(latest_config.get("inbrowser", True)),
        show_error=True,
    )


if __name__ == "__main__":
    main()
