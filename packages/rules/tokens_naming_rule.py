from __future__ import annotations

import re

from packages.contracts import CanonicalToken, CanonicalTokenModel, RuleEvaluation, RuleViolation

RULE_ID = "TOKENS_NAMING"
DOT_SAFE_PATTERN = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*(?:\.[a-z0-9]+(?:[._-][a-z0-9]+)*)*$")
CAMELCASE_BOUNDARY = re.compile(r"([a-z0-9])([A-Z])")


def _normalize_segment(segment: str) -> str:
    segment = CAMELCASE_BOUNDARY.sub(r"\1-\2", segment)
    segment = re.sub(r"[^a-zA-Z0-9_-]+", "-", segment)
    segment = segment.strip("-_").lower()
    return segment or "token"


def _normalize_dot_path(path: str) -> str:
    parts = [part for part in path.split(".") if part]
    if not parts:
        return "token"
    return ".".join(_normalize_segment(part) for part in parts)


def _new_violation(
    *,
    index: int,
    code: str,
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
        severity="medium",
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


def evaluate_tokens_naming(canonical: CanonicalTokenModel) -> RuleEvaluation:
    violations: list[RuleViolation] = []

    for token in canonical.tokens:
        suggested_path = _normalize_dot_path(token.path)
        suggested_name = _normalize_dot_path(token.name)

        if not token.path.startswith(f"{token.group}."):
            violations.append(
                _new_violation(
                    index=len(violations) + 1,
                    code="GROUP_PREFIX",
                    title="Token Path Missing Group Prefix",
                    description="Token path must start with its canonical group prefix.",
                    token=token,
                    evidence={"expected_prefix": f"{token.group}."},
                    fix_hint={
                        "action": "rename_token",
                        "target": "path",
                        "suggested_value": f"{token.group}.{suggested_name}",
                    },
                )
            )

        if not DOT_SAFE_PATTERN.match(token.path):
            violations.append(
                _new_violation(
                    index=len(violations) + 1,
                    code="PATH_FORMAT",
                    title="Token Path Has Invalid Format",
                    description="Use lowercase dot-safe token path segments (a-z, 0-9, -, _).",
                    token=token,
                    evidence={"pattern": DOT_SAFE_PATTERN.pattern},
                    fix_hint={
                        "action": "rename_token",
                        "target": "path",
                        "suggested_value": suggested_path,
                    },
                )
            )

        if not DOT_SAFE_PATTERN.match(token.name):
            violations.append(
                _new_violation(
                    index=len(violations) + 1,
                    code="NAME_FORMAT",
                    title="Token Name Has Invalid Format",
                    description="Use lowercase dot-safe token names (a-z, 0-9, -, _).",
                    token=token,
                    evidence={"pattern": DOT_SAFE_PATTERN.pattern},
                    fix_hint={
                        "action": "rename_token",
                        "target": "name",
                        "suggested_value": suggested_name,
                    },
                )
            )

    status = "fail" if violations else "pass"
    return RuleEvaluation(rule_id=RULE_ID, status=status, violations=violations)
