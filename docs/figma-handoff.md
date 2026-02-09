# Figma Handoff

## Purpose

Define how Figma prototypes and component documentation feed QADMS without becoming production code.

## Workflow

1. Build or update product flows in Figma.
2. Maintain component specs and accessibility notes in Figma.
3. Export tokens from Figma/Tokens Studio as JSON.
4. Commit exports to `design/tokens/figma/`.
5. Import tokens via API endpoint: `POST /api/v1/sources/{source_id}/tokens/import/figma`.
6. Review validation report and normalization output.

## Naming Conventions

- Token roots: `color`, `spacing`, `typography`, `radius`, `shadow`.
- Paths should be lower-case and semantic.
- Keep token key style consistent across groups.

## Schema Mapping

- Figma export input supports token leaves with either `$value` or `value`.
- Token type supports `$type` or `type`.
- FigmaDMS `theme-config.json` input is also supported:
  - `colors[]` entries map into canonical `color.*` tokens.
  - `uiTokens.radius` maps to `radius.base`.
  - `uiTokens.fontSize` maps to `typography.body.base.fontSize`.
- Normalized canonical token fields:
  - `group`
  - `path`
  - `name`
  - `token_type`
  - `value`
  - `source` (`figma_export`)

## Rules for Generated Code

- Do not import Lovable-generated app code directly into production paths.
- Figma outputs are design/spec inputs only.
- Manually port generated snippets into:
  - `apps/web`
  - `apps/api`
  - `packages/*`
- Current reference bundle location: `/Users/murdadrum/CodexQADMS/FigmaDMS`.

## Release Checklist

- Flow links are up to date in `design/figma-links.md`.
- Component specs include required states and accessibility annotations.
- Token export committed to `design/tokens/figma/`.
- Changelog updated in `design/tokens/CHANGELOG.md`.
- Import endpoint validation passes with zero errors.
