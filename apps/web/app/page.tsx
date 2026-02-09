import Link from "next/link";

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
        <h1 className="text-3xl sm:text-4xl font-semibold text-ink">Next.js Console (in progress)</h1>
        <p className="text-slate-700 max-w-3xl">
          We are migrating the token import and violations console to Next.js with Tailwind/shadcn. Use the static
          console for now while this shell stabilizes.
        </p>
      </header>

      <div className="grid gap-5 md:grid-cols-2">
        <Panel title="Static Console (current)">
          <p className="text-sm text-slate-700">Run imports and rule audits via the existing static UI.</p>
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

      <Panel title="Upcoming">
        <ul className="list-disc pl-5 text-sm text-slate-800 space-y-1">
          <li>Port import + audit UI into React components.</li>
          <li>Connect Firebase Auth (Google) for sign-in gating.</li>
          <li>Style with Tailwind + shadcn and keep the intentional visual direction.</li>
        </ul>
      </Panel>
    </main>
  );
}
