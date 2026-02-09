# apps/web (Next.js)

Next.js migration shell for QADMS. Static console remains available at `/index.html` during the transition.

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
-
- Firebase Auth (Google) stub included; configure env vars to enable sign-in.

## Notes
- Keep static files for now (`index.html`, `app.js`, `styles.css`) until the React version reaches feature parity.
- Env needed for Firebase (create `.env.local` in `apps/web`):
  - `NEXT_PUBLIC_FIREBASE_API_KEY`
  - `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
  - `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
