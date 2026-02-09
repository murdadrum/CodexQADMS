from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

RuleStatus = Literal["pass", "fail"]
Severity = Literal["low", "medium", "high", "critical"]


@dataclass
class RuleViolation:
    violation_id: str
    rule_id: str
    code: str
    severity: Severity
    title: str
    description: str
    evidence: dict[str, Any] = field(default_factory=dict)
    fix_hint: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RuleEvaluation:
    rule_id: str
    status: RuleStatus
    violations: list[RuleViolation] = field(default_factory=list)

    @property
    def violation_count(self) -> int:
        return len(self.violations)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "status": self.status,
            "violation_count": self.violation_count,
            "violations": [violation.to_dict() for violation in self.violations],
        }
