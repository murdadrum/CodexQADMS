# QADMS Project Plan

Last updated: 2026-02-09

## Goal
Build a production-style QA Design Management System that ingests design tokens/components, runs deterministic quality checks, and presents violations, evidence, and remediation guidance.

## Success Criteria
- Token imports work from Tokens Studio-style JSON and FigmaDMS `theme-config.json`.
- Canonical token model and validation reports are deterministic.
- Web UI shows import provenance (`source_id`, `version_id`, `imported_at`, `source`).
- Local stack can be started and verified with a one-command smoke test.
- Repo is ready for expansion into auth, jobs, integrations, and cloud deployment.

## Scope
In scope now:
- Figma-centered handoff workflow docs and token contract.
- FastAPI token import endpoint.
- Token normalization adapter and tests.
- Web import/provenance console.
- Local dev runner and smoke testing.

Out of scope for current slice:
- Multi-tenant auth and RBAC enforcement.
- Async audit worker orchestration (Celery).
- Cloud infra modules (Terraform, Cloud Run, SQL, GCS).
- GitHub/Slack/Jira integrations.
- Full rule catalog and visual regression pipeline.

## Architecture Decisions (Locked)
- Monorepo structure under `apps/`, `packages/`, `design/`, `docs/`, `tests/`.
- API stack: FastAPI.
- Contract-first endpoint: `POST /api/v1/sources/{source_id}/tokens/import/figma`.
- Canonical source marker: `figma_export`.
- Deterministic normalization for pass/fail.
- Figma artifacts are inputs only; generated code is reference-only.

## Milestones

### Milestone A: Foundation and Import Pipeline
Status: In progress
- Done:
  - Hybrid workflow docs and Figma link registry.
  - Token fixtures including `theme-config.json`.
  - Import endpoint contract and implementation.
  - Persistence contract draft (schema + API mapping).
  - DB-ready in-memory import persistence adapter and endpoint mapping.
  - Normalization adapter with validation reporting.
  - Unit tests for valid/invalid import and canonical parity.
  - Web provenance console.
  - Local runner and smoke test script.
- Remaining:
  - Formal source/version persistence layer (DB).
  - API error contract hardening and pagination-ready response envelopes.

### Milestone B: Rule Engine and Core UX
Status: Not started
- Deterministic rules package expansion (`naming`, `scale`, `semantic coverage`, `contrast`).
- Violation list/detail UI with filtering and severity.
- Report export endpoints and static report output.

### Milestone C: Components and Visual Regression
Status: Not started
- Storybook ingestion path.
- Baseline vs current screenshot capture and diff evaluation.
- UI diff viewer.

### Milestone D: Integrations and CI/CD/Infra
Status: Not started
- GitHub integration and PR check reporting.
- CI workflows for test/build/e2e.
- Terraform baseline for Cloud Run stack.

### Milestone E: LLM Add-ons
Status: Not started
- Explanation and fix-suggestion endpoints.
- Structured output contracts and evidence-bound prompts.

## Risks and Mitigations
- Port conflicts in local dev: solved with configurable ports and fail-fast checks.
- Drift between design and implementation: mitigated with explicit handoff docs and link registry.
- Over-reliance on generated UI code: mitigated by manual-porting policy.
- Contract drift between API and web: mitigated by smoke test and contract-first endpoint shape.

## Current Artifacts
- Plan source: `ChatGPTplanning-1.md`
- Handoff guide: `docs/figma-handoff.md`
- Figma registry: `design/figma-links.md`
- API contract: `apps/api/contracts/figma-import.openapi.yaml`
- Smoke test: `scripts/smoke_test.sh`

## Next Decision Gates
- Approve persistence model for source/version/audit tables.
- Choose first deterministic rule set order for Milestone B.
- Decide web migration timing from static prototype to full Next.js app scaffold.
