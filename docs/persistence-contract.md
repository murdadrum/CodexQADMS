# Persistence Contract (A-01)

Last updated: 2026-02-09

## Purpose
Define a DB-ready persistence contract for token import source/version metadata and map it to the existing API response shape.

## Tables (Draft)

### `design_sources`
Stores unique design-system sources.

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `source_id` | TEXT | PK | Client-facing source identifier from API path |
| `source_type` | TEXT | NOT NULL | `figma` initially |
| `created_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |

Suggested indexes:
- PK on `source_id`
- Index on `updated_at`

### `token_source_versions`
Stores each import attempt/version metadata.

| Column | Type | Constraints | Notes |
| --- | --- | --- | --- |
| `version_id` | TEXT | PK | UUID string |
| `source_id` | TEXT | FK -> `design_sources(source_id)` | Source owner |
| `imported_at` | TIMESTAMPTZ | NOT NULL | UTC timestamp |
| `input_format` | TEXT | NOT NULL | `figma_json` initially |
| `input_sha256` | TEXT | NOT NULL | Hash of raw request body |
| `token_source` | TEXT | NOT NULL | Canonical token source (`figma_export`) |
| `token_counts` | JSONB | NOT NULL | Group counts (`color`, `spacing`, etc.) |
| `validation_valid` | BOOLEAN | NOT NULL | True when no validation errors |

Suggested indexes:
- Index on `source_id, imported_at DESC`
- Index on `validation_valid`
- Optional unique index on `source_id, input_sha256` if dedupe is desired

## API Mapping
`POST /api/v1/sources/{source_id}/tokens/import/figma`

Response fields mapped from persistence contract:

| Response Field | Source |
| --- | --- |
| `source_id` | path param / persisted source record |
| `version_id` | persisted token version record |
| `imported_at` | persisted token version record |
| `token_version.*` | normalization pipeline output |
| `validation.*` | normalization pipeline output |

Status rules:
- `200` when `validation.valid == true`
- `422` when `validation.valid == false`
- `400` for malformed JSON payloads

## Code Contract Types
- `packages/contracts/persistence_models.py`
  - `SourceRecord`
  - `TokenVersionRecord`
- `apps/api/src/persistence.py`
  - `TokenImportStore` protocol
  - `InMemoryTokenImportStore` implementation (DB-ready adapter shape)

## Current Implementation Note
Current implementation uses in-memory storage to enforce the contract shape and response mapping. A DB adapter can replace `InMemoryTokenImportStore` without changing endpoint response semantics.
