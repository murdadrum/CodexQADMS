from __future__ import annotations

import colorsys
import re
from typing import Any

from packages.contracts import CanonicalToken, CanonicalTokenModel, RuleEvaluation, RuleViolation

RULE_ID = "A11Y_CONTRAST"
WCAG_AA_TEXT_THRESHOLD = 4.5

HEX_PATTERN = re.compile(r"^#([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
RGB_PATTERN = re.compile(r"^rgba?\(([^)]+)\)$")
HSL_PATTERN = re.compile(r"^hsla?\(([^)]+)\)$")

TEXT_MARKERS = ("text", "foreground", "fg")
BG_MARKERS = ("bg", "background", "surface", "canvas", "card")


def _to_rgb(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str):
        return None
    raw = value.strip()

    hex_match = HEX_PATTERN.match(raw)
    if hex_match:
        color = hex_match.group(1)
        if len(color) in (3, 4):
            r = int(color[0] * 2, 16)
            g = int(color[1] * 2, 16)
            b = int(color[2] * 2, 16)
            return (r, g, b)
        if len(color) in (6, 8):
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            return (r, g, b)

    rgb_match = RGB_PATTERN.match(raw)
    if rgb_match:
        parts = [part.strip() for part in rgb_match.group(1).split(",")]
        if len(parts) < 3:
            return None
        try:
            r = int(float(parts[0]))
            g = int(float(parts[1]))
            b = int(float(parts[2]))
        except ValueError:
            return None
        return (_clamp_channel(r), _clamp_channel(g), _clamp_channel(b))

    hsl_match = HSL_PATTERN.match(raw)
    if hsl_match:
        parts = [part.strip() for part in hsl_match.group(1).split(",")]
        if len(parts) < 3:
            return None
        try:
            h = float(parts[0]) % 360.0
            s = _parse_percent(parts[1])
            l = _parse_percent(parts[2])
        except ValueError:
            return None
        r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
        return (_clamp_channel(round(r * 255)), _clamp_channel(round(g * 255)), _clamp_channel(round(b * 255)))

    return None


def _parse_percent(value: str) -> float:
    cleaned = value.strip()
    if cleaned.endswith("%"):
        return float(cleaned[:-1]) / 100.0
    return float(cleaned)


def _clamp_channel(value: int) -> int:
    return max(0, min(255, value))


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        srgb = c / 255.0
        if srgb <= 0.03928:
            return srgb / 12.92
        return ((srgb + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast_ratio(foreground: tuple[int, int, int], background: tuple[int, int, int]) -> float:
    l1 = _relative_luminance(foreground)
    l2 = _relative_luminance(background)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 3)


def _is_text_token(token: CanonicalToken) -> bool:
    path = token.path.lower()
    return any(f".{marker}." in path or path.endswith(f".{marker}") for marker in TEXT_MARKERS)


def _is_bg_token(token: CanonicalToken) -> bool:
    path = token.path.lower()
    return any(f".{marker}." in path or path.endswith(f".{marker}") for marker in BG_MARKERS)


def _build_violation(
    *,
    index: int,
    code: str,
    severity: str,
    title: str,
    description: str,
    text_token: CanonicalToken,
    bg_token: CanonicalToken,
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
            "text_path": text_token.path,
            "text_name": text_token.name,
            "bg_path": bg_token.path,
            "bg_name": bg_token.name,
            **evidence,
        },
        fix_hint=fix_hint,
    )


def evaluate_a11y_contrast(canonical: CanonicalTokenModel) -> RuleEvaluation:
    violations: list[RuleViolation] = []
    color_tokens = [token for token in canonical.tokens if token.group == "color"]
    text_tokens = [token for token in color_tokens if _is_text_token(token)]
    bg_tokens = [token for token in color_tokens if _is_bg_token(token)]

    if not text_tokens or not bg_tokens:
        return RuleEvaluation(rule_id=RULE_ID, status="pass", violations=[])

    for text_token in text_tokens:
        text_rgb = _to_rgb(text_token.value)
        if text_rgb is None:
            violations.append(
                _build_violation(
                    index=len(violations) + 1,
                    code="INVALID_TEXT_COLOR",
                    severity="medium",
                    title="Unparseable Text Color",
                    description="Text color token format is not supported for contrast checks.",
                    text_token=text_token,
                    bg_token=bg_tokens[0],
                    evidence={"raw_text_value": text_token.value},
                    fix_hint={
                        "action": "normalize_color_format",
                        "supported_formats": ["#RRGGBB", "#RGB", "rgb()", "hsl()"],
                    },
                )
            )
            continue

        worst_pair: tuple[float, CanonicalToken, tuple[int, int, int]] | None = None
        for bg_token in bg_tokens:
            bg_rgb = _to_rgb(bg_token.value)
            if bg_rgb is None:
                continue
            ratio = _contrast_ratio(text_rgb, bg_rgb)
            if worst_pair is None or ratio < worst_pair[0]:
                worst_pair = (ratio, bg_token, bg_rgb)

        if worst_pair is None:
            violations.append(
                _build_violation(
                    index=len(violations) + 1,
                    code="INVALID_BACKGROUND_COLOR",
                    severity="medium",
                    title="No Parseable Background Color",
                    description="Background tokens were found, but none could be parsed for contrast checks.",
                    text_token=text_token,
                    bg_token=bg_tokens[0],
                    evidence={"candidate_backgrounds": [token.path for token in bg_tokens]},
                    fix_hint={
                        "action": "normalize_color_format",
                        "supported_formats": ["#RRGGBB", "#RGB", "rgb()", "hsl()"],
                    },
                )
            )
            continue

        ratio, worst_bg, _ = worst_pair
        if ratio < WCAG_AA_TEXT_THRESHOLD:
            severity = "high" if ratio < 3.0 else "medium"
            violations.append(
                _build_violation(
                    index=len(violations) + 1,
                    code="LOW_CONTRAST",
                    severity=severity,
                    title="Text/Background Contrast Below WCAG AA",
                    description="Contrast ratio is below the 4.5:1 threshold for normal text.",
                    text_token=text_token,
                    bg_token=worst_bg,
                    evidence={
                        "text_value": text_token.value,
                        "bg_value": worst_bg.value,
                        "contrast_ratio": ratio,
                        "required_ratio": WCAG_AA_TEXT_THRESHOLD,
                    },
                    fix_hint={
                        "action": "increase_contrast",
                        "required_ratio": WCAG_AA_TEXT_THRESHOLD,
                        "suggestion": "Adjust text or background token values to increase luminance difference.",
                    },
                )
            )

    status = "fail" if violations else "pass"
    return RuleEvaluation(rule_id=RULE_ID, status=status, violations=violations)
