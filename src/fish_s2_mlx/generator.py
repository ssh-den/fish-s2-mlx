"""Speech generation workflow."""

from __future__ import annotations

import os
import random
import tempfile
import time
from pathlib import Path

import mlx.core as mx
import soundfile as sf

from .audio import concat_audio_files
from .config import CONFIG_PATH, load_config, save_config
from .constants import GENERATION_MODE_CLONE
from .memory import clear_memory
from .model_manager import model_manager
from .text import split_text


def random_seed() -> int:
    """Generate a seed that fits common 32-bit signed integer constraints."""
    return random.randint(1, 2_147_483_647)


def save_generation_config(
    *,
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
) -> None:
    """Persist the current generation options before running TTS."""
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
        }
    )
    save_config(config)


def _remove_files(paths: list[str | Path]) -> None:
    """Delete temporary files, ignoring cleanup errors."""
    for path in paths:
        try:
            os.remove(path)
        except OSError:
            pass


def generate_speech(
    text: str,
    generation_mode: str,
    reference_audio: str | None,
    reference_text: str | None,
    model_choice: str,
    custom_model_id: str,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_chars: int = 220,
    pause_sec: float = 0.25,
    seed_value: int | None = None,
    use_random_seed: bool = True,
    cache_dir: str = "",
) -> tuple[str | None, str]:
    """Generate speech from text and optionally clone a voice from reference audio."""
    if not text or not text.strip():
        return None, "Enter text to synthesize."

    is_cloning = generation_mode == GENERATION_MODE_CLONE
    if is_cloning and not reference_audio:
        return None, "Reference audio is required for voice cloning."
    if is_cloning and (not reference_text or not reference_text.strip()):
        return None, "Reference audio transcript is required for voice cloning."

    temp_files: list[str] = []

    try:
        seed = random_seed() if use_random_seed else int(seed_value or 1)
        save_generation_config(
            text=text,
            generation_mode=generation_mode,
            model_choice=model_choice,
            custom_model_id=custom_model_id,
            temperature=temperature,
            top_p=top_p,
            max_chars=max_chars,
            pause_sec=pause_sec,
            seed_value=seed,
            use_random_seed=use_random_seed,
            cache_dir=cache_dir,
        )

        model = model_manager.ensure_loaded(model_choice, custom_model_id)
        chunks = split_text(text, int(max_chars))
        if not chunks:
            return None, "Text could not be split into chunks."

        start_time = time.time()
        wav_paths: list[str] = []

        for index, chunk in enumerate(chunks, start=1):
            try:
                mx.random.seed(seed)
            except Exception:
                pass

            generate_kwargs = {
                "text": chunk,
                "temperature": float(temperature),
                "top_p": float(top_p),
            }

            if is_cloning:
                generate_kwargs["reference_audio"] = reference_audio
                generate_kwargs["reference_text"] = reference_text.strip()

            result = model.generate(**generate_kwargs)

            chunk_path = tempfile.NamedTemporaryFile(
                suffix=f"_chunk_{index}.wav",
                delete=False,
            ).name
            temp_files.append(chunk_path)
            sf.write(chunk_path, result.waveform, result.sample_rate)
            wav_paths.append(chunk_path)
            clear_memory()

        output_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        concat_audio_files(wav_paths, output_path, float(pause_sec))
        _remove_files(temp_files)

        duration = time.time() - start_time
        chunk_sizes = [len(chunk) for chunk in chunks]

        return (
            output_path,
            "Done.\n"
            f"Mode: {generation_mode}\n"
            f"Model: {model_manager.current_model_id}\n"
            f"Seed: {seed}\n"
            f"Random seed: {'yes' if use_random_seed else 'no'}\n"
            f"Chunks: {len(chunks)}\n"
            f"Chunk limit: {max_chars} characters\n"
            f"Chunk sizes: {chunk_sizes}\n"
            f"Generation time: {duration:.1f} sec.\n"
            f"Config saved: {CONFIG_PATH}",
        )

    except Exception as error:
        _remove_files(temp_files)
        clear_memory()
        return None, f"Error: {error}"
