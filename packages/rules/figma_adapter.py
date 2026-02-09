from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any
from uuid import uuid4

from packages.contracts import CanonicalToken, CanonicalTokenModel, ImportResponse, ValidationReport

ALLOWED_GROUPS = {"color", "spacing", "typography", "radius", "shadow"}
ALT_GROUPS = {"colors", "uiTokens"}
DEFAULT_GROUP_TYPES = {
    "color": "color",
    "spacing": "dimension",
    "typography": "dimension",
    "radius": "dimension",
    "shadow": "shadow",
}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", ".", value.lower()).strip(".")
    return slug or "unnamed"


def _is_leaf(node: Any) -> bool:
    return isinstance(node, dict) and ("$value" in node or "value" in node)


def _collect_tokens(
    group: str,
    node: Any,
    segments: list[str],
    tokens: list[CanonicalToken],
    report: ValidationReport,
) -> None:
    path = ".".join([group] + segments) if segments else group

    if _is_leaf(node):
        value = node.get("$value", node.get("value"))
        token_type = node.get("$type", node.get("type", DEFAULT_GROUP_TYPES[group]))
        if value is None:
            report.add_error(path, "Token leaf is missing $value/value.")
            return
        token_name = ".".join(segments)
        tokens.append(
            CanonicalToken(
                group=group,
                path=path,
                name=token_name,
                token_type=str(token_type),
                value=value,
            )
        )
        return

    if isinstance(node, dict):
        for key, child in node.items():
            if not isinstance(key, str):
                report.add_error(path, "Token key must be a string.")
                continue
            _collect_tokens(group, child, [*segments, key], tokens, report)
        return

    report.add_error(path, "Token branches must be objects or token leaves.")


def _collect_theme_config_tokens(
    payload: dict[str, Any], tokens: list[CanonicalToken], report: ValidationReport
) -> bool:
    handled = False

    if "colors" in payload:
        handled = True
        colors = payload["colors"]
        if not isinstance(colors, list):
            report.add_error("colors", "Theme config `colors` must be an array.")
        else:
            for idx, item in enumerate(colors):
                path = f"colors[{idx}]"
                if not isinstance(item, dict):
                    report.add_error(path, "Each color entry must be an object.")
                    continue
                raw_name = item.get("name") or item.get("variable") or f"color_{idx}"
                name = _slugify(str(raw_name).replace("--", ""))
                value = item.get("hex", item.get("hsl"))
                if value is None:
                    report.add_error(path, "Color entry must include `hex` or `hsl`.")
                    continue
                tokens.append(
                    CanonicalToken(
                        group="color",
                        path=f"color.{name}",
                        name=name,
                        token_type="color",
                        value=value,
                    )
                )

    if "uiTokens" in payload:
        handled = True
        ui_tokens = payload["uiTokens"]
        if not isinstance(ui_tokens, dict):
            report.add_error("uiTokens", "Theme config `uiTokens` must be an object.")
        else:
            if "radius" in ui_tokens:
                tokens.append(
                    CanonicalToken(
                        group="radius",
                        path="radius.base",
                        name="base",
                        token_type="dimension",
                        value=ui_tokens["radius"],
                    )
                )
            if "fontSize" in ui_tokens:
                tokens.append(
                    CanonicalToken(
                        group="typography",
                        path="typography.body.base.fontSize",
                        name="body.base.fontSize",
                        token_type="dimension",
                        value=ui_tokens["fontSize"],
                    )
                )

    return handled


def normalize_figma_export(payload: Any) -> tuple[CanonicalTokenModel, ValidationReport]:
    report = ValidationReport(valid=True)
    tokens: list[CanonicalToken] = []

    if not isinstance(payload, dict):
        report.add_error("$", "Figma export must be a JSON object.")
        return CanonicalTokenModel(source="figma_export", tokens=[]), report

    found_group = False
    alt_format_handled = _collect_theme_config_tokens(payload, tokens, report)
    for key, node in payload.items():
        if key in ALLOWED_GROUPS:
            found_group = True
            if not isinstance(node, dict):
                report.add_error(key, "Top-level token group must be an object.")
                continue
            _collect_tokens(key, node, [], tokens, report)
        else:
            if key in ALT_GROUPS and alt_format_handled:
                continue
            report.add_warning(key, "Unknown top-level group ignored by canonical mapping.")

    if not found_group and not alt_format_handled:
        report.add_error("$", "At least one supported token group is required.")

    tokens.sort(key=lambda item: item.path)
    return CanonicalTokenModel(source="figma_export", tokens=tokens), report


def build_import_response(source_id: str, payload: Any) -> ImportResponse:
    canonical, report = normalize_figma_export(payload)
    return ImportResponse(
        source_id=source_id,
        version_id=str(uuid4()),
        imported_at=datetime.now(tz=timezone.utc).isoformat(),
        token_version=canonical,
        validation=report,
    )
