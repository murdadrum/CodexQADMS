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

const state = {
  violations: [],
};

const el = {
  sourceId: document.getElementById("sourceId"),
  apiBase: document.getElementById("apiBase"),
  useMockFallback: document.getElementById("useMockFallback"),
  fileInput: document.getElementById("fileInput"),
  payload: document.getElementById("payload"),
  importBtn: document.getElementById("importBtn"),
  resetBtn: document.getElementById("resetBtn"),
  status: document.getElementById("status"),

  provenancePanel: document.getElementById("provenancePanel"),
  validationPanel: document.getElementById("validationPanel"),
  tokensPanel: document.getElementById("tokensPanel"),
  violationsPanel: document.getElementById("violationsPanel"),

  provSourceId: document.getElementById("provSourceId"),
  provVersionId: document.getElementById("provVersionId"),
  provImportedAt: document.getElementById("provImportedAt"),
  provTokenSource: document.getElementById("provTokenSource"),

  errorList: document.getElementById("errorList"),
  warningList: document.getElementById("warningList"),
  counts: document.getElementById("counts"),
  tokenRows: document.getElementById("tokenRows"),

  violationSummary: document.getElementById("violationSummary"),
  violationMeta: document.getElementById("violationMeta"),
  filterSeverity: document.getElementById("filterSeverity"),
  filterCategory: document.getElementById("filterCategory"),
  filterRule: document.getElementById("filterRule"),
  filterSearch: document.getElementById("filterSearch"),
  violationRows: document.getElementById("violationRows"),
  violationDetailPanel: document.getElementById("violationDetailPanel"),
  violationDetailTitle: document.getElementById("violationDetailTitle"),
  detailRule: document.getElementById("detailRule"),
  detailCode: document.getElementById("detailCode"),
  detailSeverity: document.getElementById("detailSeverity"),
  detailCategory: document.getElementById("detailCategory"),
  detailEvidence: document.getElementById("detailEvidence"),
  detailFix: document.getElementById("detailFix"),
};

el.payload.value = JSON.stringify(defaultPayload, null, 2);

function setStatus(message, tone = "") {
  el.status.classList.remove("error", "warn");
  if (tone) {
    el.status.classList.add(tone);
  }
  el.status.textContent = message;
}

function slugify(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, ".").replace(/^\.+|\.+$/g, "") || "unnamed";
}

function getApiErrorMessage(body, status) {
  if (body?.error?.message) {
    return `${body.error.message}${body.error.code ? ` (${body.error.code})` : ""}`;
  }
  if (body?.message) {
    return body.message;
  }
  return `Request failed with status ${status}`;
}

function readJsonFromUI() {
  if (el.fileInput.files && el.fileInput.files.length > 0) {
    return el.fileInput.files[0].text().then((text) => JSON.parse(text));
  }
  return Promise.resolve(JSON.parse(el.payload.value));
}

