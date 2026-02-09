"use client";

import { useState } from "react";

type VisualDiffResponse = {
  source_id: string;
  diff_id: string;
  evaluated_at: string;
  status: "pass" | "fail";
  summary: {
    baseline_bytes: number;
    current_bytes: number;
    changed_bytes: number;
    diff_ratio: number;
    threshold: number;
  };
  artifacts: {
    baseline_ref: string;
    current_ref: string;
    diff_ref: string;
  };
};

function getApiErrorMessage(body: any, status: number) {
  if (body?.error?.message) {
    return `${body.error.message}${body.error.code ? ` (${body.error.code})` : ""}`;
  }
  if (body?.message) {
    return body.message;
  }
  return `Request failed with status ${status}`;
}

function mockVisualDiff(sourceId: string, baseline: string, current: string, threshold: number): VisualDiffResponse {
  const baselineBytes = new TextEncoder().encode(baseline).length;
  const currentBytes = new TextEncoder().encode(current).length;
  const changedBytes = Math.abs(baselineBytes - currentBytes);
  const diffRatio = changedBytes / Math.max(baselineBytes, currentBytes, 1);
  return {
    source_id: sourceId,
    diff_id: `mock-diff-${Date.now()}`,
    evaluated_at: new Date().toISOString(),
    status: diffRatio <= threshold ? "pass" : "fail",
    summary: {
      baseline_bytes: baselineBytes,
      current_bytes: currentBytes,
      changed_bytes: changedBytes,
      diff_ratio: Number(diffRatio.toFixed(6)),
      threshold,
    },
    artifacts: {
      baseline_ref: "inline://baseline",
      current_ref: "inline://current",
      diff_ref: "inline://diff/mock",
    },
  };
}

