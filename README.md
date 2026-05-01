# PDFtoPDFocr — PDF OCR Converter

Wandelt gescannte PDF-Dateien in durchsuchbare PDFs um — per OCR (Texterkennung) mit Tesseract. Batch-Verarbeitung, automatischer Sprachpaket-Download, portable Tesseract-Integration.

![PDFtoPDFocr Hauptfenster](README/screenshots/main.png)

## Features

- **Batch-Verarbeitung** — Mehrere PDFs auf einmal konvertieren (Dateiauswahl oder Drag & Drop)
- **Automatische Spracherkennung** — Sprache wird automatisch erkannt
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
3. "Start" klicken — fertig

## Tests / Verifikation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

Der aktuelle lokale Check prüft die Tesseract-Konfiguration über
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

## Lizenz

MIT License

---

## English

# PDFtoPDFocr — PDF OCR Converter

Converts scanned PDF files into searchable PDFs using OCR (text recognition) with Tesseract. Batch processing, automatic language pack download, portable Tesseract integration.

## Features

- **Batch Processing** — Convert multiple PDFs at once (file picker or drag & drop)
- **Automatic Language Detection** — Language is detected automatically
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
3. Click "Start" — done

## Tests / Verification

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

The current local check covers the Tesseract configuration through
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

## License

MIT License
