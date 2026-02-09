from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from packages.rules.figma_adapter import build_import_response

OPENAPI_CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contracts" / "figma-import.openapi.yaml"


def post_tokens_import_figma(source_id: str, request_body: bytes) -> tuple[int, dict[str, Any]]:
    """Framework-agnostic handler for POST /api/v1/sources/{source_id}/tokens/import/figma."""
    try:
        payload = json.loads(request_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return 400, {
            "error": "invalid_json",
            "message": "Request body must be valid UTF-8 JSON.",
        }

    response = build_import_response(source_id=source_id, payload=payload)
    status_code = 200 if response.validation.valid else 422
    return status_code, response.to_dict()
