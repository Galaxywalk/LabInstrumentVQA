"""Evaluation runner for lab-instrument visual question answering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .image_io import image_to_data_url
from .openrouter import OpenRouterClient
from .schema import ModelResult, VQASample


DEFAULT_SYSTEM_PROMPT = """You are evaluating lab-instrument screenshots.
Answer the user's question using only the visible display.
Be precise about units, channel/trace labels, marker values, and instrument state.
If the display is unclear or the requested value is not visible, say so instead of guessing."""


def load_jsonl(path: str | Path) -> list[VQASample]:
    """Load VQA samples from JSONL.

    Expected fields per line:
      id, image, question, optional answer, optional instrument, optional metadata
    Relative image paths are resolved against the JSONL file directory.
    """
    jsonl_path = Path(path).expanduser().resolve()
    samples: list[VQASample] = []
    with jsonl_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                item = json.loads(stripped)
                samples.append(VQASample.from_json(item, jsonl_path.parent))
            except Exception as exc:
                raise ValueError(f"Invalid sample at {jsonl_path}:{line_number}") from exc
    return samples


def write_jsonl(path: str | Path, rows: Iterable[dict]) -> None:
    output_path = Path(path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_vqa_payload(
    *,
    model: str,
    sample: VQASample,
    prompt: str = DEFAULT_SYSTEM_PROMPT,
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> dict:
    image_url = image_to_data_url(sample.image_path)
    user_text = sample.question
    if sample.instrument:
        user_text = f"Instrument: {sample.instrument}\nQuestion: {sample.question}"

    return {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ],
    }


def extract_text(response: dict) -> str:
    choices = response.get("choices") or []
    if not choices:
        return ""

    content = choices[0].get("message", {}).get("content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = [part.get("text", "") for part in content if isinstance(part, dict)]
        return "\n".join(part for part in parts if part).strip()
    return str(content).strip()


def run_evaluation(
    *,
    client: OpenRouterClient,
    samples: list[VQASample],
    models: list[str],
    prompt: str = DEFAULT_SYSTEM_PROMPT,
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> list[ModelResult]:
    results: list[ModelResult] = []

    for sample in samples:
        for model in models:
            try:
                payload = build_vqa_payload(
                    model=model,
                    sample=sample,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                response = client.chat_completion(payload)
                prediction = extract_text(response)
                results.append(
                    ModelResult(
                        sample_id=sample.sample_id,
                        model=model,
                        question=sample.question,
                        prediction=prediction,
                        answer=sample.answer,
                        instrument=sample.instrument,
                        raw_response=response,
                    )
                )
            except Exception as exc:
                results.append(
                    ModelResult(
                        sample_id=sample.sample_id,
                        model=model,
                        question=sample.question,
                        prediction="",
                        answer=sample.answer,
                        instrument=sample.instrument,
                        raw_response={},
                        error=str(exc),
                    )
                )

    return results
