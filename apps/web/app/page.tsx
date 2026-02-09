import Link from "next/link";
import { ConsolePanel } from "./console-panel";
import { AuthPanel } from "./auth-panel";

const Panel = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <section className="rounded-2xl border border-line/70 bg-white/90 shadow-lg p-6 space-y-3">
    <h2 className="text-xl font-semibold text-ink">{title}</h2>
    {children}
  </section>
);

export default function Home() {
  return (
    <main className="mx-auto max-w-5xl px-4 py-10 space-y-6">
      <header className="space-y-2">
        <p className="uppercase tracking-[0.14em] text-sm text-brand">QADMS</p>
        <h1 className="text-3xl sm:text-4xl font-semibold text-ink">Token Import Console</h1>
        <p className="text-slate-700 max-w-3xl">
          Import Figma/Tokens Studio exports into the canonical token model, run rule audits, and inspect violation
          details directly in the Next.js app.
        </p>
      </header>

      <div className="grid gap-5 md:grid-cols-2">
        <Panel title="Static Console (fallback)">
          <p className="text-sm text-slate-700">The original HTML/JS console remains available during migration.</p>
          <Link
            href="/index.html"
            className="inline-flex w-fit items-center gap-2 rounded-lg bg-brand px-3 py-2 text-white font-medium shadow-sm"
          >
            Open Static Console
          </Link>
        </Panel>

        <Panel title="Local API Health">
          <p className="text-sm text-slate-700">
            Start the stack with <code className="font-mono">./scripts/run_local_stack.sh</code> then check health:
          </p>
          <ul className="list-disc pl-5 text-sm text-slate-800 space-y-1">
            <li>API: http://127.0.0.1:8000/health</li>
            <li>Web: http://127.0.0.1:4173</li>
            <li>Audit: POST /api/v1/sources/&lt;source_id&gt;/audits/rules</li>
            <li>Report: POST /api/v1/sources/&lt;source_id&gt;/audits/report</li>
          </ul>
        </Panel>
      </div>

      <AuthPanel />
      <ConsolePanel />

      <Panel title="Upcoming">
        <ul className="list-disc pl-5 text-sm text-slate-800 space-y-1">
          <li>Auth-gate write actions based on Firebase user context.</li>
          <li>Persist recent imports/audits and filter presets.</li>
          <li>Add report export action from the in-app violations view.</li>
        </ul>
      </Panel>
    </main>
  );
}
