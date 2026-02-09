from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .error_envelope import error_response


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _parse_payload(source_id: str, request_body: bytes) -> tuple[int, dict[str, Any]] | tuple[None, dict[str, Any]]:
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
            code="invalid_llm_payload",
            message="LLM contract payload must be a JSON object.",
        )
    return None, payload


def _extract_violation(payload: dict[str, Any]) -> dict[str, Any] | tuple[int, dict[str, Any]]:
    violation = payload.get("violation")
    if not isinstance(violation, dict):
        return error_response(
            status_code=400,
            code="invalid_llm_payload",
            message="`violation` must be an object.",
        )
    required = ["rule_id", "code", "title", "description", "evidence", "fix_hint"]
    for field in required:
        if field not in violation:
            return error_response(
                status_code=400,
                code="invalid_llm_payload",
                message=f"`violation.{field}` is required.",
            )
    if not isinstance(violation.get("evidence"), dict):
        return error_response(
            status_code=400,
            code="invalid_llm_payload",
            message="`violation.evidence` must be an object.",
        )
    if not isinstance(violation.get("fix_hint"), dict):
        return error_response(
            status_code=400,
            code="invalid_llm_payload",
            message="`violation.fix_hint` must be an object.",
        )
    return violation


def post_violation_explain(source_id: str, request_body: bytes) -> tuple[int, dict[str, Any]]:
    error_status, parsed = _parse_payload(source_id, request_body)
    if error_status is not None:
        return error_status, parsed
    violation_or_error = _extract_violation(parsed)
    if isinstance(violation_or_error, tuple):
        return violation_or_error

    violation = violation_or_error
    evidence = violation.get("evidence", {})
    evidence_keys = sorted(evidence.keys())
    explanation = {
        "source_id": source_id,
        "explanation_id": str(uuid4()),
        "generated_at": _now_iso(),
        "model": "contract_stub_v1",
        "summary": f"{violation['rule_id']}::{violation['code']} impacts design quality and should be addressed.",
        "rationale": (
            f"Violation '{violation['title']}' indicates a deterministic rule failure. "
            "Addressing it reduces accessibility and consistency drift risk."
        ),
        "evidence_citations": [f"evidence.{key}" for key in evidence_keys],
        "confidence": 0.76,
    }
    return 200, explanation


def post_violation_fix_suggest(source_id: str, request_body: bytes) -> tuple[int, dict[str, Any]]:
    error_status, parsed = _parse_payload(source_id, request_body)
    if error_status is not None:
        return error_status, parsed
    violation_or_error = _extract_violation(parsed)
    if isinstance(violation_or_error, tuple):
        return violation_or_error

    violation = violation_or_error
    fix_hint = violation.get("fix_hint", {})
    suggestion = {
        "source_id": source_id,
        "suggestion_id": str(uuid4()),
        "generated_at": _now_iso(),
        "model": "contract_stub_v1",
        "suggested_changes": [
            {
                "target": fix_hint.get("token_path", violation.get("code", "unknown")),
                "action": fix_hint.get("action", "review_and_update"),
                "reason": violation.get("description", ""),
                "before": fix_hint.get("current", "unknown"),
                "after": fix_hint.get("recommended", "update to compliant semantic token"),
            }
        ],
        "verification_steps": [
            "Re-run deterministic audit rules for this source.",
            "Confirm violation is no longer present in report output.",
        ],
    }
    return 200, suggestion
