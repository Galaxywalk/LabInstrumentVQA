"""Keyword relevance scoring for LabInstrumentVQA literature."""

from __future__ import annotations

import re

from .model import PaperRecord

DEFAULT_STRONG_KEYWORDS = [
    "oscilloscope",
    "spectrum analyzer",
    "network analyzer",
    "vna",
    "measurement",
    "test",
    "calibration",
    "bist",
    "monitor",
    "sensor readout",
    "adc",
    "dac",
    "pll",
    "rf",
    "mmwave",
    "wireless",
    "phase noise",
    "jitter",
    "s-parameter",
]

DEFAULT_VISUAL_KEYWORDS = [
    "waveform",
    "spectrum",
    "eye diagram",
    "constellation",
    "calibration curve",
    "histogram",
    "smith chart",
    "measurement setup",
    "chip micrograph",
]


def _normalized_text(record: PaperRecord) -> str:
    parts = [
        record.title,
        record.abstract or "",
        " ".join(record.keywords),
        " ".join(record.subjects),
    ]
    return " ".join(parts).lower().replace("-", "")


def _matches(text: str, keywords: list[str]) -> list[str]:
    found: list[str] = []
    compact_text = text.replace("-", "")
    for keyword in keywords:
        normalized = keyword.lower().replace("-", "")
        pattern = r"(?<![a-z0-9])" + re.escape(normalized) + r"(?![a-z0-9])"
        if re.search(pattern, compact_text):
            found.append(keyword)
    return found


def score_record(record: PaperRecord, rules: dict | None = None) -> PaperRecord:
    relevance = (rules or {}).get("relevance", {})
    strong_keywords = relevance.get("strong_keywords") or DEFAULT_STRONG_KEYWORDS
    visual_keywords = relevance.get("visual_evidence_keywords") or DEFAULT_VISUAL_KEYWORDS
    categories = relevance.get("categories") or {}

    text = _normalized_text(record)
    strong = _matches(text, strong_keywords)
    visual = _matches(text, visual_keywords)
    matched_categories = [
        name
        for name, category_keywords in categories.items()
        if _matches(text, list(category_keywords or []))
    ]

    record.matched_keywords = sorted(set(strong + visual), key=str.lower)
    record.matched_categories = sorted(set(matched_categories), key=str.lower)
    record.figure_evidence_type = sorted(set(visual), key=str.lower)
    record.relevance_score = float((len(strong) * 2) + (len(visual) * 3) + len(matched_categories))
    if record.relevance_score > 0 and record.review_status == "new":
        record.review_status = "needs_review"
    return record
