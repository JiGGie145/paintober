"""Vertex AI adapter for cartoonish image preprocessing."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from django.conf import settings

logger = logging.getLogger("pipeline")

PROMPT = """A cute, kawaii-style sticker illustration based on the subject(s). Clean, bold dark vector outlines, vibrant colors, and smooth cel-shading. It is critical to ensure all limbs and their positions strictly match the poses and anatomy structure shown in the original reference image. Retain the core elements and distinctive features of the source image while simplifying them into an endearing, animated aesthetic. High contrast, die-cut white sticker border, isolated on a solid white background."""


def _vertex_credentials() -> Any:
    credentials_path = getattr(settings, "VERTEX_AI_CREDENTIALS_PATH", "")
    if not credentials_path:
        return None
    from google.oauth2 import service_account

    return service_account.Credentials.from_service_account_file(credentials_path)


def generate_cartoon_image(image_path: str | Path, output_path: str | Path) -> str:
    """Transform an image with Vertex AI and save the generated image as PNG."""
    from vertexai.preview.generative_models import GenerativeModel, Part
    import vertexai

    source_path = Path(image_path)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    credentials = _vertex_credentials()
    init_kwargs = {
        "project": settings.VERTEX_AI_PROJECT_ID,
        "location": settings.VERTEX_AI_LOCATION,
    }
    if credentials is not None:
        init_kwargs["credentials"] = credentials
    vertexai.init(**init_kwargs)

    with source_path.open("rb") as source:
        image_part = Part.from_data(data=source.read(), mime_type="image/png")

    model = GenerativeModel(settings.VERTEX_AI_MODEL)
    response = model.generate_content(
        [PROMPT, image_part],
        generation_config={
            "temperature": 1,
            "max_output_tokens": 65536,
            "top_p": 0.95,
        },
    )

    for candidate in getattr(response, "candidates", []):
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", []) if content else []:
            image = getattr(part, "image", None)
            inline_data = getattr(part, "inline_data", None)
            image_data = getattr(image, "data", None) or getattr(inline_data, "data", None)
            if image_data:
                destination.write_bytes(image_data)
                logger.info("Cartoon image generated | output=%s", destination)
                return str(destination)

    raise RuntimeError("Vertex AI did not return an image for the cartoonish job")