export function VisualDiffPanel() {
  const [sourceId, setSourceId] = useState("source-theme");
  const [apiBase, setApiBase] = useState("http://127.0.0.1:8000");
  const [baselineSnapshot, setBaselineSnapshot] = useState("component:button:default");
  const [currentSnapshot, setCurrentSnapshot] = useState("component:button:danger");
  const [baselineRef, setBaselineRef] = useState("");
  const [currentRef, setCurrentRef] = useState("");
  const [threshold, setThreshold] = useState(0.05);
  const [useMockFallback, setUseMockFallback] = useState(true);
  const [status, setStatus] = useState("Ready.");
  const [statusTone, setStatusTone] = useState<"" | "error" | "warn">("");
  const [result, setResult] = useState<VisualDiffResponse | null>(null);

  async function runDiff() {
    const trimmedSource = sourceId.trim();
    if (!trimmedSource) {
      setStatusTone("error");
      setStatus("Source ID is required.");
      return;
    }
    if (!baselineSnapshot.trim() || !currentSnapshot.trim()) {
      setStatusTone("error");
      setStatus("Baseline and current snapshot labels are required.");
      return;
    }
    setStatusTone("");
    setStatus("Running visual diff...");

    const payload = {
      baseline_snapshot: baselineSnapshot,
      current_snapshot: currentSnapshot,
      baseline_ref: baselineRef || undefined,
      current_ref: currentRef || undefined,
      threshold,
    };

    try {
      const base = apiBase.replace(/\/$/, "");
      const response = await fetch(`${base}/api/v1/sources/${encodeURIComponent(trimmedSource)}/audits/visual-diff`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(payload),
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(getApiErrorMessage(body, response.status));
      }
      setResult(body);
      setStatusTone("");
      setStatus("Visual diff completed using live API.");
      return;
    } catch (error: any) {
      if (!useMockFallback) {
        setStatusTone("error");
        setStatus(`Visual diff API error: ${error?.message || "Unknown error"}`);
        return;
      }
    }

    const mockResult = mockVisualDiff(trimmedSource, baselineSnapshot, currentSnapshot, threshold);
    setResult(mockResult);
    setStatusTone("warn");
    setStatus("API unavailable. Visual diff simulated locally.");
  }

  return (
    <section className="rounded-2xl border border-line/70 bg-white/90 p-6 shadow-lg space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-xl font-semibold text-ink">Visual Diff Viewer</h2>
        <button onClick={runDiff} className="rounded-lg bg-brand px-3 py-2 text-sm font-semibold text-white shadow-sm">
          Run Visual Diff
        </button>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <label className="grid gap-1 text-sm text-ink">
          Source ID
          <input
            type="text"
            value={sourceId}
            onChange={(event) => setSourceId(event.target.value)}
            className="rounded-lg border border-line bg-white px-3 py-2 font-mono text-sm"
          />
        </label>
        <label className="grid gap-1 text-sm text-ink">
          API Base URL
          <input
            type="url"
            value={apiBase}
            onChange={(event) => setApiBase(event.target.value)}
            className="rounded-lg border border-line bg-white px-3 py-2 font-mono text-sm"
          />
        </label>
        <label className="grid gap-1 text-sm text-ink">
          Baseline Snapshot
          <input
            type="text"
            value={baselineSnapshot}
            onChange={(event) => setBaselineSnapshot(event.target.value)}
            className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
          />
        </label>
        <label className="grid gap-1 text-sm text-ink">
          Current Snapshot
          <input
            type="text"
            value={currentSnapshot}
            onChange={(event) => setCurrentSnapshot(event.target.value)}
            className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
          />
        </label>
        <label className="grid gap-1 text-sm text-ink">
          Baseline Ref (optional)
          <input
            type="text"
            value={baselineRef}
            onChange={(event) => setBaselineRef(event.target.value)}
            className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
          />
        </label>
        <label className="grid gap-1 text-sm text-ink">
          Current Ref (optional)
          <input
            type="text"
            value={currentRef}
            onChange={(event) => setCurrentRef(event.target.value)}
            className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
          />
        </label>
        <label className="grid gap-1 text-sm text-ink">
          Diff Threshold (0-1)
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={threshold}
            onChange={(event) => setThreshold(Number(event.target.value))}
            className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
          />
        </label>
        <label className="flex items-center gap-2 text-sm text-ink">
          <input
            type="checkbox"
            checked={useMockFallback}
            onChange={(event) => setUseMockFallback(event.target.checked)}
            className="h-4 w-4 accent-brand"
          />
          Use local mock diff if API is unavailable
        </label>
      </div>

      <p
        className={[
          "text-sm",
          statusTone === "error" ? "text-red-700" : "",
          statusTone === "warn" ? "text-amber-700" : "",
          !statusTone ? "text-slate-700" : "",
        ].join(" ")}
      >
        {status}
      </p>

      {result && (
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full border border-line bg-slate-50 px-3 py-1 font-mono text-xs text-slate-800">
              status: {result.status}
            </span>
            <span className="rounded-full border border-line bg-slate-50 px-3 py-1 font-mono text-xs text-slate-800">
              diff ratio: {result.summary.diff_ratio}
            </span>
            <span className="rounded-full border border-line bg-slate-50 px-3 py-1 font-mono text-xs text-slate-800">
              threshold: {result.summary.threshold}
            </span>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Baseline Bytes</p>
              <p className="font-mono text-sm text-ink">{result.summary.baseline_bytes}</p>
            </div>
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Current Bytes</p>
              <p className="font-mono text-sm text-ink">{result.summary.current_bytes}</p>
            </div>
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Changed Bytes</p>
              <p className="font-mono text-sm text-ink">{result.summary.changed_bytes}</p>
            </div>
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Evaluated At</p>
              <p className="font-mono text-sm text-ink">{result.evaluated_at}</p>
            </div>
          </div>

          <div className="rounded-lg border border-line bg-slate-50 p-3">
            <p className="text-xs uppercase tracking-wide text-slate-600">Artifacts</p>
            <ul className="mt-2 space-y-1 text-xs font-mono text-slate-800">
              <li>baseline: {result.artifacts.baseline_ref}</li>
              <li>current: {result.artifacts.current_ref}</li>
              <li>diff: {result.artifacts.diff_ref}</li>
            </ul>
          </div>
        </div>
      )}
    </section>
  );
}
