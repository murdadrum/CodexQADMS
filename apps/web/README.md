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

## Notes
- Keep static files for now (`index.html`, `app.js`, `styles.css`) until the React version reaches feature parity.
- Firebase Auth (Google) will be wired next.
