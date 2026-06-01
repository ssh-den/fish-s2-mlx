"""Model loading, unloading, and model ID resolution."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import mlx_speech

from .constants import CUSTOM_MODEL_LABEL, MODEL_OPTIONS
from .memory import clear_memory


@dataclass
class ModelManager:
    """Keeps one MLX Speech model in memory and reloads when needed."""

    model: Any | None = None
    current_model_id: str | None = None

    def resolve_model_id(self, model_choice: str, custom_model_id: str | None) -> str:
        """Resolve a UI model choice to a real model identifier or local path."""
        if model_choice == CUSTOM_MODEL_LABEL:
            if not custom_model_id or not custom_model_id.strip():
                raise ValueError("Enter a Hugging Face model ID or a local model path.")
            return custom_model_id.strip()

        try:
            return MODEL_OPTIONS[model_choice]
        except KeyError as error:
            raise ValueError(f"Unknown model choice: {model_choice}") from error

    def load(self, model_choice: str, custom_model_id: str | None = "") -> str:
        """Load the selected model, unloading the previous model if necessary."""
        model_id = self.resolve_model_id(model_choice, custom_model_id)

        if self.model is not None and self.current_model_id == model_id:
            return f"Model is already loaded: {model_id}"

        self.unload(silent=True)
        start = time.time()
        self.model = mlx_speech.tts.load(model_id)
        self.current_model_id = model_id
        return f"Loaded model: {model_id}\nLoad time: {time.time() - start:.1f} sec."

    def ensure_loaded(self, model_choice: str, custom_model_id: str | None = "") -> Any:
        """Return a loaded model, loading the requested one when needed."""
        model_id = self.resolve_model_id(model_choice, custom_model_id)
        if self.model is None or self.current_model_id != model_id:
            self.load(model_choice, custom_model_id)
        return self.model

    def unload(self, silent: bool = False) -> str:
        """Unload the current model and clear MLX memory."""
        if self.model is not None:
            del self.model
            self.model = None
            self.current_model_id = None
            clear_memory()

        return "" if silent else "Model has been unloaded from memory."


model_manager = ModelManager()
