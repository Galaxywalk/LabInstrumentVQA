from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from lab_instrument_vqa.literature.dedupe import dedupe_records
from lab_instrument_vqa.literature.io import read_jsonl, write_jsonl
from lab_instrument_vqa.literature.model import PaperRecord
from lab_instrument_vqa.literature.oa import apply_oa_links, is_legal_oa_url
from lab_instrument_vqa.literature.relevance import score_record


ROOT = Path(__file__).resolve().parents[1]


def test_seed_records_validate_against_schema() -> None:
    schema = json.loads((ROOT / "data/literature/paper_metadata.schema.json").read_text())
    seed_path = ROOT / "data/literature/papers.seed.jsonl"
    for line in seed_path.read_text().splitlines():
        jsonschema.validate(json.loads(line), schema)


def test_jsonl_round_trip(tmp_path: Path) -> None:
    record = PaperRecord(
        paper_id="test:1",
        title="A Test ADC With Calibration Waveforms",
        authors=["A. Author"],
        year=2020,
        venue="ISSCC",
        publication_type="conference",
        source="unit",
    )
    path = tmp_path / "records.jsonl"
    write_jsonl(path, [record])
    loaded = read_jsonl(path)
    assert loaded[0].to_dict() == record.to_dict()


def test_dedupe_prefers_doi_and_merges_metadata() -> None:
    first = PaperRecord(
        paper_id="a",
        title="A 10-bit ADC With Calibration",
        doi="10.1109/JSSC.2020.1",
        source="crossref",
        keywords=["ADC"],
    )
    second = PaperRecord(
        paper_id="b",
        title="A 10-bit ADC with calibration",
        doi="https://doi.org/10.1109/jssc.2020.1",
        source="openalex",
        abstract="Includes measured spectra.",
        keywords=["calibration"],
    )
    result = dedupe_records([first, second])
    assert len(result) == 1
    assert result[0].abstract == "Includes measured spectra."
    assert result[0].keywords == ["ADC", "calibration"]


def test_dedupe_uses_similar_titles_without_doi() -> None:
    first = PaperRecord(paper_id="a", title="An RF PLL With Jitter Measurement", source="dblp")
    second = PaperRecord(paper_id="b", title="An RF PLL with jitter measurements", source="crossref")
    assert len(dedupe_records([first, second], title_similarity_threshold=0.85)) == 1


def test_relevance_scoring_matches_keywords_and_categories() -> None:
    rules = {
        "relevance": {
            "strong_keywords": ["ADC", "calibration", "phase noise"],
            "visual_evidence_keywords": ["waveform", "spectrum"],
            "categories": {"measurements": ["phase noise", "waveform"], "circuits": ["ADC"]},
        }
    }
    record = PaperRecord(
        paper_id="score:1",
        title="An ADC Calibration Monitor",
        abstract="Measured waveform and phase noise results are reported.",
        source="unit",
    )
    scored = score_record(record, rules)
    assert scored.relevance_score == 11.0
    assert scored.matched_keywords == ["ADC", "calibration", "phase noise", "waveform"]
    assert scored.matched_categories == ["circuits", "measurements"]


def test_oa_locator_filters_unauthorized_urls() -> None:
    assert not is_legal_oa_url("https://sci-hub.se/10.1109/example")
    assert is_legal_oa_url("https://arxiv.org/abs/2401.00001")
    record = PaperRecord(paper_id="oa:1", title="OA Test", source="unit")
    apply_oa_links(
        record,
        ["https://sci-hub.se/10.1109/example", "https://arxiv.org/abs/2401.00001"],
        ["https://sci-hub.se/example.pdf", "https://arxiv.org/pdf/2401.00001"],
    )
    assert record.oa_urls == ["https://arxiv.org/abs/2401.00001"]
    assert record.pdf_urls_legal == ["https://arxiv.org/pdf/2401.00001"]


def test_doi_landing_page_does_not_imply_open_access() -> None:
    record = PaperRecord(paper_id="doi:1", title="DOI Test", source="unit")
    apply_oa_links(record, ["https://doi.org/10.1109/example"])
    assert record.oa_urls == ["https://doi.org/10.1109/example"]
    assert record.oa_status == "unknown"
