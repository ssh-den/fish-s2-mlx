"""Audio file operations."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf


def concat_audio_files(
    wav_paths: list[str | Path],
    output_path: str | Path,
    pause_sec: float = 0.25,
) -> Path:
    """Concatenate WAV files and insert silence between generated chunks."""
    final_parts: list[np.ndarray] = []
    sample_rate: int | None = None

    for path in wav_paths:
        audio, sr = sf.read(path)

        if sample_rate is None:
            sample_rate = sr
        elif sr != sample_rate:
            raise ValueError(f"Chunk sample rates differ: {sample_rate} and {sr}")

        final_parts.append(audio)
        pause_length = int(sr * pause_sec)

        if audio.ndim == 1:
            pause = np.zeros(pause_length, dtype=audio.dtype)
        else:
            pause = np.zeros((pause_length, audio.shape[1]), dtype=audio.dtype)

        final_parts.append(pause)

    if sample_rate is None or not final_parts:
        raise ValueError("No audio chunks were provided.")

    final_audio = np.concatenate(final_parts, axis=0)
    output = Path(output_path)
    sf.write(output, final_audio, sample_rate)
    return output
