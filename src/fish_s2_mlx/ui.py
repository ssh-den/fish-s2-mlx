"""Gradio user interface for Fish S2 MLX."""

from __future__ import annotations

import gradio as gr

from .cache import (
    clear_all_hf_cache,
    clear_fish_models_cache,
    list_cached_models,
    save_cache_settings,
)
from .config import CONFIG_PATH, load_config
from .constants import (
    GENERATION_MODE_STANDARD,
    GENERATION_MODES,
    MODEL_OPTIONS,
    STYLE_TAGS,
)
from .generator import generate_speech, random_seed
from .model_manager import model_manager
from .settings import save_ui_config


def build_demo() -> gr.Blocks:
    """Build and wire the Gradio application."""
    config = load_config()

    with gr.Blocks(title="Fish S2 MLX") as demo:
        gr.Markdown(
            "# Fish S2 MLX\n"
            "Minimal local TTS and voice cloning UI powered by MLX Speech."
        )

        with gr.Tabs():
            with gr.Tab("Generate"):
                with gr.Row():
                    with gr.Column(scale=2):
                        text_input = gr.Textbox(
                            label="Text to synthesize",
                            placeholder="Write your text here...",
                            lines=8,
                            value=config.get("text", ""),
                        )

                        generation_mode = gr.Radio(
                            choices=GENERATION_MODES,
                            value=config.get(
                                "generation_mode", GENERATION_MODE_STANDARD
                            ),
                            label="Generation mode",
                        )

                        ref_audio = gr.Audio(
                            label="Reference audio for voice cloning",
                            type="filepath",
                            sources=["upload", "microphone"],
                        )

                        ref_text = gr.Textbox(
                            label="Reference audio transcript",
                            lines=3,
                            placeholder="Required only for voice cloning.",
                        )

                    with gr.Column(scale=1):
                        model_choice = gr.Dropdown(
                            choices=list(MODEL_OPTIONS.keys()),
                            value=config.get("model_choice", "Fish S2 Pro"),
                            label="Model",
                        )

                        custom_model_id = gr.Textbox(
                            label="Custom model / Hugging Face ID",
                            placeholder="Example: username/model-name or a local path",
                            value=config.get("custom_model_id", ""),
                        )

                        load_btn = gr.Button("Load / download model")
                        unload_btn = gr.Button("Unload model")

                        model_status = gr.Textbox(
                            label="Model status",
                            interactive=False,
                            lines=3,
                        )

                        temp = gr.Slider(
                            0.3,
                            1.0,
                            value=float(config.get("temperature", 0.7)),
                            step=0.05,
                            label="Temperature",
                        )

                        top_p_slider = gr.Slider(
                            0.5,
                            1.0,
                            value=float(config.get("top_p", 0.9)),
                            step=0.05,
                            label="Top-p",
                        )

                        max_chars = gr.Slider(
                            80,
                            500,
                            value=int(config.get("max_chars", 220)),
                            step=10,
                            label="Chunk size, characters",
                        )

                        pause_sec = gr.Slider(
                            0.0,
                            1.0,
                            value=float(config.get("pause_sec", 0.25)),
                            step=0.05,
                            label="Pause between chunks, sec.",
                        )

                        use_random_seed = gr.Checkbox(
                            value=bool(config.get("use_random_seed", True)),
                            label="Use a random seed for each generation",
                        )

                        seed_input = gr.Number(
                            value=int(config.get("seed_value", random_seed())),
                            precision=0,
                            label="Manual seed",
                        )

                        new_seed_btn = gr.Button("New random seed")

                        generate_btn = gr.Button(
                            "Generate speech",
                            variant="primary",
                            size="large",
                        )

                        output_audio = gr.Audio(label="Result", autoplay=True)

                        status_box = gr.Textbox(
                            label="Status",
                            interactive=False,
                            lines=10,
                        )

                gr.Markdown(
                    """
### Modes

**Standard TTS**
Generates speech without a reference voice. The model chooses the voice internally.

**Voice cloning from reference**
Uses reference audio and its exact transcript to transfer the speaker characteristics.

### Supported style / emotion tags

You can insert these tags directly into the text:

"""
                    + "`, `".join([f"{tag}" for tag in STYLE_TAGS]).join(["`", "`"])
                    + """

### Chunking logic

The app fills each chunk close to the character limit, then searches for a good split point:

1. comma;
2. period;
3. whitespace;
4. hard cut only when no separator exists.
"""
                )

            with gr.Tab("Settings"):
                gr.Markdown(
                    f"""
Config file:

`{CONFIG_PATH}`

Settings are saved automatically before generation. You can also save them manually.
"""
                )

                cache_dir_input = gr.Textbox(
                    label="Hugging Face cache path",
                    value=config.get("cache_dir", ""),
                    placeholder="Empty = default ~/.cache/huggingface/hub",
                )

                server_name_input = gr.Textbox(
                    label="Server name",
                    value=config.get("server_name", "127.0.0.1"),
                )

                server_port_input = gr.Number(
                    label="Server port",
                    value=int(config.get("server_port", 7860)),
                    precision=0,
                )

                inbrowser_input = gr.Checkbox(
                    label="Open browser on launch",
                    value=bool(config.get("inbrowser", True)),
                )

                save_config_btn = gr.Button("Save settings")
                save_config_status = gr.Textbox(
                    label="Status", interactive=False, lines=4
                )

                save_config_btn.click(
                    fn=save_ui_config,
                    inputs=[
                        text_input,
                        generation_mode,
                        model_choice,
                        custom_model_id,
                        temp,
                        top_p_slider,
                        max_chars,
                        pause_sec,
                        seed_input,
                        use_random_seed,
                        cache_dir_input,
                        server_name_input,
                        server_port_input,
                        inbrowser_input,
                    ],
                    outputs=save_config_status,
                )

            with gr.Tab("Models / cache"):
                cache_info = gr.Textbox(
                    label="Model cache information",
                    lines=18,
                    interactive=False,
                )

                refresh_cache_btn = gr.Button("Refresh Fish model list")
                save_cache_btn = gr.Button("Save cache path")
                clear_fish_btn = gr.Button("Delete only Fish models")
                clear_all_cache_btn = gr.Button(
                    "Delete entire Hugging Face cache", variant="stop"
                )

                gr.Markdown(
                    """
### Where models are stored

If the cache path is empty, the default path is used:

`~/.cache/huggingface/hub`

If you set a custom path, the app exports `HF_HOME` and `HF_HUB_CACHE` on startup.
Restart the app after changing the cache path.

Cache size is estimated with `du -sk` when available, because Hugging Face snapshots often use symlinks.
"""
                )

                refresh_cache_btn.click(
                    fn=list_cached_models, inputs=None, outputs=cache_info
                )
                save_cache_btn.click(
                    fn=save_cache_settings, inputs=cache_dir_input, outputs=cache_info
                )
                clear_fish_btn.click(
                    fn=clear_fish_models_cache, inputs=None, outputs=cache_info
                )
                clear_all_cache_btn.click(
                    fn=clear_all_hf_cache, inputs=None, outputs=cache_info
                )

        load_btn.click(
            fn=model_manager.load,
            inputs=[model_choice, custom_model_id],
            outputs=model_status,
        )
        unload_btn.click(fn=model_manager.unload, inputs=None, outputs=model_status)
        new_seed_btn.click(fn=random_seed, inputs=None, outputs=seed_input)
        generate_btn.click(
            fn=generate_speech,
            inputs=[
                text_input,
                generation_mode,
                ref_audio,
                ref_text,
                model_choice,
                custom_model_id,
                temp,
                top_p_slider,
                max_chars,
                pause_sec,
                seed_input,
                use_random_seed,
                cache_dir_input,
            ],
            outputs=[output_audio, status_box],
        )

    return demo
