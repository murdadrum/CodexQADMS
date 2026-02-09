# QADMS Tasks

Last updated: 2026-02-09

## Status Legend
- `todo`: not started
- `in_progress`: active now
- `blocked`: waiting on dependency/decision
- `done`: complete

## Active Sprint (Milestone A Completion)

| ID | Task | Status | Owner | Priority | Depends On | Done When |
| --- | --- | --- | --- | --- | --- | --- |
| A-01 | Finalize source/version persistence contract (DB schema + API mapping) | done | codex | P1 | none | Schema draft and API response mapping approved |
| A-02 | Add persistence adapter for token imports (file/in-memory placeholder -> DB-ready interface) | done | codex | P1 | A-01 | Import endpoint stores version metadata through adapter |
| A-03 | Harden API error envelope for import endpoint | done | codex | P2 | none | All error paths return stable machine-readable shape |
| A-04 | Add endpoint-level tests for malformed payload variants | done | codex | P2 | none | Tests cover invalid JSON, wrong root types, invalid leaf shapes |
| A-05 | Wire web UI to prefer live API and clearly show fallback mode | done | codex | P2 | none | UI indicates API path vs mock path in status |
| A-06 | Ensure docs are aligned with local run + smoke test flow | done | codex | P3 | none | README and app docs match actual scripts |

## Milestone B Backlog (Rules + Core UX)

| ID | Task | Status | Owner | Priority | Depends On | Done When |
| --- | --- | --- | --- | --- | --- | --- |
| B-01 | Implement `TOKENS_NAMING` deterministic rule | done | codex | P1 | A-01 | Rule emits violations with evidence + fix_hint |
| B-02 | Implement `TOKENS_SCALE` deterministic rule | done | codex | P1 | A-01 | Spacing/type scale anomalies are detected |
| B-03 | Implement `TOKENS_SEMANTIC_COVERAGE` rule | done | codex | P1 | A-01 | Missing state semantics flagged |
| B-04 | Implement `A11Y_CONTRAST` rule for color pairs | done | codex | P1 | A-01 | WCAG-based contrast violations produced |
| B-05 | Build violations list UI (filter by severity/category) | done | codex | P1 | B-01 | UI renders deterministic violations and filters |
| B-06 | Build violation detail panel (evidence + fix hint) | done | codex | P2 | B-05 | Evidence and fix hints are readable and complete |
| B-07 | Add report export endpoint (`report.json`) | done | codex | P2 | B-01 | Canonical report payload downloadable |
| B-08 | Migrate core import/audit UI from static console to Next.js app | done | codex | P1 | B-05 | Next.js console reaches functional parity for import/audit/detail |
| B-09 | Add Firebase auth gating to import/audit/report actions | done | codex | P1 | B-08 | Unauthenticated users cannot trigger write/report actions |
| B-10 | Persist recent runs + filter presets in web console | done | codex | P2 | B-08 | State survives refresh and can be restored from UI |

## Milestone C-D-E Backlog (Planned)

| ID | Task | Status | Owner | Priority | Depends On | Done When |
| --- | --- | --- | --- | --- | --- | --- |
| C-01 | Add Storybook source ingestion contract | done | codex | P2 | B-07 | Storybook source object validated and stored |
| C-02 | Add visual diff pipeline scaffold | done | codex | P2 | C-01 | Baseline/current screenshot diff result generated |
| C-03 | Add component-level frontend tests for console state and persistence | done | codex | P2 | B-10 | Recent runs/presets/report UI flows are covered in CI |
| C-04 | Add UI diff viewer screen in Next.js for visual diff results | done | codex | P2 | C-02 | Visual diff endpoint results are browsable in app UI |
| C-05 | Integrate visual diff results with persisted audit history | todo | codex | P2 | C-04 | Visual diff runs are stored and listed in UI |
| C-06 | Add visual diff history view with compare links | todo | codex | P2 | C-05 | Users can navigate past diffs and open artifact refs |
| D-01 | Add CI workflow (`test + smoke`) | done | codex | P1 | A-04 | PR checks run unit + smoke tests automatically |
| D-02 | Add deploy workflow scaffold | done | codex | P2 | D-01 | Build/deploy job skeleton committed |
| D-03 | Add Terraform infra skeleton directories | done | codex | P2 | D-02 | Cloud modules scaffolded with variables |
| D-04 | Connect deploy workflow to provider secrets + real deploy commands | done | codex | P1 | D-02, D-03 | Manual deploy workflow can publish API/web to target environment |
| D-05 | Add environment-specific provider auth + IAM setup docs | done | codex | P2 | D-03 | Cloud identity, service accounts, and IAM roles documented |
| D-06 | Add container build pipeline for API/web images | todo | codex | P1 | D-04 | Images built and pushed from CI/CD |
| E-01 | Add LLM explain endpoint contract | done | codex | P2 | B-06 | Contract defined with deterministic evidence input |
| E-02 | Add LLM fix suggestion endpoint contract | done | codex | P2 | E-01 | Structured patch response shape finalized |

## External Inputs Needed

| ID | Input | Status | Owner | Needed For |
| --- | --- | --- | --- | --- |
| X-01 | Final Figma component-state docs for all core components | in_progress | murdadrum | B-05, B-06 |
| X-02 | Decision on first production auth path (Firebase exact flow) | done | murdadrum | D-series planning |
| X-03 | Decision on Next.js migration start point for `apps/web` | done | murdadrum | B-series UI implementation |

## Immediate Next 3 Tasks
1. C-05 Integrate visual diff results with persisted audit history.
2. C-06 Add visual diff history view with compare links.
3. D-06 Add container build pipeline for API/web images.
