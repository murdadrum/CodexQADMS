from __future__ import annotations

from packages.contracts import CanonicalTokenModel, ImportResponse, TokenVersionRecord, ValidationReport


def map_import_response(
    *,
    source_id: str,
    version: TokenVersionRecord,
    token_version: CanonicalTokenModel,
    validation: ValidationReport,
) -> ImportResponse:
    return ImportResponse(
        source_id=source_id,
        version_id=version.version_id,
        imported_at=version.imported_at,
        token_version=token_version,
        validation=validation,
    )
