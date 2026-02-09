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
  provSourceId: document.getElementById("provSourceId"),
  provVersionId: document.getElementById("provVersionId"),
  provImportedAt: document.getElementById("provImportedAt"),
  provTokenSource: document.getElementById("provTokenSource"),
  errorList: document.getElementById("errorList"),
  warningList: document.getElementById("warningList"),
  counts: document.getElementById("counts"),
  tokenRows: document.getElementById("tokenRows"),
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
        add(
          "typography",
          "typography.body.base.fontSize",
          "body.base.fontSize",
          "dimension",
          payload.uiTokens.fontSize,
        );
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
    throw new Error(body?.message || `Import failed with status ${response.status}`);
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

async function onImportClick() {
  const sourceId = el.sourceId.value.trim();
  if (!sourceId) {
    setStatus("Source ID is required.", "error");
    return;
  }

  setStatus("Importing tokens...");

  let payload;
  try {
    payload = await readJsonFromUI();
  } catch (err) {
    setStatus(`Invalid JSON: ${err.message}`, "error");
    return;
  }

  try {
    const result = await importWithApi(sourceId, payload);
    renderResult(result);
    if (result.validation?.valid) {
      setStatus("Import succeeded using live API.");
    } else {
      setStatus("Import completed with validation errors.", "warn");
    }
    return;
  } catch (err) {
    if (!el.useMockFallback.checked) {
      setStatus(`API error: ${err.message}`, "error");
      return;
    }
  }

  const mockResult = mockImport(sourceId, payload);
  renderResult(mockResult);
  if (mockResult.validation.valid) {
    setStatus("API unavailable. Import simulated with local mock adapter.", "warn");
  } else {
    setStatus("API unavailable. Mock import produced validation issues.", "warn");
  }
}

el.importBtn.addEventListener("click", onImportClick);
el.resetBtn.addEventListener("click", () => {
  el.payload.value = JSON.stringify(defaultPayload, null, 2);
  el.fileInput.value = "";
  setStatus("Default payload loaded.");
});
