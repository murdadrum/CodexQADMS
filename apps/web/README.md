# apps/web

Token import and provenance UI prototype for QADMS.

## Features

- Calls `POST /api/v1/sources/{source_id}/tokens/import/figma`
- Displays provenance fields: `source_id`, `version_id`, `imported_at`, `token_version.source`
- Shows validation errors/warnings and token summary
- Includes a local mock fallback for offline demos

## Run

Preferred (API + web together):

```bash
cd /Users/murdadrum/QADMS
./scripts/run_local_stack.sh
```

If default ports are already in use:

```bash
cd /Users/murdadrum/QADMS
API_PORT=18000 WEB_PORT=14173 ./scripts/run_local_stack.sh
```

Web-only:

```bash
cd /Users/murdadrum/QADMS/apps/web
python3 -m http.server 4173
```

Open http://127.0.0.1:4173

## Notes

- Keep this UI manually authored and aligned with Figma references.
- Do not copy generated design-tool code directly into production paths.
