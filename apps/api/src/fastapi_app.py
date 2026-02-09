from __future__ import annotations

import json

from .figma_import_endpoint import post_tokens_import_figma
from .llm_contract_endpoints import post_violation_explain, post_violation_fix_suggest
from .rule_audit_endpoint import post_rule_audit, post_rule_report
from .storybook_endpoint import post_storybook_source_import
from .visual_diff_endpoint import post_visual_diff_audit

try:
    from fastapi import Body, FastAPI, Path
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
except ImportError:  # pragma: no cover - optional runtime dependency
    Body = FastAPI = Path = CORSMiddleware = JSONResponse = None


def create_app() -> "FastAPI":
    if FastAPI is None or JSONResponse is None or CORSMiddleware is None:
        raise RuntimeError(
            "fastapi is not installed. Install fastapi and uvicorn to run the HTTP API wrapper."
        )

    app = FastAPI(title="QADMS API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

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

    @app.post("/api/v1/sources/{source_id}/audits/rules")
    def run_rule_audit(
        source_id: str = Path(..., description="Design source identifier"),
        payload: dict = Body(..., description="Figma/Tokens Studio export JSON"),
    ) -> JSONResponse:
        status_code, response = post_rule_audit(
            source_id=source_id,
            request_body=json.dumps(payload).encode("utf-8"),
        )
        return JSONResponse(status_code=status_code, content=response)

    @app.post("/api/v1/sources/{source_id}/audits/report")
    def export_rule_report(
        source_id: str = Path(..., description="Design source identifier"),
        payload: dict = Body(..., description="Figma/Tokens Studio export JSON"),
    ) -> JSONResponse:
        status_code, response = post_rule_report(
            source_id=source_id,
            request_body=json.dumps(payload).encode("utf-8"),
        )
        return JSONResponse(status_code=status_code, content=response)

    @app.post("/api/v1/sources/{source_id}/storybook/import")
    def import_storybook_source(
        source_id: str = Path(..., description="Design source identifier"),
        payload: dict = Body(..., description="Storybook source metadata and component stories"),
    ) -> JSONResponse:
        status_code, response = post_storybook_source_import(
            source_id=source_id,
            request_body=json.dumps(payload).encode("utf-8"),
        )
        return JSONResponse(status_code=status_code, content=response)

    @app.post("/api/v1/sources/{source_id}/audits/visual-diff")
    def run_visual_diff_audit(
        source_id: str = Path(..., description="Design source identifier"),
        payload: dict = Body(..., description="Visual diff baseline/current snapshot references"),
    ) -> JSONResponse:
        status_code, response = post_visual_diff_audit(
            source_id=source_id,
            request_body=json.dumps(payload).encode("utf-8"),
        )
        return JSONResponse(status_code=status_code, content=response)

    @app.post("/api/v1/sources/{source_id}/violations/explain")
    def explain_violation(
        source_id: str = Path(..., description="Design source identifier"),
        payload: dict = Body(..., description="Violation payload for LLM explanation contract"),
    ) -> JSONResponse:
        status_code, response = post_violation_explain(
            source_id=source_id,
            request_body=json.dumps(payload).encode("utf-8"),
        )
        return JSONResponse(status_code=status_code, content=response)

    @app.post("/api/v1/sources/{source_id}/violations/fix-suggest")
    def suggest_violation_fix(
        source_id: str = Path(..., description="Design source identifier"),
        payload: dict = Body(..., description="Violation payload for LLM fix-suggestion contract"),
    ) -> JSONResponse:
        status_code, response = post_violation_fix_suggest(
            source_id=source_id,
            request_body=json.dumps(payload).encode("utf-8"),
        )
        return JSONResponse(status_code=status_code, content=response)

    return app
