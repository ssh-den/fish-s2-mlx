"""Memory cleanup helpers for MLX-based generation."""

from __future__ import annotations

import gc

import mlx.core as mx


def clear_memory() -> None:
    """Release Python objects and clear the MLX cache when available."""
    gc.collect()
    try:
        mx.clear_cache()
    except Exception:
        # MLX cache cleanup is best effort and should not break generation.
        pass
