# CodexQADMS

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
- Token normalization adapter for:
  - Tokens Studio-style grouped JSON
  - FigmaDMS `theme-config.json` shape (`colors[]`, `uiTokens`)
- Unit tests validating import behavior and canonical parity

## Repository Layout

- `apps/api` API contracts and endpoint handlers
- `apps/web` frontend app target (scaffold)
- `packages/contracts` shared token/report contracts
- `packages/rules` token adapters and rule utilities
- `design` Figma links, component spec guidance, token handoff artifacts
- `docs` handoff and project documentation
- `tests` importer and rule behavior tests

## Quick Start (current)

```bash
python3 -m unittest -v tests.test_figma_import
```

## Hybrid Workflow Rule

- Figma prototypes and component documentation are sources of truth for design intent.
- Generated code bundles (for example from design tools) are reference-only.
- Production implementation is authored manually in this repository.

## License

This project is licensed under the MIT License. See `LICENSE`.
