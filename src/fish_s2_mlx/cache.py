"""Hugging Face cache inspection and cleanup."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .config import CONFIG_PATH, format_size, get_hf_cache_dir, load_config, save_config
from .memory import clear_memory
from .model_manager import model_manager


def folder_size(path: str | Path) -> int:
    """Return disk usage in bytes, preferring `du` to avoid HF symlink over-counting."""
    resolved = Path(path).expanduser()
    if not resolved.exists():
        return 0

    try:
        result = subprocess.check_output(
            ["du", "-sk", str(resolved)],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return int(result.split()[0]) * 1024
    except Exception:
        total = 0
        seen_inodes: set[tuple[int, int]] = set()

        for file in resolved.rglob("*"):
            try:
                stat = file.lstat()
                if file.is_symlink():
                    continue

                inode_key = (stat.st_dev, stat.st_ino)
                if inode_key in seen_inodes:
                    continue

                seen_inodes.add(inode_key)
                if file.is_file():
                    total += stat.st_size
            except OSError:
                continue

        return total


def is_fish_model_cache_dir(path: Path) -> bool:
    """Detect likely Fish Speech cache folders by their Hugging Face cache name."""
    name = path.name.lower()
    return "fish" in name or "fishaudio" in name


def list_cached_models() -> str:
    """List cached Fish Speech models and their approximate disk usage."""
    cache_dir = get_hf_cache_dir(load_config())
    if not cache_dir.exists():
        return f"Cache directory was not found:\n{cache_dir}"

    rows: list[str] = []
    total = 0

    for item in sorted(cache_dir.iterdir()):
        if item.is_dir() and is_fish_model_cache_dir(item):
            size = folder_size(item)
            total += size
            rows.append(f"{item.name}\n  {format_size(size)}\n  {item}")

    if not rows:
        return f"No Fish Speech models found.\n\nCache path:\n{cache_dir}"

    return (
        f"Cache path:\n{cache_dir}\n\n"
        f"Total Fish Speech model cache size: {format_size(total)}\n\n"
        + "\n\n".join(rows)
    )


def clear_fish_models_cache() -> str:
    """Remove only cached Fish Speech model folders."""
    model_manager.unload(silent=True)
    cache_dir = get_hf_cache_dir(load_config())

    if not cache_dir.exists():
        return f"Cache directory was not found:\n{cache_dir}"

    removed: list[str] = []
    freed = 0

    for item in sorted(cache_dir.iterdir()):
        if item.is_dir() and is_fish_model_cache_dir(item):
            freed += folder_size(item)
            shutil.rmtree(item, ignore_errors=True)
            removed.append(item.name)

    clear_memory()

    if not removed:
        return f"No Fish Speech model cache folders were found.\n\nPath:\n{cache_dir}"

    return (
        f"Removed models: {len(removed)}\n"
        f"Approx. freed space: {format_size(freed)}\n\n"
        + "\n".join(removed)
    )


def clear_all_hf_cache() -> str:
    """Remove the whole configured Hugging Face cache directory."""
    model_manager.unload(silent=True)
    cache_dir = get_hf_cache_dir(load_config())

    if not cache_dir.exists():
        return f"Cache directory was not found:\n{cache_dir}"

    size = folder_size(cache_dir)
    shutil.rmtree(cache_dir, ignore_errors=True)
    clear_memory()

    return (
        "The entire Hugging Face cache has been removed.\n"
        f"Approx. freed space: {format_size(size)}\n\n"
        f"Path:\n{cache_dir}"
    )


def save_cache_settings(cache_dir: str | None) -> str:
    """Persist a custom Hugging Face cache path."""
    config = load_config()
    config["cache_dir"] = cache_dir.strip() if cache_dir else ""
    save_config(config)

    return (
        f"Cache path saved to:\n{CONFIG_PATH}\n\n"
        "Restart the app to make sure model loaders use the new cache path."
    )
