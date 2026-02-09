from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SourceRecord:
    source_id: str
    source_type: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TokenVersionRecord:
    version_id: str
    source_id: str
    imported_at: str
    input_format: str
    input_sha256: str
    token_source: str
    token_counts: dict[str, int]
    validation_valid: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
