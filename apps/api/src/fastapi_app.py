from __future__ import annotations

import json

from .figma_import_endpoint import post_tokens_import_figma

try:
    from fastapi import Body, FastAPI, Path
    from fastapi.responses import JSONResponse
except ImportError:  # pragma: no cover - optional runtime dependency
    Body = FastAPI = Path = JSONResponse = None


def create_app() -> "FastAPI":
    if FastAPI is None or JSONResponse is None:
        raise RuntimeError(
            "fastapi is not installed. Install fastapi and uvicorn to run the HTTP API wrapper."
        )

    app = FastAPI(title="QADMS API", version="0.1.0")

    @app.post("/api/v1/sources/{source_id}/tokens/import/figma")
    def import_figma_tokens(
        source_id: str = Path(..., description="Design source identifier"),
        payload: dict = Body(..., description="Figma/Tokens Studio export JSON"),
    ) -> JSONResponse:
        status_code, response = post_tokens_import_figma(
            source_id=source_id,
            request_body=json.dumps(payload).encode("utf-8"),
        )
        return JSONResponse(status_code=status_code, content=response)

    return app
