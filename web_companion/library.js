export const SCHEMA = "pdftopdfocr-job-v1";

function outputNameFor(inputName) {
  const dot = inputName.lastIndexOf(".");
  if (dot <= 0) {
    return `${inputName}_ocred.pdf`;
  }
  return `${inputName.slice(0, dot)}_ocred.pdf`;
}

function manifestKeyFromFile(file) {
  return file.local_path || file.name || "";
}

export function parseJobManifest(json) {
  if (json.schema !== SCHEMA) {
    throw new Error(`Unbekanntes Schema: ${json.schema}`);
  }

  return {
    schema: SCHEMA,
    app: json.app || "PDFtoPDFocr",
    app_version: json.app_version || "",
    created_at: json.created_at || "",
    ocr_language: json.ocr_language || "deu",
    input_files: (json.input_files || []).map(file => ({
      name: file.name || "",
      local_path: file.local_path || file.name || "",
      size_bytes: file.size_bytes ?? null,
      missing: Boolean(file.missing)
    })),
    outputs: (json.outputs || []).map(output => ({
      input_name: output.input_name || "",
      input_local_path: output.input_local_path || "",
      output_name: output.output_name || outputNameFor(output.input_name || "job"),
      status: output.status || "pending",
      message: output.message || "",
      output_local_path: output.output_local_path || "",
      output_exists: Boolean(output.output_exists)
    })),
    settings: {
      dpi: json.settings?.dpi ?? 300,
      preserve_original: json.settings?.preserve_original ?? true,
      download_missing_language_pack: json.settings?.download_missing_language_pack ?? true
    }
  };
}

export function flattenEntries(job) {
  const outputsByPath = new Map();
  const fallbackOutputsByName = new Map();

  for (const output of job.outputs) {
    if (output.input_local_path) {
      outputsByPath.set(output.input_local_path, output);
      continue;
    }
    const bucket = fallbackOutputsByName.get(output.input_name) || [];
    bucket.push(output);
    fallbackOutputsByName.set(output.input_name, bucket);
  }

  return job.input_files.map(file => {
    const output =
      outputsByPath.get(manifestKeyFromFile(file)) ||
      fallbackOutputsByName.get(file.name)?.shift() ||
      {
        input_name: file.name,
        input_local_path: file.local_path || "",
        output_name: outputNameFor(file.name),
        status: "pending",
        message: "",
        output_local_path: "",
        output_exists: false
      };
    return {
      ...file,
      output
    };
  });
}

export function filterEntries(job, { query = "", status = "all", showMissing = true } = {}) {
  const q = query.trim().toLowerCase();
  return flattenEntries(job)
    .filter(entry => showMissing || !entry.missing)
    .filter(entry => status === "all" || entry.output.status === status)
    .filter(entry => {
      if (!q) {
        return true;
      }
      const haystack = [
        entry.name,
        entry.local_path,
        entry.output.output_name,
        entry.output.output_local_path,
        entry.output.message
      ].join(" ").toLowerCase();
      return haystack.includes(q);
    });
}

export function summarizeJob(job) {
  const entries = flattenEntries(job);
  return {
    total: entries.length,
    missing: entries.filter(entry => entry.missing).length,
    success: entries.filter(entry => entry.output.status === "success").length,
    failed: entries.filter(entry => entry.output.status === "failed").length,
    pending: entries.filter(entry => entry.output.status === "pending").length
  };
}

export function buildBrowserDraft(files, ocrLanguage = "deu", createdAt = new Date().toISOString()) {
  const inputFiles = files.map(file => ({
    name: file.name,
    local_path: file.name,
    size_bytes: file.size ?? null,
    missing: false
  }));

  const outputs = files.map(file => ({
    input_name: file.name,
    output_name: outputNameFor(file.name),
    status: "pending",
    message: "Browser-Entwurf: Desktop-App muss OCR und PDF-Erzeugung übernehmen.",
    output_local_path: outputNameFor(file.name),
    output_exists: false
  }));

  return parseJobManifest({
    schema: SCHEMA,
    app: "PDFtoPDFocr Browser Companion",
    app_version: "prototype",
    created_at: createdAt,
    ocr_language: ocrLanguage,
    input_files: inputFiles,
    outputs,
    settings: {
      dpi: 300,
      preserve_original: true,
      download_missing_language_pack: false
    }
  });
}

export function buildDemoManifest() {
  return parseJobManifest({
    schema: SCHEMA,
    app: "PDFtoPDFocr",
    app_version: "1.0.4",
    created_at: "2026-06-02T08:00:00Z",
    ocr_language: "deu",
    input_files: [
      {
        name: "rechnung-scan.pdf",
        local_path: "C:/Demo/rechnung-scan.pdf",
        size_bytes: 185420,
        missing: false
      },
      {
        name: "brief-ausgang.pdf",
        local_path: "C:/Demo/brief-ausgang.pdf",
        size_bytes: 90840,
        missing: false
      },
      {
        name: "fehlend.pdf",
        local_path: "D:/Archiv/fehlend.pdf",
        size_bytes: null,
        missing: true
      }
    ],
    outputs: [
      {
        input_name: "rechnung-scan.pdf",
        output_name: "rechnung-scan_ocred.pdf",
        status: "success",
        message: "OCR abgeschlossen, Ergebnis lokal vorhanden.",
        output_local_path: "C:/Demo/rechnung-scan_ocred.pdf",
        output_exists: true
      },
      {
        input_name: "brief-ausgang.pdf",
        output_name: "brief-ausgang_ocred.pdf",
        status: "pending",
        message: "Für mobile Vorprüfung eingeplant.",
        output_local_path: "C:/Demo/brief-ausgang_ocred.pdf",
        output_exists: false
      },
      {
        input_name: "fehlend.pdf",
        output_name: "fehlend_ocred.pdf",
        status: "failed",
        message: "Quelldatei ist auf diesem Gerät nicht verfügbar.",
        output_local_path: "D:/Archiv/fehlend_ocred.pdf",
        output_exists: false
      }
    ],
    settings: {
      dpi: 300,
      preserve_original: true,
      download_missing_language_pack: true
    }
  });
}
