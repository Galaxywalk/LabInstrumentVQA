from __future__ import annotations

from lab_instrument_vqa.evaluation import load_jsonl
from lab_instrument_vqa.evaluation.image_io import image_to_data_url


def test_sample_tasks_reference_existing_images() -> None:
    samples = load_jsonl("data/benchmark/sample_tasks.jsonl")
    assert {sample.instrument for sample in samples} == {"oscilloscope", "spectrum analyzer"}
    for sample in samples:
        data_url = image_to_data_url(sample.image_path)
        assert data_url.startswith("data:image/")
