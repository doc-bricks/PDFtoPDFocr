# PDFtoPDFocr - PDF OCR Converter

Converts scanned PDF files into searchable PDFs using OCR (text recognition) with Tesseract. Batch processing, selectable OCR language, automatic language pack download, and portable Tesseract integration.

Machine-readable project context: [`llms.txt`](llms.txt) | [Deutsche Dokumentation](README_de.md)

![PDFtoPDFocr main window](README/screenshots/main.png)

## Features

- **Batch Processing** — Convert multiple PDFs at once (file picker or drag & drop)
- **Selectable OCR Language** — Quick selection for German, English, French, and Spanish
- **Multi-Language** — Support for dozens of languages (deu, eng, fra, spa, ...)
- **Auto-Download** — Missing language packs are downloaded automatically from GitHub
- **Portable Tesseract** — Tesseract OCR is bundled, no separate installation needed
- **Original File Preserved** — Result saved as new file with `_ocred.pdf` suffix
- **Progress Indication** — Color-coded status per file

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

1. Add PDFs via file picker or drag & drop
2. Select OCR language (missing packs are downloaded automatically)
3. Click "Start" - done
4. Use `Job-Export` when needed to save a portable `pdftopdfocr-job-v1.json` with settings, file metadata, and result hints.

Note: PDFtoPDFocr does not auto-detect the document language. Select the matching OCR language before starting; missing Tesseract language packs are downloaded when needed.

## Tests / Verification

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

The current local checks cover the Tesseract configuration through
`tests/test_tesseract_config.py` plus the portable job export through
`tests/test_export_format.py`, and keep packaging/runtime paths aligned
with the build workflow.

## Dependencies

| Package | License | Purpose |
|---|---|---|
| PySide6 | LGPL v3 | GUI framework |
| pytesseract | Apache 2.0 | Tesseract OCR wrapper |
| Pillow | HPND | Image processing |
| pdf2image | MIT | PDF to image conversion |
| pikepdf | MPL 2.0 | PDF merging |
| requests | Apache 2.0 | Language pack download |

Can use a local portable **Tesseract OCR** (Apache 2.0) and Poppler setup.
Local runtime assets such as `tesseract_portable/`, `tessdata/`, `poppler/`, `dist/`, `build/`, and `releases/` stay out of Git via `.gitignore`.

## Privacy / Network Access

PDF files are processed locally and are not uploaded. Network access is only used when a missing Tesseract language pack is downloaded from GitHub.

Local runtime folders, build artifacts, releases, internal maintenance notes, and secrets are excluded through `.gitignore`.

## EXE / Portable Build

```bash
python build_release.py --clean

# or on Windows via double-click/terminal
build_exe.bat

# or directly with dependencies already installed
python -m PyInstaller --noconfirm --clean PDFtoPDFocr.spec
```

`build_release.py` creates an isolated `.build_venv`, installs only the
runtime/build dependencies, and runs PyInstaller with the versioned spec file.

The packaged build is written to `dist/PDFtoPDFocr/`. When present, `tesseract_portable/` and `poppler/` are bundled automatically.

## Porting / Platform Strategy

The current porting decision is documented in `PORTIERUNGSPLAN.md`: PDFtoPDFocr remains a desktop-first OCR app. Windows Store is the main release path because the app bundles local batch OCR with Tesseract, Poppler, and PySide6.

The former Web/PWA companion was removed after a use-case audit. Android, iOS, web, native mobile apps, and app-managed sync are not active product lines unless a new concrete user use-case is documented.

macOS and Linux stay source and smoke-test targets from the same desktop codebase for now. Dedicated desktop packaging should follow only after the Windows Store path is current or real macOS/Linux demand is documented.

## License

MIT License
