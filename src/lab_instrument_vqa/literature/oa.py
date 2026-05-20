"""Legal open-access URL filtering and enrichment."""

from __future__ import annotations

from urllib.parse import urlparse

from .model import PaperRecord

DISALLOWED_HOSTS = {
    "sci-hub.se",
    "sci-hub.st",
    "sci-hub.ru",
    "sci-hub.wf",
    "sci-hub.ee",
    "libgen.rs",
}

ALLOWED_HOSTS = {
    "arxiv.org",
    "doi.org",
    "export.arxiv.org",
    "ieee.org",
    "openalex.org",
    "semanticscholar.org",
}


def is_legal_oa_url(url: str, rules: dict | None = None) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    host = parsed.netloc.lower().removeprefix("www.")
    policy = (rules or {}).get("open_access_policy", {})
    disallowed = set(policy.get("disallowed_hosts") or DISALLOWED_HOSTS)
    if host in disallowed or any(host.endswith("." + item) for item in disallowed):
        return False

    allowed_hosts = set(policy.get("allowed_hosts") or ALLOWED_HOSTS)
    if allowed_hosts and (host in allowed_hosts or any(host.endswith("." + item) for item in allowed_hosts)):
        return True

    path = parsed.path.lower()
    allowed_patterns = [str(item).lower() for item in policy.get("allowed_patterns") or []]
    return any(pattern in host or pattern in path for pattern in allowed_patterns)


def _is_doi_landing_page(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    return host == "doi.org"


def apply_oa_links(record: PaperRecord, urls: list[str], pdf_urls: list[str] | None = None, rules: dict | None = None) -> PaperRecord:
    legal_pages = [url for url in urls if is_legal_oa_url(url, rules)]
    legal_pdfs = [url for url in (pdf_urls or []) if is_legal_oa_url(url, rules)]
    record.oa_urls = list(dict.fromkeys(record.oa_urls + legal_pages))
    record.pdf_urls_legal = list(dict.fromkeys(record.pdf_urls_legal + legal_pdfs))
    has_non_doi_oa_page = any(not _is_doi_landing_page(url) for url in record.oa_urls)
    if has_non_doi_oa_page or record.pdf_urls_legal:
        record.oa_status = "open" if record.oa_status in {"unknown", "closed"} else record.oa_status
    return record
