# apps/web (Next.js)

Primary web UI for QADMS. Static console remains available at `/index.html` as a fallback.

## Run (local)

```bash
cd /Users/murdadrum/QADMS/apps/web
npm install
npm run dev
```

- Next.js: http://127.0.0.1:3000
- Static console (existing): http://127.0.0.1:4173 (via `./scripts/run_local_stack.sh`)

## Stack
- Next.js 15 (App Router)
- Tailwind CSS
- Custom gradient theme (matching current static console feel)
- Firebase Auth (Google) integration for action gating

## Implemented UI Features
- Import tokens via API with optional local mock fallback
- Run rule audit and inspect violations with filters
- View violation details with evidence and fix hints
- Export report JSON from violations view
- Persist recent runs and filter presets in local storage
- Recent run detail drawer before loading saved payloads

## Notes
- Static files remain (`index.html`, `app.js`, `styles.css`) as fallback and reference.
- Env needed for Firebase (create `.env.local` in `apps/web`):
  - `NEXT_PUBLIC_FIREBASE_API_KEY`
  - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
  - `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- When Firebase env vars are set, import/audit/report actions require signed-in user.
