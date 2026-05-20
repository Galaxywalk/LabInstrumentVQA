"""Data structures for LabInstrumentVQA evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VQASample:
    """One visual question about a lab-instrument display."""

    sample_id: str
    image_path: Path
    question: str
    answer: str | None = None
    instrument: str | None = None
    metadata: dict[str, Any] | None = None

    @classmethod
    def from_json(cls, item: dict[str, Any], base_dir: Path) -> "VQASample":
        image_value = item.get("image") or item.get("image_path")
        if not image_value:
            raise ValueError("Sample is missing required field: image")

        image_path = Path(image_value)
        if not image_path.is_absolute():
            image_path = base_dir / image_path

        sample_id = str(item.get("id") or image_path.stem)
        question = item.get("question")
        if not question:
            raise ValueError(f"Sample {sample_id} is missing required field: question")

        return cls(
            sample_id=sample_id,
            image_path=image_path,
            question=str(question),
            answer=item.get("answer"),
            instrument=item.get("instrument"),
            metadata=item.get("metadata"),
        )


@dataclass(frozen=True)
class ModelResult:
    """One model response for one sample."""

    sample_id: str
    model: str
    question: str
    prediction: str
    answer: str | None
    instrument: str | None
    raw_response: dict[str, Any]
    error: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.sample_id,
            "model": self.model,
            "instrument": self.instrument,
            "question": self.question,
            "answer": self.answer,
            "prediction": self.prediction,
            "error": self.error,
            "raw_response": self.raw_response,
        }
