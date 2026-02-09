from __future__ import annotations

from packages.contracts import CanonicalToken, CanonicalTokenModel, RuleEvaluation, RuleViolation

RULE_ID = "TOKENS_SEMANTIC_COVERAGE"
REQUIRED_STATES = ("hover", "focus", "disabled")
INTERACTIVE_SEGMENTS = {"button", "link", "action", "control", "input", "cta", "interactive"}


def _is_state_segment(segment: str) -> bool:
    return segment in REQUIRED_STATES


def _is_interactive_path(segments: list[str]) -> bool:
    return any(segment in INTERACTIVE_SEGMENTS for segment in segments)


def _root_without_state(path: str) -> tuple[str, str | None]:
    segments = path.split(".")
    last = segments[-1] if segments else ""
    if _is_state_segment(last):
        return ".".join(segments[:-1]), last
    return path, None


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


def evaluate_tokens_semantic_coverage(canonical: CanonicalTokenModel) -> RuleEvaluation:
    violations: list[RuleViolation] = []
    color_tokens = [token for token in canonical.tokens if token.group == "color"]
    path_to_token = {token.path: token for token in color_tokens}

    candidate_roots: dict[str, CanonicalToken] = {}
    seen_states: dict[str, set[str]] = {}

    for token in color_tokens:
        segments = token.path.split(".")
        if len(segments) < 3:
            continue
        if not _is_interactive_path(segments):
            continue

        root, state = _root_without_state(token.path)
        candidate_roots.setdefault(root, token)
        if state:
            seen_states.setdefault(root, set()).add(state)

    for root, representative_token in candidate_roots.items():
        root_token = path_to_token.get(root)
        states = seen_states.get(root, set())

        if root_token is None:
            violations.append(
                _build_violation(
                    index=len(violations) + 1,
                    code="MISSING_BASE_STATE",
                    severity="medium",
                    title="Missing Base Semantic Token",
                    description=(
                        "State tokens exist but the base semantic token is missing."
                    ),
                    token=representative_token,
                    evidence={"root_path": root, "states_found": sorted(states)},
                    fix_hint={
                        "action": "create_base_semantic_token",
                        "root_path": root,
                    },
                )
            )

        missing_states = [state for state in REQUIRED_STATES if state not in states]
        if missing_states:
            violations.append(
                _build_violation(
                    index=len(violations) + 1,
                    code="MISSING_SEMANTIC_STATES",
                    severity="medium",
                    title="Missing Semantic State Coverage",
                    description=(
                        "Interactive semantic tokens should provide hover, focus, and disabled states."
                    ),
                    token=root_token or representative_token,
                    evidence={
                        "root_path": root,
                        "required_states": list(REQUIRED_STATES),
                        "present_states": sorted(states),
                        "missing_states": missing_states,
                    },
                    fix_hint={
                        "action": "add_semantic_states",
                        "root_path": root,
                        "missing_states": missing_states,
                    },
                )
            )

    status = "fail" if violations else "pass"
    return RuleEvaluation(rule_id=RULE_ID, status=status, violations=violations)
