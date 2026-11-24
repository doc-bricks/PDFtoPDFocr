---
name: pdftopdfocr
description: Local batch OCR and PDF merging desktop & CLI tool (`PDFtoPDFocr` v1.1.4) converting scanned PDFs and images (JPG, PNG, TIFF) into searchable `_ocred.pdf` files via Tesseract, Poppler, and pikepdf.
version: 1.1.4
license: MIT
---

# PDFtoPDFocr — Product Skill (Human & LLM Dual-Use)

- **Supported software version:** `1.1.4` (source line frozen)
- **Repository:** `https://github.com/doc-bricks/PDFtoPDFocr`
- **Main entrypoint:** `PDFtoPDFocr_2.py`

## 1. Capabilities & Boundaries

**What PDFtoPDFocr does:**
- Converts scanned PDFs and images (`.pdf`, `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff`) locally into searchable `_ocred.pdf` files using `pdf2image` (Poppler), `pytesseract` (Tesseract), and `pikepdf`.
- Merges multiple OCRed PDFs into one collective PDF while archiving single-page results into `Einzeldateien/`.
- Exports job metadata without PDF byte payloads in the `pdftopdfocr-job-v1` JSON schema ([`EXPORTFORMAT.md`](EXPORTFORMAT.md)).
- Supports 6 UI languages (`de`, `en`, `es`, `zh`, `ja`, `ru`) and configurable OCR languages (`deu`, `eng`, `fra`, `spa`, or installed Tesseract traineddata).

**What PDFtoPDFocr does NOT do:**
- No cloud OCR, no document upload server, no firewall, and no OS sandbox ([`PRIVACY_POLICY.md`](PRIVACY_POLICY.md), [`SECURITY.md`](SECURITY.md)).
- When a requested Tesseract `<lang>.traineddata` file is missing locally, the application requests that public language model file via HTTPS GET from `github.com/tesseract-ocr/tessdata_best`.

## 2. Prerequisites & Launch

- **Python:** `>= 3.10` with dependencies from `requirements.txt` (`PySide6`, `pytesseract`, `Pillow`, `pdf2image`, `pikepdf`, `requests`).
- **System binaries:** Tesseract OCR and Poppler (`pdftoppm`), either bundled in `tesseract_portable/` or available on `PATH` / via `TESSERACT_CMD` and `TESSDATA_PREFIX`.
- **Human GUI start:** `python PDFtoPDFocr_2.py` (optionally pass file or folder paths for "Open with"; keyboard shortcuts: `Ctrl+O` add, `Ctrl+Return` OCR, `Ctrl+E` export job, `Ctrl+M` merge selected, `Ctrl+Shift+O` export folder, `F5` clear, `Del`/`Backspace` remove).

## 3. Machine / Headless CLI Interface

All core operations share the same business logic and staged atomic output publication (`staged_output()` + `validate_pdf_output()`, see [`SAVE_SAFETY.md`](SAVE_SAFETY.md)). Pass `--json` for structured machine output.

| Command | Purpose | Key Options |
|---|---|---|
| `python PDFtoPDFocr_2.py --version --json` | Read app name, version, export schema | `--json` |
| `python PDFtoPDFocr_2.py languages --json` | List supported UI & OCR languages | `--json` |
| `python PDFtoPDFocr_2.py check --ocr-lang eng --json` | Verify Tesseract, `tessdata`, and `pdftoppm` availability | `--ocr-lang <code_>`, `--json` |
| `python PDFtoPDFocr_2.py export-job <paths...> --out job.json --json` | Write `pdftopdfocr-job-v1` manifest (UTF-8 without BOM) | `--out <file>`, `--ocr-lang <code>`, `--export-folder <dir>` |
| `python PDFtoPDFocr_2.py merge <pdf1> <pdf2> ... --out merged.pdf --json` | Merge `>= 2` PDFs and archive singles into `Einzeldateien/` | `--out <file>`, `--json` |
| `python PDFtoPDFocr_2.py ocr <paths...> --lang eng --json` | Run headless local OCR to `<stem>_ocred.pdf` | `--lang <code>`, `--poppler-path <dir>`, `--json` |

## 4. Side Effects, Permissions & Error Behavior

- **File writes:**
  - `ocr` writes `<stem>_ocred.pdf` next to each input file via private same-directory staging (`pdftopdfocr-output-*`). Existing targets are only replaced after page-count validation succeeds.
  - `merge` writes `--out` atomically and moves source files into `<out.parent>/Einzeldateien/`. If archiving fails after saving the collective PDF, `archive_warnings` reports the details.
  - `export-job` writes UTF-8 JSON without BOM atomically.
  - GUI mode reads/writes user preferences (`ui_language`, `export_folder`) in `%APPDATA%/PDFtoPDFocr/config.json` (Windows) or `~/.config/PDFtoPDFocr/config.json` (Linux/macOS).
- **Exit codes (CLI):**
  - `0`: Success (or readiness check passed).
  - `1`: Runtime failure (OCR/Tesseract missing, merge/write error, or `check` missing runtime).
  - `2`: Invalid CLI usage or insufficient/invalid input arguments (e.g., `< 2` PDFs for `merge`, missing inputs for `ocr`, directory passed as `--out`).

## 5. Verification & Readback

After calling `ocr`, `merge`, or `export-job` with `--json`:
1. Check process exit code (`0`) and `"ok": true` in JSON output.
2. Verify `output_path` / `merged_path` exists on disk and inspect `"pages"` (for `merge`) or `"succeeded"` / `"failed"` (for `ocr`).
3. Keep `TESSERACT_CMD` / `TESSDATA_PREFIX` explicit in automated environments when using non-default installations.

## 6. Related Documentation

- LLM index: [`llms.txt`](llms.txt) (compatibility pointer: [`llm.txt`](llm.txt))
- Export schema: [`EXPORTFORMAT.md`](EXPORTFORMAT.md)
- Output staging guarantees: [`SAVE_SAFETY.md`](SAVE_SAFETY.md)
- Privacy & security: [`PRIVACY_POLICY.md`](PRIVACY_POLICY.md), [`SECURITY.md`](SECURITY.md)
