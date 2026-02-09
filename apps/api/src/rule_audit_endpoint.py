from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from packages.rules import (
    evaluate_a11y_contrast,
    evaluate_tokens_naming,
    evaluate_tokens_scale,
    evaluate_tokens_semantic_coverage,
    normalize_figma_export,
)

from .error_envelope import error_response

RULE_CATEGORY = {
    "TOKENS_NAMING": "tokens",
    "TOKENS_SCALE": "tokens",
    "TOKENS_SEMANTIC_COVERAGE": "tokens",
    "A11Y_CONTRAST": "a11y",
}


def _build_violation_payload(rule_id: str, violation: Any) -> dict[str, Any]:
    category = RULE_CATEGORY.get(rule_id, "other")
    return {
        "violation_id": violation.violation_id,
        "rule_id": violation.rule_id,
        "category": category,
        "severity": violation.severity,
        "code": violation.code,
        "title": violation.title,
        "description": violation.description,
        "evidence": violation.evidence,
        "fix_hint": violation.fix_hint,
    }


def post_rule_audit(source_id: str, request_body: bytes) -> tuple[int, dict[str, Any]]:
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
        canonical, validation = normalize_figma_export(payload)
        evaluations = [
            evaluate_tokens_naming(canonical),
            evaluate_tokens_scale(canonical),
            evaluate_tokens_semantic_coverage(canonical),
            evaluate_a11y_contrast(canonical),
        ]

        violations: list[dict[str, Any]] = []
        for evaluation in evaluations:
            for violation in evaluation.violations:
                violations.append(_build_violation_payload(evaluation.rule_id, violation))

        # Deterministic order for stable UI/test behavior.
        violations.sort(
            key=lambda item: (
                item["severity"],
                item["category"],
                item["rule_id"],
                item["code"],
                item["violation_id"],
            )
        )

        severity_counts = Counter(violation["severity"] for violation in violations)
        category_counts = Counter(violation["category"] for violation in violations)
        rule_counts = Counter(violation["rule_id"] for violation in violations)

        response = {
            "source_id": source_id,
            "audit_id": str(uuid4()),
            "evaluated_at": datetime.now(tz=timezone.utc).isoformat(),
            "normalization": {
                "valid": validation.valid,
                "error_count": len(validation.errors),
                "warning_count": len(validation.warnings),
            },
            "summary": {
                "total_violations": len(violations),
                "by_severity": {
                    "low": severity_counts.get("low", 0),
                    "medium": severity_counts.get("medium", 0),
                    "high": severity_counts.get("high", 0),
                    "critical": severity_counts.get("critical", 0),
                },
                "by_category": {
                    "tokens": category_counts.get("tokens", 0),
                    "a11y": category_counts.get("a11y", 0),
                    "other": category_counts.get("other", 0),
                },
                "by_rule": dict(sorted(rule_counts.items())),
            },
            "violations": violations,
        }
        return 200, response
    except Exception:
        return error_response(
            status_code=500,
            code="internal_error",
            message="Unexpected server error while running rule audit.",
        )
