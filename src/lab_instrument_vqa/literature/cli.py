"""CLI entry points for literature metadata tooling."""

from __future__ import annotations

import argparse
import sys

import requests

from .clients import CLIENTS
from .dedupe import dedupe_records
from .io import load_yaml, read_jsonl, write_jsonl
from .model import PaperRecord
from .relevance import score_record


def _expanded_queries(rules: dict, query_limit: int | None = None) -> list[str]:
    start = int(rules.get("years", {}).get("start", 2006))
    end = int(rules.get("years", {}).get("end", 2026))
    keywords = rules.get("relevance", {}).get("strong_keywords", [])
    queries = []
    for year in range(start, end + 1):
        queries.append(f'ISSCC {year} measurement')
        queries.append(f'"IEEE Journal of Solid-State Circuits" {year} measurement')
        for keyword in keywords[:8]:
            queries.append(f"ISSCC {year} {keyword}")
            queries.append(f'"IEEE Journal of Solid-State Circuits" {year} {keyword}')
    return queries[:query_limit] if query_limit else queries


def search_main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Collect legal literature metadata from public APIs.")
    parser.add_argument("--rules", required=True, help="YAML source rules file.")
    parser.add_argument("--out", required=True, help="Output JSONL path.")
    parser.add_argument("--limit-per-query", type=int, default=5)
    parser.add_argument("--query-limit", type=int, default=None)
    args = parser.parse_args(argv)

    rules = load_yaml(args.rules)
    source_names = rules.get("sources", {}).get("priority") or list(CLIENTS)
    records: list[PaperRecord] = []
    for query in _expanded_queries(rules, args.query_limit):
        for source_name in source_names:
            client = CLIENTS.get(source_name)
            if client is None:
                print(f"Skipping unknown source: {source_name}", file=sys.stderr)
                continue
            try:
                for record in client.search(query, args.limit_per_query, rules):
                    records.append(score_record(record, rules))
            except (requests.RequestException, ValueError, TimeoutError) as exc:
                print(f"Source {source_name} failed for query {query!r}: {exc}", file=sys.stderr)
    write_jsonl(args.out, records)


def dedupe_main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Deduplicate literature metadata JSONL.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title-similarity-threshold", type=float, default=0.92)
    args = parser.parse_args(argv)
    records = read_jsonl(args.input)
    write_jsonl(args.out, dedupe_records(records, args.title_similarity_threshold))


def rank_main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Rank literature metadata by LabInstrumentVQA relevance.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--rules", default="data/literature/source_rules.yaml")
    args = parser.parse_args(argv)
    rules = load_yaml(args.rules)
    records = [score_record(record, rules) for record in read_jsonl(args.input)]
    records.sort(key=lambda item: (item.relevance_score, item.year or 0, item.title), reverse=True)
    write_jsonl(args.out, records)


if __name__ == "__main__":
    search_main()
