# apps/api

API contracts and implementation for QADMS.

Current scope includes Figma token import contract and normalization adapter integration.

## Endpoints

- `GET /health`
- `POST /api/v1/sources/{source_id}/tokens/import/figma`

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
