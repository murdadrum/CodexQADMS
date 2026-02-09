"use client";

import { useMemo, useState } from "react";

type ValidationIssue = {
  path: string;
  message: string;
};

type CanonicalToken = {
  group: string;
  path: string;
  name: string;
  token_type: string;
  value: unknown;
  source?: string;
};

type ImportResult = {
  source_id: string;
  version_id: string;
  imported_at: string;
  token_version: {
    source: string;
    tokens: CanonicalToken[];
    token_counts: Record<string, number>;
  };
  validation: {
    valid: boolean;
    errors: ValidationIssue[];
    warnings: ValidationIssue[];
  };
};

type Violation = {
  violation_id?: string;
  rule_id: string;
  category: string;
  severity: string;
  code: string;
  title: string;
  description?: string;
  evidence?: Record<string, unknown>;
  fix_hint?: Record<string, unknown>;
};

type AuditResult = {
  source_id: string;
  audit_id: string;
  evaluated_at: string;
  summary: {
    total_violations: number;
    by_severity: Record<string, number>;
    by_category: Record<string, number>;
    by_rule: Record<string, number>;
  };
  violations: Violation[];
};

const defaultPayload = {
  colors: [
    { name: "Primary", variable: "--primary", hsl: "hsl(160, 65%, 35%)", hex: "#1f936d" },
    { name: "Secondary", variable: "--secondary", hsl: "hsl(85, 55%, 92%)", hex: "#ecf6df" },
    { name: "Accent", variable: "--accent", hsl: "hsl(350, 70%, 90%)", hex: "#f7d4da" },
  ],
  uiTokens: {
    radius: 12,
    fontSize: 16,
  },
};

function slugify(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, ".").replace(/^\.+|\.+$/g, "") || "unnamed";
}

function getApiErrorMessage(body: any, status: number) {
  if (body?.error?.message) {
    return `${body.error.message}${body.error.code ? ` (${body.error.code})` : ""}`;
  }
  if (body?.message) {
    return body.message;
  }
  return `Request failed with status ${status}`;
}

function mockImport(sourceId: string, payload: any): ImportResult {
  const tokens: CanonicalToken[] = [];
  const errors: ValidationIssue[] = [];
  const warnings: ValidationIssue[] = [];

  const add = (group: string, path: string, name: string, tokenType: string, value: unknown) => {
    tokens.push({ group, path, name, token_type: tokenType, value, source: "figma_export" });
  };

  if (payload && typeof payload === "object") {
    if (Array.isArray(payload.colors)) {
      payload.colors.forEach((item: any, idx: number) => {
        if (!item || typeof item !== "object") {
          errors.push({ path: `colors[${idx}]`, message: "Each color entry must be an object." });
          return;
        }
        const rawName = item.name || item.variable || `color_${idx}`;
        const name = slugify(String(rawName).replace(/^--/, ""));
        const value = item.hex ?? item.hsl;
        if (value === undefined) {
          errors.push({ path: `colors[${idx}]`, message: "Color entry must include `hex` or `hsl`." });
          return;
        }
        add("color", `color.${name}`, name, "color", value);
      });
    }

    if (payload.uiTokens && typeof payload.uiTokens === "object") {
      if (payload.uiTokens.radius !== undefined) {
        add("radius", "radius.base", "base", "dimension", payload.uiTokens.radius);
      }
      if (payload.uiTokens.fontSize !== undefined) {
        add("typography", "typography.body.base.fontSize", "body.base.fontSize", "dimension", payload.uiTokens.fontSize);
      }
    }

    const known = ["colors", "uiTokens", "color", "spacing", "typography", "radius", "shadow"];
    Object.keys(payload).forEach((key) => {
      if (!known.includes(key)) {
        warnings.push({ path: key, message: "Unknown top-level group ignored by canonical mapping." });
      }
    });
  } else {
    errors.push({ path: "$", message: "Payload must be a JSON object." });
  }

  const tokenCounts = tokens.reduce<Record<string, number>>((acc, token) => {
    acc[token.group] = (acc[token.group] || 0) + 1;
    return acc;
  }, {});

  return {
    source_id: sourceId,
    version_id: `mock-${Date.now()}`,
    imported_at: new Date().toISOString(),
    token_version: {
      source: "figma_export",
      tokens,
      token_counts: tokenCounts,
    },
    validation: {
      valid: errors.length === 0,
      errors,
      warnings,
    },
  };
}

