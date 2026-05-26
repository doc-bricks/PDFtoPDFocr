# PDFtoPDFocr - PDF OCR Converter

Wandelt gescannte PDF-Dateien in durchsuchbare PDFs um: per OCR (Texterkennung) mit Tesseract. Batch-Verarbeitung, auswählbare OCR-Sprache, automatischer Sprachpaket-Download und portable Tesseract-Integration.

![PDFtoPDFocr Hauptfenster](README/screenshots/main.png)

## Features

- **Batch-Verarbeitung** — Mehrere PDFs auf einmal konvertieren (Dateiauswahl oder Drag & Drop)
- **Auswählbare OCR-Sprache** — Schnellwahl für Deutsch, Englisch, Französisch und Spanisch
- **Multi-Language** — Unterstützung für dutzende Sprachen (deu, eng, fra, spa, ...)
- **Auto-Download** — Fehlende Sprachpakete werden automatisch von GitHub geladen
- **Portable Tesseract** — Tesseract OCR ist integriert, keine separate Installation nötig
- **Originaldatei erhalten** — Ergebnis als neue Datei mit Suffix `_ocred.pdf`
- **Fortschrittsanzeige** — Farbige Statusanzeige pro Datei

## Voraussetzungen

- Python 3.10+
- Windows 10/11

## Installation

```bash
pip install -r requirements.txt
```

Poppler muss für `pdf2image` verfügbar sein (als PATH-Variable oder portable im Projektordner).

## Verwendung

```bash
python PDFtoPDFocr_2.py
```

Unter Windows funktioniert außerdem `START.bat` als Doppelklick-Einstieg.

1. PDFs per Dateiauswahl oder Drag & Drop hinzufügen
2. OCR-Sprache auswählen (fehlende Pakete werden automatisch geladen)
3. "Start" klicken - fertig

Hinweis: PDFtoPDFocr erkennt die Dokumentsprache nicht automatisch. Wählen Sie vor dem Start die passende OCR-Sprache aus; fehlende Tesseract-Sprachpakete werden bei Bedarf nachgeladen.

## Tests / Verifikation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

Der aktuelle lokale Check vom 2026-05-15 prüft die Tesseract-Konfiguration über
`tests/test_tesseract_config.py` und hält die Packaging-/Runtime-Pfade
mit dem Build-Workflow synchron.

## Abhängigkeiten

| Paket | Lizenz | Zweck |
|---|---|---|
| PySide6 | LGPL v3 | GUI-Framework |
| pytesseract | Apache 2.0 | Tesseract-OCR-Wrapper |
| Pillow | HPND | Bildverarbeitung |
| pdf2image | MIT | PDF zu Bild-Konvertierung |
| pikepdf | MPL 2.0 | PDF-Zusammenführung |
| requests | Apache 2.0 | Sprachpaket-Download |

Optional lokal gebündelt: **Tesseract OCR** (Apache 2.0) und Poppler. Die großen Runtime-Ordner `tesseract_portable/`, `tessdata/`, `poppler/`, `dist/`, `build/` und `releases/` sind bewusst per `.gitignore` ausgeschlossen.

## Datenschutz / Netzwerkzugriff

PDF-Dateien werden lokal verarbeitet und nicht hochgeladen. Netzwerkzugriff wird nur genutzt, wenn ein fehlendes Tesseract-Sprachpaket automatisch von GitHub nachgeladen wird.

Lokale Runtime-Ordner, Build-Artefakte, Releases, interne Wartungsnotizen und Secrets werden per `.gitignore` ausgeschlossen.

## EXE / Portable Build

```bash
python build_release.py --clean

# oder unter Windows per Doppelklick/Terminal
build_exe.bat

# oder direkt mit vorhandenen Abhängigkeiten
python -m PyInstaller --noconfirm --clean PDFtoPDFocr.spec
```

`build_release.py` legt dafür ein isoliertes `.build_venv` an, installiert nur
die nötigen Runtime-/Build-Abhängigkeiten und startet PyInstaller mit der
versionierten Spec-Datei.

Die Ausgabe landet in `dist/PDFtoPDFocr/`. Falls vorhanden, werden `tesseract_portable/` und `poppler/` automatisch mit in den Build aufgenommen.

## Portierung / Plattformstrategie

Die aktuelle Portierungsentscheidung steht in `PORTIERUNGSPLAN.md`: Windows Store bleibt der erste Release-Kanal, weil die App lokale Batch-OCR mit Tesseract, Poppler und PySide6 bündelt. Android, iOS und Web sollen nicht als sofortige native Clones entstehen, sondern über einen Web/PWA-Companion mit dem geplanten Austauschformat `pdftopdfocr-job-v1.json` vorbereitet werden.

macOS und Linux bleiben zunächst Source- und Smoke-Test-Ziele aus derselben Desktop-Codebasis. Eine eigene Desktop-Paketierung folgt erst, wenn Windows Store und PWA-Linie stabil sind.

## Lizenz

MIT License

---

## English

# PDFtoPDFocr - PDF OCR Converter

Converts scanned PDF files into searchable PDFs using OCR (text recognition) with Tesseract. Batch processing, selectable OCR language, automatic language pack download, and portable Tesseract integration.

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

1. Add PDFs via file picker or drag & drop
2. Select OCR language (missing packs are downloaded automatically)
3. Click "Start" - done

Note: PDFtoPDFocr does not auto-detect the document language. Select the matching OCR language before starting; missing Tesseract language packs are downloaded when needed.

## Tests / Verification

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

The current local check from 2026-05-15 covers the Tesseract configuration through
`tests/test_tesseract_config.py` and keeps packaging/runtime paths aligned
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

The current porting decision is documented in `PORTIERUNGSPLAN.md`: Windows Store remains the first release channel because the app bundles local batch OCR with Tesseract, Poppler, and PySide6. Android, iOS, and web should start through a Web/PWA companion and the planned `pdftopdfocr-job-v1.json` exchange format, not through immediate native clones.

macOS and Linux stay source and smoke-test targets from the same desktop codebase for now. Dedicated desktop packaging should follow only after the Windows Store and PWA paths are stable.

## License

MIT License