function mockImport(sourceId, payload) {
  const tokens = [];
  const errors = [];
  const warnings = [];

  const add = (group, path, name, token_type, value) => {
    tokens.push({ group, path, name, token_type, value, source: "figma_export" });
  };

  if (payload && typeof payload === "object") {
    if (Array.isArray(payload.colors)) {
      payload.colors.forEach((item, idx) => {
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

  const tokenCounts = tokens.reduce((acc, token) => {
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

function mockAudit(importResult) {
  const violations = [];
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

  const bySeverity = { low: 0, medium: 0, high: 0, critical: 0 };
  const byCategory = { tokens: 0, a11y: 0, other: 0 };
  const byRule = {};
  violations.forEach((v) => {
    bySeverity[v.severity] = (bySeverity[v.severity] || 0) + 1;
    byCategory[v.category] = (byCategory[v.category] || 0) + 1;
    byRule[v.rule_id] = (byRule[v.rule_id] || 0) + 1;
  });

  return {
    source_id: importResult.source_id,
    audit_id: `mock-audit-${Date.now()}`,
    evaluated_at: new Date().toISOString(),
    normalization: {
      valid: importResult.validation?.valid ?? false,
      error_count: (importResult.validation?.errors || []).length,
      warning_count: (importResult.validation?.warnings || []).length,
    },
    summary: {
      total_violations: violations.length,
      by_severity: bySeverity,
      by_category: byCategory,
      by_rule: byRule,
    },
    violations,
  };
}

async function importWithApi(sourceId, payload) {
  const base = el.apiBase.value.replace(/\/$/, "");
  const url = `${base}/api/v1/sources/${encodeURIComponent(sourceId)}/tokens/import/figma`;
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

async function auditWithApi(sourceId, payload) {
  const base = el.apiBase.value.replace(/\/$/, "");
  const url = `${base}/api/v1/sources/${encodeURIComponent(sourceId)}/audits/rules`;
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

function renderIssues(node, issues) {
  node.innerHTML = "";
  if (!issues || issues.length === 0) {
    const li = document.createElement("li");
    li.textContent = "None";
    node.appendChild(li);
    return;
  }
  issues.forEach((issue) => {
    const li = document.createElement("li");
    li.textContent = `${issue.path}: ${issue.message}`;
    node.appendChild(li);
  });
}

function renderCounts(counts) {
  el.counts.innerHTML = "";
  Object.entries(counts || {}).forEach(([key, value]) => {
    const chip = document.createElement("span");
    chip.textContent = `${key}: ${value}`;
    el.counts.appendChild(chip);
  });
}

function renderRows(tokens) {
  el.tokenRows.innerHTML = "";
  (tokens || []).slice(0, 25).forEach((token) => {
    const tr = document.createElement("tr");
    const path = document.createElement("td");
    const type = document.createElement("td");
    const value = document.createElement("td");
    path.textContent = token.path;
    type.textContent = token.token_type;
    value.textContent = typeof token.value === "object" ? JSON.stringify(token.value) : String(token.value);
    tr.append(path, type, value);
    el.tokenRows.appendChild(tr);
  });
}

function setSelectOptions(select, values) {
  const current = select.value;
  select.innerHTML = '<option value="all">All</option>';
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
  if ([...select.options].some((opt) => opt.value === current)) {
    select.value = current;
  }
}

function renderViolationRows(violations) {
  el.violationRows.innerHTML = "";
  if (!violations.length) {
    const tr = document.createElement("tr");
    const td = document.createElement("td");
    td.colSpan = 6;
    td.textContent = "No violations match current filters.";
    tr.appendChild(td);
    el.violationRows.appendChild(tr);
    return;
  }

  violations.forEach((violation) => {
    const tr = document.createElement("tr");
    const severity = document.createElement("td");
    const category = document.createElement("td");
    const rule = document.createElement("td");
    const code = document.createElement("td");
    const title = document.createElement("td");
    const evidence = document.createElement("td");

    severity.textContent = violation.severity;
    category.textContent = violation.category;
    rule.textContent = violation.rule_id;
    code.textContent = violation.code;
    title.textContent = violation.title;

    const evidenceBits = [];
    if (violation.evidence?.token_path) evidenceBits.push(`token: ${violation.evidence.token_path}`);
    if (violation.evidence?.text_path && violation.evidence?.bg_path) {
      evidenceBits.push(`pair: ${violation.evidence.text_path} vs ${violation.evidence.bg_path}`);
    }
    if (violation.evidence?.contrast_ratio !== undefined) {
      evidenceBits.push(`ratio: ${violation.evidence.contrast_ratio}`);
    }
    evidence.textContent = evidenceBits.join(" | ") || "-";

    tr.append(severity, category, rule, code, title, evidence);
    tr.addEventListener("click", () => renderViolationDetail(violation));
    el.violationRows.appendChild(tr);
  });
}

function applyViolationFilters() {
  const severity = el.filterSeverity.value;
  const category = el.filterCategory.value;
  const rule = el.filterRule.value;
  const search = el.filterSearch.value.trim().toLowerCase();

  const filtered = state.violations.filter((violation) => {
    if (severity !== "all" && violation.severity !== severity) return false;
    if (category !== "all" && violation.category !== category) return false;
    if (rule !== "all" && violation.rule_id !== rule) return false;
    if (search) {
      const haystack = [
        violation.title,
        violation.code,
        violation.rule_id,
        violation.category,
        violation.evidence?.token_path,
        violation.evidence?.text_path,
        violation.evidence?.bg_path,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      if (!haystack.includes(search)) return false;
    }
    return true;
  });

  el.violationMeta.textContent = `Showing ${filtered.length} of ${state.violations.length} violations.`;
  renderViolationRows(filtered);
}

function renderViolations(audit) {
  el.violationsPanel.hidden = false;
  state.violations = audit.violations || [];

  el.violationSummary.innerHTML = "";
  const summary = audit.summary || {};
  const chips = [
    `total: ${summary.total_violations ?? 0}`,
    `low: ${summary.by_severity?.low ?? 0}`,
    `medium: ${summary.by_severity?.medium ?? 0}`,
    `high: ${summary.by_severity?.high ?? 0}`,
    `critical: ${summary.by_severity?.critical ?? 0}`,
  ];
  chips.forEach((text) => {
    const chip = document.createElement("span");
    chip.textContent = text;
    el.violationSummary.appendChild(chip);
  });

  setSelectOptions(
    el.filterSeverity,
    [...new Set(state.violations.map((violation) => violation.severity))].sort(),
  );
  setSelectOptions(
    el.filterCategory,
    [...new Set(state.violations.map((violation) => violation.category))].sort(),
  );
  setSelectOptions(
    el.filterRule,
    [...new Set(state.violations.map((violation) => violation.rule_id))].sort(),
  );

  applyViolationFilters();
}

function renderResult(result) {
  el.provenancePanel.hidden = false;
  el.validationPanel.hidden = false;
  el.tokensPanel.hidden = false;

  el.provSourceId.textContent = result.source_id || "-";
  el.provVersionId.textContent = result.version_id || "-";
  el.provImportedAt.textContent = result.imported_at || "-";
  el.provTokenSource.textContent = result.token_version?.source || "-";

  renderIssues(el.errorList, result.validation?.errors || []);
  renderIssues(el.warningList, result.validation?.warnings || []);
  renderCounts(result.token_version?.token_counts || {});
  renderRows(result.token_version?.tokens || []);
}

function renderViolationDetail(violation) {
  state.selectedViolation = violation;
  el.violationDetailPanel.hidden = false;

  el.violationDetailTitle.textContent = violation.title || "Violation";
  el.detailRule.textContent = violation.rule_id || "-";
  el.detailCode.textContent = violation.code || "-";
  el.detailSeverity.textContent = violation.severity || "-";
  el.detailCategory.textContent = violation.category || "-";
  el.detailEvidence.textContent = JSON.stringify(violation.evidence || {}, null, 2);
  el.detailFix.textContent = JSON.stringify(violation.fix_hint || {}, null, 2);
}

async function onImportClick() {
  const sourceId = el.sourceId.value.trim();
  if (!sourceId) {
    setStatus("Source ID is required.", "error");
    return;
  }

  setStatus("Importing tokens and running rule audit...");

  let payload;
  try {
    payload = await readJsonFromUI();
  } catch (err) {
    setStatus(`Invalid JSON: ${err.message}`, "error");
    return;
  }

  try {
    const importResult = await importWithApi(sourceId, payload);
    renderResult(importResult);

    try {
      const auditResult = await auditWithApi(sourceId, payload);
      renderViolations(auditResult);
      if (importResult.validation?.valid) {
        setStatus("Import and rule audit succeeded using live API.");
      } else {
        setStatus("Import completed with validation errors; rule audit generated violations.", "warn");
      }
      return;
    } catch (auditErr) {
      if (!el.useMockFallback.checked) {
        setStatus(`Rule audit API error: ${auditErr.message}`, "error");
        return;
      }
      const mockAuditResult = mockAudit(importResult);
      renderViolations(mockAuditResult);
      setStatus("Rule audit API unavailable. Showing mock violations from imported tokens.", "warn");
      return;
    }
  } catch (err) {
    if (!el.useMockFallback.checked) {
      setStatus(`API error: ${err.message}`, "error");
      return;
    }
  }

  const mockResult = mockImport(sourceId, payload);
  renderResult(mockResult);
  const mockAuditResult = mockAudit(mockResult);
  renderViolations(mockAuditResult);
  if (mockResult.validation.valid) {
    setStatus("API unavailable. Import and audit simulated locally.", "warn");
  } else {
    setStatus("API unavailable. Local simulation produced validation issues.", "warn");
  }
}

el.importBtn.addEventListener("click", onImportClick);
el.resetBtn.addEventListener("click", () => {
  el.payload.value = JSON.stringify(defaultPayload, null, 2);
  el.fileInput.value = "";
  el.filterSeverity.value = "all";
  el.filterCategory.value = "all";
  el.filterRule.value = "all";
  el.filterSearch.value = "";
  el.violationDetailPanel.hidden = true;
  el.violationRows.innerHTML = "";
  el.violationSummary.innerHTML = "";
  setStatus("Default payload loaded.");
});

el.filterSeverity.addEventListener("change", applyViolationFilters);
el.filterCategory.addEventListener("change", applyViolationFilters);
el.filterRule.addEventListener("change", applyViolationFilters);
el.filterSearch.addEventListener("input", applyViolationFilters);
