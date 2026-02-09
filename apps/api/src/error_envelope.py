from __future__ import annotations

from typing import Any


def error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    return status_code, {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        }
    }
