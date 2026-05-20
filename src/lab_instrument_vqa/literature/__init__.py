"""Literature metadata tooling for LabInstrumentVQA."""

from .dedupe import dedupe_records
from .io import read_jsonl, write_jsonl
from .model import PaperRecord
from .relevance import score_record

__all__ = ["PaperRecord", "dedupe_records", "read_jsonl", "score_record", "write_jsonl"]
