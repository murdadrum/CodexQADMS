from __future__ import annotations

import re
from typing import Any

from packages.contracts import CanonicalToken, CanonicalTokenModel, RuleEvaluation, RuleViolation

RULE_ID = "TOKENS_SCALE"
NUMERIC_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")
TARGET_GROUPS = ("spacing", "typography")


def _parse_numeric(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, dict):
        if "$value" in value:
            return _parse_numeric(value["$value"])
        if "value" in value:
            return _parse_numeric(value["value"])
        return None

    if isinstance(value, str):
        match = NUMERIC_PATTERN.search(value.strip())
        if not match:
            return None
        try:
            return float(match.group(0))
        except ValueError:
            return None

    return None


def _build_violation(
    *,
    index: int,
    code: str,
    severity: str,
    title: str,
    description: str,
    token: CanonicalToken,
    evidence: dict[str, object],
    fix_hint: dict[str, object],
) -> RuleViolation:
    return RuleViolation(
        violation_id=f"{RULE_ID}:{index}",
        rule_id=RULE_ID,
        code=code,
        severity=severity,  # type: ignore[arg-type]
        title=title,
        description=description,
        evidence={
            "token_path": token.path,
            "token_name": token.name,
            "token_group": token.group,
            **evidence,
        },
        fix_hint=fix_hint,
    )


def evaluate_tokens_scale(canonical: CanonicalTokenModel) -> RuleEvaluation:
    violations: list[RuleViolation] = []

    for group in TARGET_GROUPS:
        group_tokens = [token for token in canonical.tokens if token.group == group]
        numeric_values: list[tuple[float, CanonicalToken]] = []
        value_to_token: dict[float, CanonicalToken] = {}

        for token in group_tokens:
            number = _parse_numeric(token.value)
            if number is None:
                violations.append(
                    _build_violation(
                        index=len(violations) + 1,
                        code="INVALID_NUMERIC_VALUE",
                        severity="medium",
                        title="Scale Token Is Not Numeric",
                        description="Scale checks require numeric token values.",
                        token=token,
                        evidence={"raw_value": token.value},
                        fix_hint={
                            "action": "set_numeric_value",
                            "group": group,
                            "suggested_value": 1,
                        },
                    )
                )
                continue

            if number <= 0:
                violations.append(
                    _build_violation(
                        index=len(violations) + 1,
                        code="NON_POSITIVE_VALUE",
                        severity="high",
                        title="Scale Token Must Be Positive",
                        description="Scale token values should be greater than zero.",
                        token=token,
                        evidence={"parsed_value": number},
                        fix_hint={
                            "action": "set_positive_value",
                            "group": group,
                            "suggested_value": abs(number) if number != 0 else 1,
                        },
                    )
                )
                continue

            numeric_values.append((number, token))
            value_to_token.setdefault(number, token)

        unique_sorted = sorted({value for value, _ in numeric_values})
        if len(unique_sorted) < 3:
            continue

        deltas = [unique_sorted[i + 1] - unique_sorted[i] for i in range(len(unique_sorted) - 1)]
        min_delta = min(deltas)
        max_delta = max(deltas)
        has_variance = max_delta > min_delta

        for i, delta in enumerate(deltas):
            lower = unique_sorted[i]
            upper = unique_sorted[i + 1]
            lower_token = value_to_token[lower]
            upper_token = value_to_token[upper]

            if min_delta > 0 and delta >= min_delta * 3:
                violations.append(
                    _build_violation(
                        index=len(violations) + 1,
                        code="SCALE_GAP",
                        severity="medium",
                        title="Large Scale Gap Detected",
                        description=(
                            "Scale step jump is significantly larger than the smallest observed step."
                        ),
                        token=upper_token,
                        evidence={
                            "lower_path": lower_token.path,
                            "lower_value": lower,
                            "upper_path": upper_token.path,
                            "upper_value": upper,
                            "delta": delta,
                            "smallest_delta": min_delta,
                        },
                        fix_hint={
                            "action": "adjust_scale_step",
                            "group": group,
                            "suggested_delta": min_delta,
                            "between_values": [lower, upper],
                        },
                    )
                )

            if has_variance and max_delta > 0 and delta <= max_delta / 3:
                violations.append(
                    _build_violation(
                        index=len(violations) + 1,
                        code="SCALE_COMPRESSION",
                        severity="low",
                        title="Compressed Scale Step Detected",
                        description=(
                            "Scale step is much smaller than the largest observed step."
                        ),
                        token=upper_token,
                        evidence={
                            "lower_path": lower_token.path,
                            "lower_value": lower,
                            "upper_path": upper_token.path,
                            "upper_value": upper,
                            "delta": delta,
                            "largest_delta": max_delta,
                        },
                        fix_hint={
                            "action": "normalize_scale_step",
                            "group": group,
                            "suggested_delta": max_delta,
                            "between_values": [lower, upper],
                        },
                    )
                )

    status = "fail" if violations else "pass"
    return RuleEvaluation(rule_id=RULE_ID, status=status, violations=violations)
