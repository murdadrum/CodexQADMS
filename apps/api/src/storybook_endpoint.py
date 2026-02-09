from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .error_envelope import error_response

_STORYBOOK_IMPORTS: dict[str, list[dict[str, Any]]] = {}


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _validate_component(component: Any, index: int) -> tuple[bool, str]:
    if not isinstance(component, dict):
        return False, f"components[{index}] must be an object."
    component_id = component.get("component_id")
    if not isinstance(component_id, str) or not component_id.strip():
        return False, f"components[{index}].component_id must be a non-empty string."
    stories = component.get("stories")
    if not isinstance(stories, list) or any(not isinstance(story, str) or not story.strip() for story in stories):
        return False, f"components[{index}].stories must be an array of non-empty strings."
    return True, ""


def post_storybook_source_import(source_id: str, request_body: bytes) -> tuple[int, dict[str, Any]]:
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
            code="invalid_storybook_payload",
            message="Storybook import payload must be a JSON object.",
        )

    storybook_url = payload.get("storybook_url")
    build_artifact_url = payload.get("build_artifact_url")
    if not isinstance(storybook_url, str) or not storybook_url.strip():
        return error_response(
            status_code=400,
            code="invalid_storybook_payload",
            message="`storybook_url` must be a non-empty string.",
        )
    if build_artifact_url is not None and (
        not isinstance(build_artifact_url, str) or not build_artifact_url.strip()
    ):
        return error_response(
            status_code=400,
            code="invalid_storybook_payload",
            message="`build_artifact_url` must be a non-empty string when provided.",
        )

    components = payload.get("components", [])
    if not isinstance(components, list):
        return error_response(
            status_code=400,
            code="invalid_storybook_payload",
            message="`components` must be an array.",
        )
    for idx, component in enumerate(components):
        valid, message = _validate_component(component, idx)
        if not valid:
            return error_response(
                status_code=400,
                code="invalid_storybook_payload",
                message=message,
            )

    normalized_components = [
        {
            "component_id": component["component_id"].strip(),
            "title": str(component.get("title", component["component_id"])).strip(),
            "stories": [story.strip() for story in component["stories"]],
        }
        for component in components
    ]

    record = {
        "source_id": source_id,
        "ingestion_id": str(uuid4()),
        "imported_at": _now_iso(),
        "storybook_url": storybook_url.strip(),
        "build_artifact_url": build_artifact_url.strip() if isinstance(build_artifact_url, str) else None,
        "version_label": str(payload.get("version_label", "latest")),
        "component_count": len(normalized_components),
        "story_count": sum(len(component["stories"]) for component in normalized_components),
        "components": normalized_components,
        "metadata": payload.get("metadata", {}) if isinstance(payload.get("metadata"), dict) else {},
    }

    _STORYBOOK_IMPORTS.setdefault(source_id, []).append(record)
    return 200, record