function mockAudit(importResult: ImportResult): AuditResult {
  const violations: Violation[] = [];

  (importResult.token_version?.tokens || []).forEach((token, idx) => {
    if (/[A-Z ]/.test(token.path || "") || /[A-Z ]/.test(token.name || "")) {
      violations.push({
        violation_id: `MOCK_NAMING:${idx + 1}`,
        rule_id: "TOKENS_NAMING",
        category: "tokens",
        severity: "medium",
        code: "PATH_FORMAT",
        title: "Token naming format issue",
        description: "Token path/name should be lowercase dot-safe values.",
        evidence: { token_path: token.path, token_name: token.name },
        fix_hint: { action: "rename_token" },
      });
    }
  });

  const bySeverity: Record<string, number> = { low: 0, medium: 0, high: 0, critical: 0 };
  const byCategory: Record<string, number> = { tokens: 0, a11y: 0, other: 0 };
  const byRule: Record<string, number> = {};
  violations.forEach((violation) => {
    bySeverity[violation.severity] = (bySeverity[violation.severity] || 0) + 1;
    byCategory[violation.category] = (byCategory[violation.category] || 0) + 1;
    byRule[violation.rule_id] = (byRule[violation.rule_id] || 0) + 1;
  });

  return {
    source_id: importResult.source_id,
    audit_id: `mock-audit-${Date.now()}`,
    evaluated_at: new Date().toISOString(),
    summary: {
      total_violations: violations.length,
      by_severity: bySeverity,
      by_category: byCategory,
      by_rule: byRule,
    },
    violations,
  };
}

