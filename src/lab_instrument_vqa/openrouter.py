"""Small OpenRouter chat-completions client."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests


OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


@dataclass(frozen=True)
class OpenRouterConfig:
    """Runtime options for OpenRouter requests."""

    api_key: str
    site_url: str | None = None
    app_name: str = "LabInstrumentVQA"
    timeout_seconds: int = 120
    max_retries: int = 2

    @classmethod
    def from_env(cls) -> "OpenRouterConfig":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("Set OPENROUTER_API_KEY before running evaluation.")

        return cls(
            api_key=api_key,
            site_url=os.getenv("OPENROUTER_SITE_URL"),
            app_name=os.getenv("OPENROUTER_APP_NAME", "LabInstrumentVQA"),
        )


class OpenRouterClient:
    """OpenAI-compatible client for OpenRouter chat completions."""

    def __init__(self, config: OpenRouterConfig):
        self.config = config

    def chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "X-Title": self.config.app_name,
        }
        if self.config.site_url:
            headers["HTTP-Referer"] = self.config.site_url

        last_error: requests.RequestException | None = None
        for attempt in range(self.config.max_retries + 1):
            try:
                response = requests.post(
                    OPENROUTER_CHAT_URL,
                    headers=headers,
                    json=payload,
                    timeout=self.config.timeout_seconds,
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_error = exc
                if attempt >= self.config.max_retries:
                    break
                time.sleep(2**attempt)

        raise RuntimeError(f"OpenRouter request failed: {last_error}") from last_error
