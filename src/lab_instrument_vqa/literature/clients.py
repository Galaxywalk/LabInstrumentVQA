"""Metadata source clients for literature discovery."""

from __future__ import annotations

import os
from typing import Any, Protocol
from urllib.parse import quote_plus

import requests

from .model import PaperRecord, utc_now_iso
from .oa import apply_oa_links

USER_AGENT = "LabInstrumentVQA literature metadata collector (legal metadata/OA links only)"


class SourceClient(Protocol):
    name: str

    def search(self, query: str, limit: int, rules: dict) -> list[PaperRecord]:
        ...


def _session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def _authors_from_crossref(authors: list[dict[str, Any]] | None) -> list[str]:
    names = []
    for author in authors or []:
        parts = [author.get("given"), author.get("family")]
        name = " ".join(part for part in parts if part)
        if name:
            names.append(name)
    return names


def _year_from_parts(parts: dict[str, Any] | None) -> int | None:
    values = (parts or {}).get("date-parts") or []
    if values and values[0]:
        return values[0][0]
    return None


class CrossrefClient:
    name = "crossref"
    endpoint = "https://api.crossref.org/works"

    def search(self, query: str, limit: int, rules: dict) -> list[PaperRecord]:
        response = _session().get(
            self.endpoint,
            params={"query.bibliographic": query, "rows": limit},
            timeout=20,
        )
        response.raise_for_status()
        items = response.json().get("message", {}).get("items", [])
        records = []
        for item in items:
            title = " ".join(item.get("title") or []).strip()
            if not title:
                continue
            doi = item.get("DOI")
            urls = [item.get("URL")] if item.get("URL") else []
            record = PaperRecord(
                paper_id=f"crossref:{doi or quote_plus(title.lower())}",
                title=title,
                authors=_authors_from_crossref(item.get("author")),
                year=_year_from_parts(item.get("published-print") or item.get("published-online")),
                venue=" ".join(item.get("container-title") or []),
                publication_type="journal" if item.get("type") == "journal-article" else "conference",
                doi=doi,
                volume=item.get("volume"),
                issue=item.get("issue"),
                pages=item.get("page"),
                publisher=item.get("publisher"),
                source=self.name,
                source_query=query,
                source_url=item.get("URL"),
                retrieved_at=utc_now_iso(),
                license=(item.get("license") or [{}])[0].get("URL") if item.get("license") else None,
                review_status="new",
            )
            records.append(apply_oa_links(record, urls, rules=rules))
        return records


class OpenAlexClient:
    name = "openalex"
    endpoint = "https://api.openalex.org/works"

    def search(self, query: str, limit: int, rules: dict) -> list[PaperRecord]:
        response = _session().get(self.endpoint, params={"search": query, "per-page": limit}, timeout=20)
        response.raise_for_status()
        records = []
        for item in response.json().get("results", []):
            title = item.get("title") or item.get("display_name")
            if not title:
                continue
            doi = (item.get("doi") or "").removeprefix("https://doi.org/") or None
            authors = [
                authorship.get("author", {}).get("display_name")
                for authorship in item.get("authorships", [])
                if authorship.get("author", {}).get("display_name")
            ]
            primary_location = item.get("primary_location") or {}
            source_info = primary_location.get("source") or {}
            oa = item.get("open_access") or {}
            oa_url = oa.get("oa_url")
            landing_url = primary_location.get("landing_page_url")
            pdf_url = primary_location.get("pdf_url")
            record = PaperRecord(
                paper_id=f"openalex:{item.get('id')}",
                title=title,
                authors=authors,
                year=item.get("publication_year"),
                venue=source_info.get("display_name") or "",
                publication_type="journal" if item.get("type") == "article" else "conference",
                doi=doi,
                source=self.name,
                source_query=query,
                source_url=item.get("id"),
                retrieved_at=utc_now_iso(),
                abstract=item.get("abstract"),
                keywords=[concept.get("display_name") for concept in item.get("concepts", []) if concept.get("display_name")],
                oa_status=oa.get("oa_status") or "unknown",
                review_status="new",
            )
            records.append(apply_oa_links(record, [url for url in [oa_url, landing_url] if url], [pdf_url] if pdf_url else [], rules))
        return records


class DBLPClient:
    name = "dblp"
    endpoint = "https://dblp.org/search/publ/api"

    def search(self, query: str, limit: int, rules: dict) -> list[PaperRecord]:
        response = _session().get(self.endpoint, params={"q": query, "format": "json", "h": limit}, timeout=20)
        response.raise_for_status()
        hits = response.json().get("result", {}).get("hits", {}).get("hit", [])
        records = []
        for hit in hits:
            info = hit.get("info", {})
            title = info.get("title")
            if not title:
                continue
            authors_raw = info.get("authors", {}).get("author", [])
            if isinstance(authors_raw, dict):
                authors_raw = [authors_raw]
            authors = [author.get("text") for author in authors_raw if author.get("text")]
            venue = info.get("venue") or ""
            record = PaperRecord(
                paper_id=f"dblp:{info.get('key') or quote_plus(title.lower())}",
                title=title,
                authors=authors,
                year=int(info["year"]) if str(info.get("year", "")).isdigit() else None,
                venue=venue,
                publication_type="journal" if "journal" in (info.get("type") or "").lower() else "conference",
                pages=info.get("pages"),
                source=self.name,
                source_query=query,
                source_url=info.get("url"),
                retrieved_at=utc_now_iso(),
                review_status="new",
            )
            records.append(apply_oa_links(record, [info.get("ee"), info.get("url")], rules=rules))
        return records


