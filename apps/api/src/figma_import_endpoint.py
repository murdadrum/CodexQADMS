from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from packages.rules.figma_adapter import normalize_figma_export

from .error_envelope import error_response
from .import_mapping import map_import_response
from .persistence import DEFAULT_IMPORT_STORE, TokenImportStore

OPENAPI_CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contracts" / "figma-import.openapi.yaml"


def post_tokens_import_figma(
    source_id: str,
    request_body: bytes,
    import_store: TokenImportStore | None = None,
) -> tuple[int, dict[str, Any]]:
    """Framework-agnostic handler for POST /api/v1/sources/{source_id}/tokens/import/figma."""
    if not source_id or not source_id.strip():
        return error_response(
            status_code=400,
            code="invalid_source_id",
            message="Path parameter `source_id` must be a non-empty string.",
        )

    try:
        payload = json.loads(request_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return error_response(
            status_code=400,
            code="invalid_json",
            message="Request body must be valid UTF-8 JSON.",
        )

    try:
        token_version, validation = normalize_figma_export(payload)
        storage = import_store or DEFAULT_IMPORT_STORE
        storage.upsert_source(source_id=source_id, source_type="figma")

        persisted_version = storage.create_token_version(
            source_id=source_id,
            input_format="figma_json",
            input_sha256=hashlib.sha256(request_body).hexdigest(),
            token_source=token_version.source,
            token_counts=token_version.token_counts(),
            validation_valid=validation.valid,
        )

        response = map_import_response(
            source_id=source_id,
            version=persisted_version,
            token_version=token_version,
            validation=validation,
        )
        status_code = 200 if validation.valid else 422
        return status_code, response.to_dict()
    except Exception:
        return error_response(
            status_code=500,
            code="internal_error",
            message="Unexpected server error while processing token import.",
        )
