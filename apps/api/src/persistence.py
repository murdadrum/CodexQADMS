from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol
from uuid import uuid4

from packages.contracts import SourceRecord, TokenVersionRecord


class TokenImportStore(Protocol):
    def upsert_source(self, source_id: str, source_type: str = "figma") -> SourceRecord:
        """Ensure a source exists and return its current record."""

    def create_token_version(
        self,
        *,
        source_id: str,
        input_format: str,
        input_sha256: str,
        token_source: str,
        token_counts: dict[str, int],
        validation_valid: bool,
    ) -> TokenVersionRecord:
        """Create and return a persisted token version record."""


class InMemoryTokenImportStore:
    """DB-ready persistence contract implementation for local development and tests."""

    def __init__(self) -> None:
        self._sources: dict[str, SourceRecord] = {}
        self._versions: list[TokenVersionRecord] = []

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(tz=timezone.utc).isoformat()

    def upsert_source(self, source_id: str, source_type: str = "figma") -> SourceRecord:
        now = self._now_iso()
        existing = self._sources.get(source_id)
        if existing is None:
            record = SourceRecord(
                source_id=source_id,
                source_type=source_type,
                created_at=now,
                updated_at=now,
            )
            self._sources[source_id] = record
            return record

        existing.updated_at = now
        return existing

    def create_token_version(
        self,
        *,
        source_id: str,
        input_format: str,
        input_sha256: str,
        token_source: str,
        token_counts: dict[str, int],
        validation_valid: bool,
    ) -> TokenVersionRecord:
        record = TokenVersionRecord(
            version_id=str(uuid4()),
            source_id=source_id,
            imported_at=self._now_iso(),
            input_format=input_format,
            input_sha256=input_sha256,
            token_source=token_source,
            token_counts=dict(token_counts),
            validation_valid=validation_valid,
        )
        self._versions.append(record)
        return record

    def list_versions_for_source(self, source_id: str) -> list[TokenVersionRecord]:
        return [version for version in self._versions if version.source_id == source_id]


DEFAULT_IMPORT_STORE = InMemoryTokenImportStore()
