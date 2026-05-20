"""Record deduplication by DOI and normalized title."""

from __future__ import annotations

from difflib import SequenceMatcher
import re

from .model import PaperRecord


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    value = doi.strip().lower()
    value = value.removeprefix("https://doi.org/")
    value = value.removeprefix("http://doi.org/")
    value = value.removeprefix("doi:")
    return value or None


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", title.lower())).strip()


def _merge_records(primary: PaperRecord, duplicate: PaperRecord) -> PaperRecord:
    for field_name in [
        "doi",
        "ieee_article_number",
        "volume",
        "issue",
        "pages",
        "publisher",
        "source_url",
        "abstract",
        "license",
        "notes",
    ]:
        if getattr(primary, field_name) in (None, "") and getattr(duplicate, field_name):
            setattr(primary, field_name, getattr(duplicate, field_name))

    for field_name in [
        "authors",
        "keywords",
        "subjects",
        "oa_urls",
        "pdf_urls_legal",
        "matched_keywords",
        "matched_categories",
        "instrument_type",
        "measurement_type",
        "figure_evidence_type",
        "task_relevance",
    ]:
        merged = list(dict.fromkeys(getattr(primary, field_name) + getattr(duplicate, field_name)))
        setattr(primary, field_name, merged)

    primary.relevance_score = max(primary.relevance_score, duplicate.relevance_score)
    if primary.oa_status == "unknown" and duplicate.oa_status != "unknown":
        primary.oa_status = duplicate.oa_status
    return primary


def dedupe_records(records: list[PaperRecord], title_similarity_threshold: float = 0.92) -> list[PaperRecord]:
    deduped: list[PaperRecord] = []
    doi_index: dict[str, PaperRecord] = {}

    for record in records:
        doi = normalize_doi(record.doi)
        if doi and doi in doi_index:
            _merge_records(doi_index[doi], record)
            continue
        title = normalize_title(record.title)
        title_match = None
        for existing in deduped:
            existing_title = normalize_title(existing.title)
            if title and existing_title:
                ratio = SequenceMatcher(None, title, existing_title).ratio()
                if ratio >= title_similarity_threshold:
                    title_match = existing
                    break
        if title_match:
            _merge_records(title_match, record)
            if doi:
                doi_index[doi] = title_match
            continue
        deduped.append(record)
        if doi:
            doi_index[doi] = record
    return deduped
