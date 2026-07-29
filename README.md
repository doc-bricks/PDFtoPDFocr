[English](README.md) | [Deutsch](README_de.md)

# PDFtoPDFocr - PDF OCR Converter

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Pytest](https://img.shields.io/badge/pytest-47%20passed-brightgreen.svg)](tests/)
[![LLM-Ready](https://img.shields.io/badge/LLM--Ready-llms.txt-blueviolet.svg)](llms.txt)
[![Ecosystem](https://img.shields.io/badge/Ecosystem-doc--bricks-orange.svg)](https://github.com/doc-bricks)
[![Umbrella](https://img.shields.io/badge/Umbrella-open--bricks-blue.svg)](https://github.com/open-bricks)

Converts scanned PDF files into searchable PDFs using OCR (text recognition) with Tesseract. Batch processing, selectable OCR language, automatic language pack download, and portable Tesseract integration.

Machine-readable project context: [`llms.txt`](llms.txt) | [Deutsche Dokumentation](README_de.md)

> [!NOTE]
> **AI & LLM Integration:** This repository contains a structured [`llms.txt`](llms.txt) file providing machine-readable context, architectural details, CLI/GUI interfaces, and test entry points for autonomous agents.

> [!TIP]
> **Privacy & Local-First Processing:** PDF files are processed 100% locally on your machine. Documents are never uploaded to any remote server or cloud API.

![PDFtoPDFocr main window](README/screenshots/main.png)

## System Architecture & Data Flow

```mermaid
graph TD
    A[Scanned PDF File / Batch] --> B[PySide6 Desktop GUI]
    B --> C[pdf2image / Poppler Rasterizer]
    C --> D[pytesseract / Portable Tesseract Engine]
    D --> E[pikepdf / PDF Assembler]
    E --> F[Searchable Output _ocred.pdf]
    B --> G[Job Exporter]
    G --> H[pdftopdfocr-job-v1.json Manifest]
    H --> I[Web/PWA Companion Preview]
```

## Features

- **Batch Processing** — Convert multiple PDFs and images at once (file picker or drag & drop)
- **Direct Image Import** — Convert JPG, PNG, and multi-frame TIFF images directly into searchable PDFs
- **Selectable OCR Language** — Quick selection for German, English, French, Spanish, and dozens of others
- **Auto-Download** — Missing Tesseract language packs are downloaded automatically from GitHub
- **Auto-Merge & Stacking** — Merge multiple processed OCR results into a single consolidated PDF document
- **Portable Tesseract** — Tesseract OCR is bundled locally; no global installation required
- **Original File Preserved** — Result saved as a new file with `_ocred.pdf` suffix or in a configured output folder
- **Job Manifest Export** — Save portable `pdftopdfocr-job-v1.json` manifests containing job settings and file metadata
- **Progress Indication** — Color-coded status per file with accessible UI controls

## Requirements

- Python 3.10+
- Windows 10/11

## Installation

```bash
pip install -r requirements.txt
```

Poppler must be available for `pdf2image` (via PATH variable or portable in the project folder).

## Usage

```bash
python PDFtoPDFocr_2.py
```

On Windows, `START.bat` also works as a double-click launcher.

1. Add PDFs or images via file picker or drag & drop
2. Select OCR language (missing packs are downloaded automatically)
3. Click "Start" - done
4. Use `Job-Export` when needed to save a portable `pdftopdfocr-job-v1.json` with settings, file metadata, and result hints.

Note: PDFtoPDFocr does not auto-detect document language. Select the matching OCR language before starting; missing Tesseract language packs are downloaded when needed.

## Tests / Verification

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

The test suite covers Tesseract configuration (`tests/test_tesseract_config.py`), job export format (`tests/test_export_format.py`), language switching (`tests/test_language_switch.py`), bug regressions (`tests/test_bug_regressions.py`), and release build validation (`tests/test_build_release.py`).

## Dependencies

| Package | License | Purpose |
|---|---|---|
| PySide6 | LGPL v3 | GUI framework |
| pytesseract | Apache 2.0 | Tesseract OCR wrapper |
| Pillow | HPND | Image processing & TIFF frame extraction |
| pdf2image | MIT | PDF to image rasterization |
| pikepdf | MPL 2.0 | PDF page merging & output assembly |
| requests | Apache 2.0 | Tesseract language pack download |

Can use a local portable **Tesseract OCR** (Apache 2.0) and Poppler setup.
Local runtime assets such as `tesseract_portable/`, `tessdata/`, `poppler/`, `dist/`, `build/`, and `releases/` stay out of Git via `.gitignore`.

## Privacy / Network Access

PDF files and images are processed locally and are not uploaded anywhere. Network access is only used when a missing Tesseract language pack is downloaded from GitHub.

Local runtime folders, build artifacts, releases, internal maintenance notes, and secrets are excluded through `.gitignore`.

## EXE / Portable Build

```bash
python build_release.py --clean

# or on Windows via double-click/terminal
build_exe.bat

# or directly with dependencies already installed
python -m PyInstaller --noconfirm --clean PDFtoPDFocr.spec
```

`build_release.py` creates an isolated `.build_venv`, installs only the runtime/build dependencies, and runs PyInstaller with the versioned spec file.

The packaged build is written to `dist/PDFtoPDFocr/`. When present, `tesseract_portable/` and `poppler/` are bundled automatically.

## Porting / Platform Strategy

The current porting decision is documented in `PORTIERUNGSPLAN.md`: Windows Store remains the primary release channel because the app bundles local batch OCR with Tesseract, Poppler, and PySide6.

macOS and Linux stay source and smoke-test targets from the same desktop codebase. Dedicated desktop packaging should follow only after the Windows Store release path is finalized.

## License

MIT License
