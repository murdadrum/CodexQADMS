from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ValidationIssue:
    path: str
    message: str


@dataclass
class ValidationReport:
    valid: bool = True
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    def add_error(self, path: str, message: str) -> None:
        self.valid = False
        self.errors.append(ValidationIssue(path=path, message=message))

    def add_warning(self, path: str, message: str) -> None:
        self.warnings.append(ValidationIssue(path=path, message=message))

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": [asdict(issue) for issue in self.errors],
            "warnings": [asdict(issue) for issue in self.warnings],
        }


@dataclass
class CanonicalToken:
    group: str
    path: str
    name: str
    token_type: str
    value: Any
    source: str = "figma_export"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CanonicalTokenModel:
    source: str
    tokens: list[CanonicalToken]

    def token_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for token in self.tokens:
            counts[token.group] = counts.get(token.group, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "tokens": [token.to_dict() for token in self.tokens],
            "token_counts": self.token_counts(),
        }


@dataclass
class ImportResponse:
    source_id: str
    version_id: str
    imported_at: str
    token_version: CanonicalTokenModel
    validation: ValidationReport

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "version_id": self.version_id,
            "imported_at": self.imported_at,
            "token_version": self.token_version.to_dict(),
            "validation": self.validation.to_dict(),
        }
