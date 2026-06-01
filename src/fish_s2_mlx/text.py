"""Text normalization and chunking helpers."""

from __future__ import annotations

import re


def split_text(text: str, max_chars: int = 220) -> list[str]:
    """Split text into speech-friendly chunks without cutting words when possible."""
    normalized = re.sub(r"\s+", " ", text.strip())
    chunks: list[str] = []

    while len(normalized) > max_chars:
        window = normalized[:max_chars]
        split_pos = max(window.rfind(", "), window.rfind(". "), window.rfind(" "))

        if split_pos == -1:
            split_pos = max_chars

        chunk = normalized[:split_pos].strip()
        if not chunk:
            chunk = normalized[:max_chars].strip()
            split_pos = max_chars

        chunks.append(chunk)
        normalized = normalized[split_pos:].strip()

    if normalized:
        chunks.append(normalized)

    return chunks
