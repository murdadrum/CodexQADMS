# apps/api

API contracts and implementation for QADMS.

Current scope includes Figma token import contract and normalization adapter integration.
Persistence contract draft is documented in `docs/persistence-contract.md`.

## Endpoints

- `GET /health`
- `POST /api/v1/sources/{source_id}/tokens/import/figma`
- `POST /api/v1/sources/{source_id}/audits/rules`
- `POST /api/v1/sources/{source_id}/audits/report`
- `POST /api/v1/sources/{source_id}/storybook/import`
- `POST /api/v1/sources/{source_id}/audits/visual-diff`
- `POST /api/v1/sources/{source_id}/violations/explain`
- `POST /api/v1/sources/{source_id}/violations/fix-suggest`

Additional contract file for C-D-E scaffolds:
- `apps/api/contracts/milestone-cde.openapi.yaml`

## Error Envelope

For hard request failures (`400`) and unexpected failures (`500`), API returns:

```json
{
  "error": {
    "code": "string_code",
    "message": "human-readable message",
    "details": {}
  }
}
```

## Run

```bash
cd /Users/murdadrum/QADMS
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/api/requirements.txt
python3 -m uvicorn apps.api.src.main:app --host 127.0.0.1 --port 8000
```

Or run API + web together:

```bash
cd /Users/murdadrum/QADMS
./scripts/run_local_stack.sh
```

End-to-end smoke check:

```bash
cd /Users/murdadrum/QADMS
./scripts/smoke_test.sh
```
