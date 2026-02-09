from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .error_envelope import error_response


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _diff_bytes(baseline: bytes, current: bytes) -> int:
    min_len = min(len(baseline), len(current))
    mismatch = sum(1 for idx in range(min_len) if baseline[idx] != current[idx])
    mismatch += abs(len(baseline) - len(current))
    return mismatch


def post_visual_diff_audit(source_id: str, request_body: bytes) -> tuple[int, dict[str, Any]]:
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

    if not isinstance(payload, dict):
        return error_response(
            status_code=400,
            code="invalid_visual_diff_payload",
            message="Visual diff payload must be a JSON object.",
        )

    baseline_snapshot = payload.get("baseline_snapshot")
    current_snapshot = payload.get("current_snapshot")
    if not isinstance(baseline_snapshot, str) or not baseline_snapshot:
        return error_response(
            status_code=400,
            code="invalid_visual_diff_payload",
            message="`baseline_snapshot` must be a non-empty string.",
        )
    if not isinstance(current_snapshot, str) or not current_snapshot:
        return error_response(
            status_code=400,
            code="invalid_visual_diff_payload",
            message="`current_snapshot` must be a non-empty string.",
        )

    threshold = payload.get("threshold", 0.0)
    if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 1:
        return error_response(
            status_code=400,
            code="invalid_visual_diff_payload",
            message="`threshold` must be a number between 0 and 1.",
        )

    baseline_bytes = baseline_snapshot.encode("utf-8")
    current_bytes = current_snapshot.encode("utf-8")
    changed_bytes = _diff_bytes(baseline_bytes, current_bytes)
    total_bytes = max(len(baseline_bytes), len(current_bytes), 1)
    diff_ratio = changed_bytes / total_bytes
    passed = diff_ratio <= float(threshold)

    response = {
        "source_id": source_id,
        "diff_id": str(uuid4()),
        "evaluated_at": _now_iso(),
        "status": "pass" if passed else "fail",
        "summary": {
            "baseline_bytes": len(baseline_bytes),
            "current_bytes": len(current_bytes),
            "changed_bytes": changed_bytes,
            "diff_ratio": round(diff_ratio, 6),
            "threshold": float(threshold),
        },
        "artifacts": {
            "baseline_ref": payload.get("baseline_ref", "inline://baseline"),
            "current_ref": payload.get("current_ref", "inline://current"),
            "diff_ref": f"inline://diff/{source_id}/{changed_bytes}",
        },
    }
    return 200, response
