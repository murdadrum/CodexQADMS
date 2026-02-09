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
| B-07 | Add report export endpoint (`report.json`) | todo | codex | P2 | B-01 | Canonical report payload downloadable |

## Milestone C-D-E Backlog (Planned)

| ID | Task | Status | Owner | Priority | Depends On | Done When |
| --- | --- | --- | --- | --- | --- | --- |
| C-01 | Add Storybook source ingestion contract | todo | codex | P2 | B-07 | Storybook source object validated and stored |
| C-02 | Add visual diff pipeline scaffold | todo | codex | P2 | C-01 | Baseline/current screenshot diff result generated |
| D-01 | Add CI workflow (`test + smoke`) | todo | codex | P1 | A-04 | PR checks run unit + smoke tests automatically |
| D-02 | Add deploy workflow scaffold | todo | codex | P2 | D-01 | Build/deploy job skeleton committed |
| D-03 | Add Terraform infra skeleton directories | todo | codex | P2 | D-02 | Cloud modules scaffolded with variables |
| E-01 | Add LLM explain endpoint contract | todo | codex | P2 | B-06 | Contract defined with deterministic evidence input |
| E-02 | Add LLM fix suggestion endpoint contract | todo | codex | P2 | E-01 | Structured patch response shape finalized |

## External Inputs Needed

| ID | Input | Status | Owner | Needed For |
| --- | --- | --- | --- | --- |
| X-01 | Final Figma component-state docs for all core components | in_progress | murdadrum | B-05, B-06 |
| X-02 | Decision on first production auth path (Firebase exact flow) | done | murdadrum | D-series planning |
| X-03 | Decision on Next.js migration start point for `apps/web` | done | murdadrum | B-series UI implementation |

## Immediate Next 3 Tasks
1. B-07 Add report export endpoint (`report.json`).
2. C-01 Add Storybook source ingestion contract.
3. C-02 Add visual diff pipeline scaffold.
