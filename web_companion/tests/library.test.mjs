import { test } from "node:test";
import assert from "node:assert/strict";
import {
  SCHEMA,
  buildBrowserDraft,
  buildDemoManifest,
  filterEntries,
  flattenEntries,
  parseJobManifest,
  summarizeJob
} from "../library.js";

const SAMPLE = {
  schema: SCHEMA,
  app: "PDFtoPDFocr",
  app_version: "1.0.4",
  created_at: "2026-06-02T08:00:00Z",
  ocr_language: "deu",
  input_files: [
    { name: "scan.pdf", local_path: "C:/scan.pdf", size_bytes: 1234, missing: false },
    { name: "lost.pdf", local_path: "D:/lost.pdf", size_bytes: null, missing: true }
  ],
  outputs: [
    {
      input_name: "scan.pdf",
      output_name: "scan_ocred.pdf",
      status: "success",
      message: "Fertig",
      output_local_path: "C:/scan_ocred.pdf",
      output_exists: true
    },
    {
      input_name: "lost.pdf",
      output_name: "lost_ocred.pdf",
      status: "failed",
      message: "Datei fehlt",
      output_local_path: "D:/lost_ocred.pdf",
      output_exists: false
    }
  ],
  settings: {
    dpi: 300,
    preserve_original: true,
    download_missing_language_pack: true
  }
};

test("parseJobManifest rejects unknown schema", () => {
  assert.throws(() => parseJobManifest({ schema: "other-v1" }), /Unbekanntes Schema/);
});

test("parseJobManifest normalizes inputs and settings", () => {
  const job = parseJobManifest(SAMPLE);
  assert.equal(job.input_files.length, 2);
  assert.equal(job.settings.dpi, 300);
  assert.equal(job.outputs[0].status, "success");
});

test("filterEntries filters by status and hides missing inputs when requested", () => {
  const job = parseJobManifest(SAMPLE);
  const successOnly = filterEntries(job, { status: "success", showMissing: false });
  assert.equal(successOnly.length, 1);
  assert.equal(successOnly[0].name, "scan.pdf");
});

test("filterEntries searches path and message content", () => {
  const job = parseJobManifest(SAMPLE);
  const found = filterEntries(job, { query: "datei fehlt" });
  assert.equal(found.length, 1);
  assert.equal(found[0].name, "lost.pdf");
});

test("summarizeJob counts success, failed, pending and missing states", () => {
  const job = parseJobManifest(SAMPLE);
  const summary = summarizeJob(job);
  assert.equal(summary.total, 2);
  assert.equal(summary.success, 1);
  assert.equal(summary.failed, 1);
  assert.equal(summary.pending, 0);
  assert.equal(summary.missing, 1);
});

test("buildBrowserDraft creates pending outputs for local browser files", () => {
  const job = buildBrowserDraft(
    [
      { name: "scan.pdf", size: 4000 },
      { name: "foto.jpg", size: 2000 }
    ],
    "eng",
    "2026-06-02T09:00:00Z"
  );

  assert.equal(job.ocr_language, "eng");
  assert.equal(job.input_files[0].local_path, "scan.pdf");
  assert.equal(job.outputs[1].output_name, "foto_ocred.pdf");
  assert.ok(job.outputs.every(output => output.status === "pending"));
});

test("flattenEntries keeps duplicate basenames separated via input_local_path", () => {
  const job = parseJobManifest({
    schema: SCHEMA,
    input_files: [
      { name: "scan.pdf", local_path: "A/scan.pdf", missing: false },
      { name: "scan.pdf", local_path: "B/scan.pdf", missing: false }
    ],
    outputs: [
      {
        input_name: "scan.pdf",
        input_local_path: "A/scan.pdf",
        output_name: "scan_ocred.pdf",
        status: "success",
        message: "A",
        output_local_path: "A/scan_ocred.pdf",
        output_exists: true
      },
      {
        input_name: "scan.pdf",
        input_local_path: "B/scan.pdf",
        output_name: "scan_ocred.pdf",
        status: "failed",
        message: "B",
        output_local_path: "B/scan_ocred.pdf",
        output_exists: false
      }
    ]
  });

  const entries = flattenEntries(job);
  assert.equal(entries[0].output.message, "A");
  assert.equal(entries[0].output.output_local_path, "A/scan_ocred.pdf");
  assert.equal(entries[1].output.message, "B");
  assert.equal(entries[1].output.output_local_path, "B/scan_ocred.pdf");
});

test("buildDemoManifest returns a parseable mixed-state example", () => {
  const job = buildDemoManifest();
  const summary = summarizeJob(job);
  assert.equal(summary.total, 3);
  assert.equal(summary.pending, 1);
  assert.equal(summary.success, 1);
  assert.equal(summary.failed, 1);
});
