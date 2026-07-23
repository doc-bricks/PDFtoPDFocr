import {
  buildBrowserDraft,
  buildDemoManifest,
  filterEntries,
  parseJobManifest,
  summarizeJob
} from "./library.js";

const STORAGE_KEY = "pdftopdfocr-web-companion-state";

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

const state = {
  job: null,
  sourceLabel: "Noch kein Manifest geladen."
};

const elements = {
  manifestInput: document.querySelector("#manifest-input"),
  demoButton: document.querySelector("#demo-button"),
  exportButton: document.querySelector("#export-button"),
  languageSelect: document.querySelector("#language-select"),
  draftFiles: document.querySelector("#draft-files"),
  draftButton: document.querySelector("#draft-button"),
  searchInput: document.querySelector("#search-input"),
  statusFilter: document.querySelector("#status-filter"),
  missingToggle: document.querySelector("#missing-toggle"),
  statusLine: document.querySelector("#status-line"),
  stats: document.querySelector("#stats"),
  resultsMeta: document.querySelector("#results-meta"),
  results: document.querySelector("#results")
};

function persistState() {
  if (!state.job) {
    localStorage.removeItem(STORAGE_KEY);
    return;
  }
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      job: state.job,
      sourceLabel: state.sourceLabel
    }));
  } catch { /* QuotaExceededError in Safari Private Browsing */ }
}

function restoreState() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return;
  }
  try {
    const saved = JSON.parse(raw);
    state.job = saved.job ? parseJobManifest(saved.job) : null;
    state.sourceLabel = saved.sourceLabel || state.sourceLabel;
  } catch {
    localStorage.removeItem(STORAGE_KEY);
  }
}

function loadJob(job, sourceLabel) {
  state.job = job;
  state.sourceLabel = sourceLabel;
  persistState();
  render();
}

function formatBytes(value) {
  if (value == null) {
    return "unbekannt";
  }
  if (value < 1024) {
    return `${value} B`;
  }
  if (value < 1024 * 1024) {
    return `${(value / 1024).toFixed(1)} KB`;
  }
  return `${(value / (1024 * 1024)).toFixed(2)} MB`;
}

function buildStatCards(job) {
  const summary = summarizeJob(job);
  const cards = [
    ["Eingaben", summary.total],
    ["Ausstehend", summary.pending],
    ["Erfolgreich", summary.success],
    ["Fehlend", summary.missing],
    ["Sprache", job.ocr_language]
  ];
  return cards.map(([label, value]) => `
    <div class="stat-card">
      <span class="stat-label">${escHtml(label)}</span>
      <span class="stat-value">${escHtml(value)}</span>
    </div>
  `).join("");
}

function renderResults(job) {
  const entries = filterEntries(job, {
    query: elements.searchInput.value,
    status: elements.statusFilter.value,
    showMissing: elements.missingToggle.checked
  });

  elements.resultsMeta.textContent = `${entries.length} Einträge sichtbar.`;
  if (!entries.length) {
    elements.results.innerHTML = `
      <div class="empty">
        Keine Einträge für diesen Filter. Probieren Sie einen anderen Status
        oder laden Sie die Demo.
      </div>
    `;
    return;
  }

  elements.results.innerHTML = entries.map(entry => `
    <article class="result-card">
      <div class="result-top">
        <div>
          <h3 class="result-title">${escHtml(entry.name)}</h3>
          <p class="result-path">${escHtml(entry.local_path)}</p>
        </div>
        <span class="badge ${escHtml(entry.output.status)}">${escHtml(entry.output.status)}</span>
      </div>
      <div class="meta-grid">
        <div><span>Größe:</span> ${escHtml(formatBytes(entry.size_bytes))}</div>
        <div><span>Ausgabe:</span> ${escHtml(entry.output.output_name)}</div>
        <div><span>Ausgabepfad:</span> ${escHtml(entry.output.output_local_path || "noch offen")}</div>
        <div><span>Ergebnis vorhanden:</span> ${entry.output.output_exists ? "ja" : "nein"}</div>
        <div><span>Quelle fehlt:</span> ${entry.missing ? "ja" : "nein"}</div>
        <div><span>Meldung:</span> ${escHtml(entry.output.message || "keine")}</div>
      </div>
    </article>
  `).join("");
}

function render() {
  if (!state.job) {
    elements.statusLine.textContent = "Noch kein Manifest geladen.";
    elements.stats.innerHTML = "";
    elements.resultsMeta.textContent = "0 Einträge sichtbar.";
    elements.results.innerHTML = `
      <div class="empty">
        Importieren Sie ein \`pdftopdfocr-job-v1.json\` oder bauen Sie einen
        Browser-Entwurf für die mobile Vorprüfung.
      </div>
    `;
    return;
  }

  elements.statusLine.textContent = `${state.sourceLabel} • ${state.job.created_at || "ohne Zeitstempel"}`;
  elements.stats.innerHTML = buildStatCards(state.job);
  renderResults(state.job);
}

async function handleManifestFile(file) {
  const text = await file.text();
  const parsed = parseJobManifest(JSON.parse(text));
  loadJob(parsed, `Manifest importiert: ${file.name}`);
}

function exportCurrentState() {
  if (!state.job) {
    return;
  }
  const blob = new Blob([JSON.stringify(state.job, null, 2) + "\n"], {
    type: "application/json"
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "pdftopdfocr-job-v1.browser.json";
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

function installServiceWorker() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("./sw.js").catch(() => {});
  }
}

elements.manifestInput.addEventListener("change", event => {
  const [file] = event.target.files || [];
  if (file) {
    handleManifestFile(file).catch(error => {
      elements.statusLine.textContent = `Manifest konnte nicht geladen werden: ${error.message}`;
    });
  }
});

elements.demoButton.addEventListener("click", () => {
  loadJob(buildDemoManifest(), "Demo-Manifest geladen");
});

elements.exportButton.addEventListener("click", exportCurrentState);

elements.draftButton.addEventListener("click", () => {
  const files = [...(elements.draftFiles.files || [])];
  if (!files.length) {
    elements.statusLine.textContent = "Für den Browser-Entwurf wurden noch keine Dateien gewählt.";
    return;
  }
  loadJob(
    buildBrowserDraft(files, elements.languageSelect.value),
    `Browser-Entwurf aus ${files.length} Datei(en)`
  );
});

[elements.searchInput, elements.statusFilter, elements.missingToggle].forEach(element =>
  element.addEventListener("input", render)
);

restoreState();
if (new URLSearchParams(window.location.search).get("demo") === "1" && !state.job) {
  state.job = buildDemoManifest();
  state.sourceLabel = "Demo-Manifest über URL geladen";
}
render();
installServiceWorker();
