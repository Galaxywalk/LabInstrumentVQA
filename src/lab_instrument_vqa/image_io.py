"""Image helpers for OpenRouter multimodal requests."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path


def image_to_data_url(image_path: str | Path) -> str:
    """Encode a local image as a data URL accepted by chat-completions APIs."""
    path = Path(image_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    mime_type, _ = mimetypes.guess_type(path.name)
    if mime_type is None or not mime_type.startswith("image/"):
        raise ValueError(f"Unsupported image type for {path}")

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"
