"""Metadata model for literature records."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return [str(value)]


@dataclass
class PaperRecord:
    paper_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str = ""
    publication_type: str = "unknown"
    doi: str | None = None
    ieee_article_number: str | None = None
    volume: str | None = None
    issue: str | None = None
    pages: str | None = None
    publisher: str | None = None
    source: str = ""
    source_query: str | None = None
    source_url: str | None = None
    retrieved_at: str = field(default_factory=utc_now_iso)
    abstract: str | None = None
    keywords: list[str] = field(default_factory=list)
    subjects: list[str] = field(default_factory=list)
    oa_status: str = "unknown"
    oa_urls: list[str] = field(default_factory=list)
    pdf_urls_legal: list[str] = field(default_factory=list)
    license: str | None = None
    relevance_score: float = 0.0
    matched_keywords: list[str] = field(default_factory=list)
    matched_categories: list[str] = field(default_factory=list)
    instrument_type: list[str] = field(default_factory=list)
    measurement_type: list[str] = field(default_factory=list)
    figure_evidence_type: list[str] = field(default_factory=list)
    task_relevance: list[str] = field(default_factory=list)
    review_status: str = "needs_review"
    notes: str | None = None
    selected_for_related_work: bool = False

    @classmethod
    def from_dict(cls, item: dict[str, Any]) -> "PaperRecord":
        return cls(
            paper_id=str(item.get("paper_id") or item.get("id") or ""),
            title=str(item.get("title") or ""),
            authors=_string_list(item.get("authors")),
            year=item.get("year"),
            venue=str(item.get("venue") or ""),
            publication_type=str(item.get("publication_type") or "unknown"),
            doi=item.get("doi"),
            ieee_article_number=item.get("ieee_article_number"),
            volume=item.get("volume"),
            issue=item.get("issue"),
            pages=item.get("pages"),
            publisher=item.get("publisher"),
            source=str(item.get("source") or ""),
            source_query=item.get("source_query"),
            source_url=item.get("source_url"),
            retrieved_at=str(item.get("retrieved_at") or utc_now_iso()),
            abstract=item.get("abstract"),
            keywords=_string_list(item.get("keywords")),
            subjects=_string_list(item.get("subjects")),
            oa_status=str(item.get("oa_status") or "unknown"),
            oa_urls=_string_list(item.get("oa_urls")),
            pdf_urls_legal=_string_list(item.get("pdf_urls_legal")),
            license=item.get("license"),
            relevance_score=float(item.get("relevance_score") or 0.0),
            matched_keywords=_string_list(item.get("matched_keywords")),
            matched_categories=_string_list(item.get("matched_categories")),
            instrument_type=_string_list(item.get("instrument_type")),
            measurement_type=_string_list(item.get("measurement_type")),
            figure_evidence_type=_string_list(item.get("figure_evidence_type")),
            task_relevance=_string_list(item.get("task_relevance")),
            review_status=str(item.get("review_status") or "needs_review"),
            notes=item.get("notes"),
            selected_for_related_work=bool(item.get("selected_for_related_work", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "venue": self.venue,
            "publication_type": self.publication_type,
            "doi": self.doi,
            "ieee_article_number": self.ieee_article_number,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "publisher": self.publisher,
            "source": self.source,
            "source_query": self.source_query,
            "source_url": self.source_url,
            "retrieved_at": self.retrieved_at,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "subjects": self.subjects,
            "oa_status": self.oa_status,
            "oa_urls": self.oa_urls,
            "pdf_urls_legal": self.pdf_urls_legal,
            "license": self.license,
            "relevance_score": self.relevance_score,
            "matched_keywords": self.matched_keywords,
            "matched_categories": self.matched_categories,
            "instrument_type": self.instrument_type,
            "measurement_type": self.measurement_type,
            "figure_evidence_type": self.figure_evidence_type,
            "task_relevance": self.task_relevance,
            "review_status": self.review_status,
            "notes": self.notes,
            "selected_for_related_work": self.selected_for_related_work,
        }