export function ConsolePanel() {
  const [sourceId, setSourceId] = useState("source-theme");
  const [apiBase, setApiBase] = useState("http://127.0.0.1:8000");
  const [useMockFallback, setUseMockFallback] = useState(true);
  const [payloadText, setPayloadText] = useState(JSON.stringify(defaultPayload, null, 2));
  const [fileJson, setFileJson] = useState<string | null>(null);
  const [status, setStatus] = useState("Ready.");
  const [statusTone, setStatusTone] = useState<"" | "error" | "warn">("");
  const [importResult, setImportResult] = useState<ImportResult | null>(null);
  const [auditResult, setAuditResult] = useState<AuditResult | null>(null);
  const [selectedViolation, setSelectedViolation] = useState<Violation | null>(null);
  const [filterSeverity, setFilterSeverity] = useState("all");
  const [filterCategory, setFilterCategory] = useState("all");
  const [filterRule, setFilterRule] = useState("all");
  const [filterSearch, setFilterSearch] = useState("");

  const violations = auditResult?.violations ?? [];

  const filteredViolations = useMemo(() => {
    const search = filterSearch.trim().toLowerCase();
    return violations.filter((violation) => {
      if (filterSeverity !== "all" && violation.severity !== filterSeverity) return false;
      if (filterCategory !== "all" && violation.category !== filterCategory) return false;
      if (filterRule !== "all" && violation.rule_id !== filterRule) return false;
      if (!search) return true;
      const evidence = violation.evidence || {};
      const haystack = [
        violation.title,
        violation.code,
        violation.rule_id,
        violation.category,
        String(evidence.token_path || ""),
        String(evidence.text_path || ""),
        String(evidence.bg_path || ""),
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(search);
    });
  }, [violations, filterSeverity, filterCategory, filterRule, filterSearch]);

  const severityOptions = useMemo(
    () => [...new Set(violations.map((violation) => violation.severity))].sort(),
    [violations],
  );
  const categoryOptions = useMemo(
    () => [...new Set(violations.map((violation) => violation.category))].sort(),
    [violations],
  );
  const ruleOptions = useMemo(() => [...new Set(violations.map((violation) => violation.rule_id))].sort(), [violations]);

  async function readPayload() {
    if (fileJson) {
      return JSON.parse(fileJson);
    }
    return JSON.parse(payloadText);
  }

  async function importWithApi(nextSourceId: string, payload: unknown): Promise<ImportResult> {
    const base = apiBase.replace(/\/$/, "");
    const url = `${base}/api/v1/sources/${encodeURIComponent(nextSourceId)}/tokens/import/figma`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    if (!response.ok && response.status !== 422) {
      throw new Error(getApiErrorMessage(body, response.status));
    }
    return body;
  }

  async function auditWithApi(nextSourceId: string, payload: unknown): Promise<AuditResult> {
    const base = apiBase.replace(/\/$/, "");
    const url = `${base}/api/v1/sources/${encodeURIComponent(nextSourceId)}/audits/rules`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await response.json();
    if (!response.ok) {
      throw new Error(getApiErrorMessage(body, response.status));
    }
    return body;
  }

  async function onImport() {
    const nextSourceId = sourceId.trim();
    if (!nextSourceId) {
      setStatusTone("error");
      setStatus("Source ID is required.");
      return;
    }

    setStatusTone("");
    setStatus("Importing tokens and running rule audit...");

    let payload: unknown;
    try {
      payload = await readPayload();
    } catch (error: any) {
      setStatusTone("error");
      setStatus(`Invalid JSON: ${error?.message || "Failed to parse JSON"}`);
      return;
    }

    try {
      const imported = await importWithApi(nextSourceId, payload);
      setImportResult(imported);

      try {
        const audited = await auditWithApi(nextSourceId, payload);
        setAuditResult(audited);
        setSelectedViolation(null);
        if (imported.validation?.valid) {
          setStatusTone("");
          setStatus("Import and rule audit succeeded using live API.");
        } else {
          setStatusTone("warn");
          setStatus("Import completed with validation errors; rule audit generated violations.");
        }
        return;
      } catch (auditError: any) {
        if (!useMockFallback) {
          setStatusTone("error");
          setStatus(`Rule audit API error: ${auditError?.message || "Unknown error"}`);
          return;
        }
        const mockAudited = mockAudit(imported);
        setAuditResult(mockAudited);
        setSelectedViolation(null);
        setStatusTone("warn");
        setStatus("Rule audit API unavailable. Showing mock violations from imported tokens.");
        return;
      }
    } catch (importError: any) {
      if (!useMockFallback) {
        setStatusTone("error");
        setStatus(`API error: ${importError?.message || "Unknown error"}`);
        return;
      }
    }

    const localImported = mockImport(nextSourceId, payload);
    const localAudited = mockAudit(localImported);
    setImportResult(localImported);
    setAuditResult(localAudited);
    setSelectedViolation(null);
    setStatusTone("warn");
    if (localImported.validation.valid) {
      setStatus("API unavailable. Import and audit simulated locally.");
    } else {
      setStatus("API unavailable. Local simulation produced validation issues.");
    }
  }

  function onReset() {
    setPayloadText(JSON.stringify(defaultPayload, null, 2));
    setFileJson(null);
    setFilterSeverity("all");
    setFilterCategory("all");
    setFilterRule("all");
    setFilterSearch("");
    setSelectedViolation(null);
    setStatusTone("");
    setStatus("Default payload loaded.");
  }

  return (
    <div className="space-y-5">
      <section className="rounded-2xl border border-line/70 bg-white/90 p-6 shadow-lg space-y-4">
        <h2 className="text-xl font-semibold text-ink">Import Request</h2>
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
        </div>

        <label className="flex items-center gap-2 text-sm text-ink">
          <input
            type="checkbox"
            checked={useMockFallback}
            onChange={(event) => setUseMockFallback(event.target.checked)}
            className="h-4 w-4 accent-brand"
          />
          Use local mock importer if API is unavailable
        </label>

        <label className="grid gap-1 text-sm text-ink">
          Token JSON file (optional)
          <input
            type="file"
            accept=".json,application/json"
            onChange={async (event) => {
              const file = event.target.files?.[0];
              if (!file) {
                setFileJson(null);
                return;
              }
              const text = await file.text();
              setFileJson(text);
            }}
            className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
          />
        </label>

        <label className="grid gap-1 text-sm text-ink">
          JSON payload (used when no file is selected)
          <textarea
            value={payloadText}
            onChange={(event) => setPayloadText(event.target.value)}
            rows={12}
            className="rounded-lg border border-line bg-white px-3 py-2 font-mono text-xs"
          />
        </label>

        <div className="flex flex-wrap gap-2">
          <button onClick={onImport} className="rounded-lg bg-brand px-3 py-2 text-sm font-semibold text-white shadow-sm">
            Import Tokens
          </button>
          <button
            onClick={onReset}
            className="rounded-lg border border-line bg-brandSoft px-3 py-2 text-sm font-semibold text-ink shadow-sm"
          >
            Load Default Payload
          </button>
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
      </section>

      {importResult && (
        <section className="rounded-2xl border border-line/70 bg-white/90 p-6 shadow-lg space-y-4">
          <h2 className="text-xl font-semibold text-ink">Provenance</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Source ID</p>
              <p className="font-mono text-sm text-ink">{importResult.source_id || "-"}</p>
            </div>
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Version ID</p>
              <p className="font-mono text-sm text-ink">{importResult.version_id || "-"}</p>
            </div>
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Imported At</p>
              <p className="font-mono text-sm text-ink">{importResult.imported_at || "-"}</p>
            </div>
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Token Source</p>
              <p className="font-mono text-sm text-ink">{importResult.token_version?.source || "-"}</p>
            </div>
          </div>
        </section>
      )}

      {importResult && (
        <section className="rounded-2xl border border-line/70 bg-white/90 p-6 shadow-lg space-y-4">
          <h2 className="text-xl font-semibold text-ink">Validation</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <article>
              <h3 className="mb-2 text-base font-semibold text-ink">Errors</h3>
              <ul className="list-disc space-y-1 pl-5">
                {(importResult.validation?.errors || []).length === 0 ? (
                  <li className="font-mono text-xs text-slate-700">None</li>
                ) : (
                  importResult.validation.errors.map((issue, index) => (
                    <li key={`error-${index}`} className="font-mono text-xs text-slate-800">
                      {issue.path}: {issue.message}
                    </li>
                  ))
                )}
              </ul>
            </article>
            <article>
              <h3 className="mb-2 text-base font-semibold text-ink">Warnings</h3>
              <ul className="list-disc space-y-1 pl-5">
                {(importResult.validation?.warnings || []).length === 0 ? (
                  <li className="font-mono text-xs text-slate-700">None</li>
                ) : (
                  importResult.validation.warnings.map((issue, index) => (
                    <li key={`warning-${index}`} className="font-mono text-xs text-slate-800">
                      {issue.path}: {issue.message}
                    </li>
                  ))
                )}
              </ul>
            </article>
          </div>
        </section>
      )}

      {importResult && (
        <section className="rounded-2xl border border-line/70 bg-white/90 p-6 shadow-lg space-y-4">
          <h2 className="text-xl font-semibold text-ink">Token Summary</h2>
          <div className="flex flex-wrap gap-2">
            {Object.entries(importResult.token_version?.token_counts || {}).map(([key, value]) => (
              <span key={key} className="rounded-full border border-line bg-slate-50 px-3 py-1 font-mono text-xs text-slate-800">
                {key}: {value}
              </span>
            ))}
          </div>
          <div className="overflow-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr>
                  <th className="border-b border-line px-2 py-2 text-left text-xs uppercase tracking-wide text-slate-600">Path</th>
                  <th className="border-b border-line px-2 py-2 text-left text-xs uppercase tracking-wide text-slate-600">Type</th>
                  <th className="border-b border-line px-2 py-2 text-left text-xs uppercase tracking-wide text-slate-600">Value</th>
                </tr>
              </thead>
              <tbody>
                {(importResult.token_version?.tokens || []).slice(0, 25).map((token, index) => (
                  <tr key={`${token.path}-${index}`}>
                    <td className="border-b border-line px-2 py-2 font-mono text-xs text-slate-800">{token.path}</td>
                    <td className="border-b border-line px-2 py-2 font-mono text-xs text-slate-800">{token.token_type}</td>
                    <td className="border-b border-line px-2 py-2 font-mono text-xs text-slate-800">
                      {typeof token.value === "object" ? JSON.stringify(token.value) : String(token.value)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {auditResult && (
        <section className="rounded-2xl border border-line/70 bg-white/90 p-6 shadow-lg space-y-4">
          <h2 className="text-xl font-semibold text-ink">Violations</h2>
          <div className="flex flex-wrap gap-2">
            <span className="rounded-full border border-line bg-slate-50 px-3 py-1 font-mono text-xs text-slate-800">
              total: {auditResult.summary?.total_violations ?? 0}
            </span>
            <span className="rounded-full border border-line bg-slate-50 px-3 py-1 font-mono text-xs text-slate-800">
              low: {auditResult.summary?.by_severity?.low ?? 0}
            </span>
            <span className="rounded-full border border-line bg-slate-50 px-3 py-1 font-mono text-xs text-slate-800">
              medium: {auditResult.summary?.by_severity?.medium ?? 0}
            </span>
            <span className="rounded-full border border-line bg-slate-50 px-3 py-1 font-mono text-xs text-slate-800">
              high: {auditResult.summary?.by_severity?.high ?? 0}
            </span>
            <span className="rounded-full border border-line bg-slate-50 px-3 py-1 font-mono text-xs text-slate-800">
              critical: {auditResult.summary?.by_severity?.critical ?? 0}
            </span>
          </div>

          <div className="grid gap-3 md:grid-cols-4">
            <label className="grid gap-1 text-sm text-ink">
              Severity
              <select
                value={filterSeverity}
                onChange={(event) => setFilterSeverity(event.target.value)}
                className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
              >
                <option value="all">All</option>
                {severityOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-1 text-sm text-ink">
              Category
              <select
                value={filterCategory}
                onChange={(event) => setFilterCategory(event.target.value)}
                className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
              >
                <option value="all">All</option>
                {categoryOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-1 text-sm text-ink">
              Rule
              <select
                value={filterRule}
                onChange={(event) => setFilterRule(event.target.value)}
                className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
              >
                <option value="all">All</option>
                {ruleOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
            <label className="grid gap-1 text-sm text-ink">
              Search
              <input
                type="text"
                value={filterSearch}
                onChange={(event) => setFilterSearch(event.target.value)}
                placeholder="title, code, token path..."
                className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
              />
            </label>
          </div>

          <p className="text-sm text-slate-700">
            Showing {filteredViolations.length} of {violations.length} violations.
          </p>

          <div className="overflow-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr>
                  <th className="border-b border-line px-2 py-2 text-left text-xs uppercase tracking-wide text-slate-600">Severity</th>
                  <th className="border-b border-line px-2 py-2 text-left text-xs uppercase tracking-wide text-slate-600">Category</th>
                  <th className="border-b border-line px-2 py-2 text-left text-xs uppercase tracking-wide text-slate-600">Rule</th>
                  <th className="border-b border-line px-2 py-2 text-left text-xs uppercase tracking-wide text-slate-600">Code</th>
                  <th className="border-b border-line px-2 py-2 text-left text-xs uppercase tracking-wide text-slate-600">Title</th>
                  <th className="border-b border-line px-2 py-2 text-left text-xs uppercase tracking-wide text-slate-600">Evidence</th>
                </tr>
              </thead>
              <tbody>
                {filteredViolations.length === 0 && (
                  <tr>
                    <td className="border-b border-line px-2 py-3 text-sm text-slate-700" colSpan={6}>
                      No violations match current filters.
                    </td>
                  </tr>
                )}
                {filteredViolations.map((violation, index) => {
                  const evidence = violation.evidence || {};
                  const evidenceParts: string[] = [];
                  if (evidence.token_path) evidenceParts.push(`token: ${String(evidence.token_path)}`);
                  if (evidence.text_path && evidence.bg_path) {
                    evidenceParts.push(`pair: ${String(evidence.text_path)} vs ${String(evidence.bg_path)}`);
                  }
                  if (evidence.contrast_ratio !== undefined) {
                    evidenceParts.push(`ratio: ${String(evidence.contrast_ratio)}`);
                  }
                  return (
                    <tr
                      key={`${violation.rule_id}-${violation.code}-${index}`}
                      className="cursor-pointer hover:bg-slate-50"
                      onClick={() => setSelectedViolation(violation)}
                    >
                      <td className="border-b border-line px-2 py-2 font-mono text-xs text-slate-800">{violation.severity}</td>
                      <td className="border-b border-line px-2 py-2 font-mono text-xs text-slate-800">{violation.category}</td>
                      <td className="border-b border-line px-2 py-2 font-mono text-xs text-slate-800">{violation.rule_id}</td>
                      <td className="border-b border-line px-2 py-2 font-mono text-xs text-slate-800">{violation.code}</td>
                      <td className="border-b border-line px-2 py-2 text-xs text-slate-900">{violation.title}</td>
                      <td className="border-b border-line px-2 py-2 font-mono text-xs text-slate-700">
                        {evidenceParts.join(" | ") || "-"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {selectedViolation && (
        <section className="rounded-2xl border border-line/70 bg-white/90 p-6 shadow-lg space-y-4">
          <h2 className="text-xl font-semibold text-ink">Violation Detail</h2>
          <p className="text-sm font-semibold text-ink">{selectedViolation.title || "Violation"}</p>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Rule</p>
              <p className="font-mono text-sm text-ink">{selectedViolation.rule_id || "-"}</p>
            </div>
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Code</p>
              <p className="font-mono text-sm text-ink">{selectedViolation.code || "-"}</p>
            </div>
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Severity</p>
              <p className="font-mono text-sm text-ink">{selectedViolation.severity || "-"}</p>
            </div>
            <div className="rounded-lg border border-line bg-white px-3 py-2">
              <p className="text-xs uppercase tracking-wide text-slate-600">Category</p>
              <p className="font-mono text-sm text-ink">{selectedViolation.category || "-"}</p>
            </div>
          </div>
          <div>
            <h3 className="mb-1 text-sm font-semibold text-ink">Evidence</h3>
            <pre className="overflow-auto rounded-lg border border-line bg-slate-50 p-3 font-mono text-xs text-slate-800">
              {JSON.stringify(selectedViolation.evidence || {}, null, 2)}
            </pre>
          </div>
          <div>
            <h3 className="mb-1 text-sm font-semibold text-ink">Fix Hint</h3>
            <pre className="overflow-auto rounded-lg border border-line bg-slate-50 p-3 font-mono text-xs text-slate-800">
              {JSON.stringify(selectedViolation.fix_hint || {}, null, 2)}
            </pre>
          </div>
        </section>
      )}
    </div>
  );
}
