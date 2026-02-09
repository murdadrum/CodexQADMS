# QADMS

QA Design Management System (QADMS): a full-stack platform for auditing design tokens and component systems for consistency, accessibility, and quality.

## Scope

- Design token ingestion and normalization
- Deterministic QA rule execution
- Violation reporting with evidence and remediation hints
- Figma-driven workflow where design assets are inputs, not production code

## Current Status

The repository currently includes:

- Hybrid workflow docs for Codex + Figma handoff
- Contract for `POST /api/v1/sources/{source_id}/tokens/import/figma`
- Deterministic `TOKENS_NAMING` rule (violations + evidence + fix hints)
- Deterministic `TOKENS_SCALE` rule (spacing/typography anomaly detection)
- Deterministic `TOKENS_SEMANTIC_COVERAGE` rule (interactive state coverage)
- Deterministic `A11Y_CONTRAST` rule (WCAG AA text/background ratio checks)
- Violations list UI with deterministic API-backed filters (`severity`, `category`, `rule`, `search`)
- Violation detail view with evidence and fix hints
- Next.js React console with Firebase-auth gated import/audit/report actions
- Report export UI wired to `POST /api/v1/sources/{source_id}/audits/report`
- Local persistence for recent runs and filter presets (with recent-run detail drawer)
- Storybook ingestion scaffold endpoint + contract (`/storybook/import`)
- Visual diff scaffold endpoint + contract (`/audits/visual-diff`)
- LLM explain/fix-suggest contract endpoints for violations
- CI workflow for Python tests + web build + smoke test
- Deploy workflow scaffold with manual environment selection and dry-run mode
- Terraform skeleton for Cloud Run-style deployments (`infra/terraform`)
- Visual diff viewer panel in Next.js (calls `/audits/visual-diff`)
- Token normalization adapter for:
  - Tokens Studio-style grouped JSON
  - FigmaDMS `theme-config.json` shape (`colors[]`, `uiTokens`)
- Unit tests validating import behavior and canonical parity

## Repository Layout

- `apps/api` API contracts and endpoint handlers
- `apps/web` Next.js frontend (active UI) + static fallback console
- `packages/contracts` shared token/report contracts
- `packages/rules` token adapters and rule utilities
- `design` Figma links, component spec guidance, token handoff artifacts
- `docs` handoff and project documentation
- `tests` importer and rule behavior tests
- `.github/workflows` CI workflows
- `infra/terraform` IaC baseline
- `docs/deploy-gcp.md` deployment setup guide
- `docs/iam-gcp.md` IAM + auth setup for staging/production
- `docs/build-images-gcp.md` image build/push guide

## Planning and Tracking

- Project plan: `PROJECT_PLAN.md`
- Task backlog: `TASKS.md`
- Initial strategy source: `ChatGPTplanning-1.md`
- Persistence contract draft: `docs/persistence-contract.md`
- Web walkthrough: `Walkthrough.md`

## Quick Start (current)

```bash
python3 -m unittest -v
cd apps/web && npm install && npm run build
```

## Smoke Test (API + Web + Import)

```bash
./scripts/smoke_test.sh
```

- Uses default ports `18000` (API) and `14173` (web).
- Verifies import, audit, and report endpoints.
- Override if needed:
  - `API_PORT=18080 WEB_PORT=14174 ./scripts/smoke_test.sh`

## Run Local Stack (API + Web)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/api/requirements.txt
./scripts/run_local_stack.sh
```

- API health: `http://127.0.0.1:8000/health`
- Web UI: `http://127.0.0.1:4173`
- If either port is busy, override at launch:
  - `API_PORT=18000 WEB_PORT=14173 ./scripts/run_local_stack.sh`

## Hybrid Workflow Rule

- Figma prototypes and component documentation are sources of truth for design intent.
- Generated code bundles (for example from design tools) are reference-only.
- Production implementation is authored manually in this repository.

## License

This project is licensed under the MIT License. See `LICENSE`.