class ArxivClient:
    name = "arxiv"
    endpoint = "https://export.arxiv.org/api/query"

    def search(self, query: str, limit: int, rules: dict) -> list[PaperRecord]:
        response = _session().get(
            self.endpoint,
            params={"search_query": f"all:{query}", "start": 0, "max_results": limit},
            timeout=20,
        )
        response.raise_for_status()
        import xml.etree.ElementTree as ET

        root = ET.fromstring(response.text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        records = []
        for entry in root.findall("atom:entry", ns):
            title = " ".join((entry.findtext("atom:title", default="", namespaces=ns)).split())
            if not title:
                continue
            entry_id = entry.findtext("atom:id", default="", namespaces=ns)
            authors = [
                author.findtext("atom:name", default="", namespaces=ns)
                for author in entry.findall("atom:author", ns)
            ]
            pdf_url = None
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf":
                    pdf_url = link.attrib.get("href")
            year = None
            published = entry.findtext("atom:published", default="", namespaces=ns)
            if len(published) >= 4 and published[:4].isdigit():
                year = int(published[:4])
            record = PaperRecord(
                paper_id=f"arxiv:{entry_id.rsplit('/', 1)[-1]}",
                title=title,
                authors=[author for author in authors if author],
                year=year,
                venue="arXiv",
                publication_type="preprint",
                source=self.name,
                source_query=query,
                source_url=entry_id,
                retrieved_at=utc_now_iso(),
                abstract=" ".join((entry.findtext("atom:summary", default="", namespaces=ns)).split()) or None,
                review_status="new",
            )
            records.append(apply_oa_links(record, [entry_id], [pdf_url] if pdf_url else [], rules))
        return records


class SemanticScholarClient:
    name = "semantic_scholar"
    endpoint = "https://api.semanticscholar.org/graph/v1/paper/search"

    def search(self, query: str, limit: int, rules: dict) -> list[PaperRecord]:
        fields = "title,authors,year,venue,externalIds,url,abstract,openAccessPdf,publicationTypes"
        response = _session().get(self.endpoint, params={"query": query, "limit": limit, "fields": fields}, timeout=20)
        response.raise_for_status()
        records = []
        for item in response.json().get("data", []):
            title = item.get("title")
            if not title:
                continue
            external = item.get("externalIds") or {}
            pdf_url = (item.get("openAccessPdf") or {}).get("url")
            publication_types = [item.lower() for item in item.get("publicationTypes") or []]
            record = PaperRecord(
                paper_id=f"semantic_scholar:{item.get('paperId')}",
                title=title,
                authors=[author.get("name") for author in item.get("authors", []) if author.get("name")],
                year=item.get("year"),
                venue=item.get("venue") or "",
                publication_type="journal" if "journalarticle" in publication_types else "conference",
                doi=external.get("DOI"),
                source=self.name,
                source_query=query,
                source_url=item.get("url"),
                retrieved_at=utc_now_iso(),
                abstract=item.get("abstract"),
                review_status="new",
            )
            records.append(apply_oa_links(record, [item.get("url")] if item.get("url") else [], [pdf_url] if pdf_url else [], rules))
        return records


class IEEEXploreClient:
    name = "ieee_xplore"
    endpoint = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

    def search(self, query: str, limit: int, rules: dict) -> list[PaperRecord]:
        api_key = os.getenv("IEEE_XPLORE_API_KEY")
        if not api_key:
            return []
        response = _session().get(
            self.endpoint,
            params={"apikey": api_key, "format": "json", "querytext": query, "max_records": limit},
            timeout=20,
        )
        response.raise_for_status()
        records = []
        for item in response.json().get("articles", []):
            title = item.get("title")
            if not title:
                continue
            record = PaperRecord(
                paper_id=f"ieee:{item.get('article_number') or quote_plus(title.lower())}",
                title=title,
                authors=[author.get("full_name") for author in item.get("authors", {}).get("authors", []) if author.get("full_name")],
                year=int(item["publication_year"]) if str(item.get("publication_year", "")).isdigit() else None,
                venue=item.get("publication_title") or "",
                publication_type="journal" if item.get("content_type") == "Journals" else "conference",
                doi=item.get("doi"),
                ieee_article_number=item.get("article_number"),
                volume=item.get("volume"),
                issue=item.get("issue"),
                pages=item.get("start_page"),
                publisher="IEEE",
                source=self.name,
                source_query=query,
                source_url=item.get("html_url"),
                retrieved_at=utc_now_iso(),
                abstract=item.get("abstract"),
                keywords=item.get("index_terms", {}).get("ieee_terms", {}).get("terms", []),
                review_status="new",
            )
            records.append(apply_oa_links(record, [item.get("html_url")] if item.get("html_url") else [], rules=rules))
        return records


CLIENTS: dict[str, SourceClient] = {
    "openalex": OpenAlexClient(),
    "crossref": CrossrefClient(),
    "dblp": DBLPClient(),
    "arxiv": ArxivClient(),
    "semantic_scholar": SemanticScholarClient(),
    "ieee_xplore": IEEEXploreClient(),
}
