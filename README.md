# PDFtoPDFocr — PDF OCR Converter

Wandelt gescannte PDF-Dateien in durchsuchbare PDFs um — per OCR (Texterkennung) mit Tesseract. Batch-Verarbeitung, automatischer Sprachpaket-Download, portable Tesseract-Integration.

## Features

- **Batch-Verarbeitung** — Mehrere PDFs auf einmal konvertieren (Dateiauswahl oder Drag & Drop)
- **Automatische Spracherkennung** — Sprache wird automatisch erkannt
- **Multi-Language** — Unterstuetzung fuer dutzende Sprachen (deu, eng, fra, spa, ...)
- **Auto-Download** — Fehlende Sprachpakete werden automatisch von GitHub geladen
- **Portable Tesseract** — Tesseract OCR ist integriert, keine separate Installation noetig
- **Originaldatei erhalten** — Ergebnis als neue Datei mit Suffix `_ocred.pdf`
- **Fortschrittsanzeige** — Farbige Statusanzeige pro Datei

## Voraussetzungen

- Python 3.10+
- Windows 10/11

## Installation

```bash
pip install PySide6 pytesseract Pillow pdf2image pikepdf requests
```

Poppler muss fuer `pdf2image` verfuegbar sein (als PATH-Variable oder portable im Projektordner).

## Verwendung

```bash
python PDFtoPDFocr_2.py
```

1. PDFs per Dateiauswahl oder Drag & Drop hinzufuegen
2. OCR-Sprache auswaehlen (fehlende Pakete werden automatisch geladen)
3. "Start" klicken — fertig

## Abhaengigkeiten

| Paket | Lizenz | Zweck |
|---|---|---|
| PySide6 | LGPL v3 | GUI-Framework |
| pytesseract | Apache 2.0 | Tesseract-OCR-Wrapper |
| Pillow | HPND | Bildverarbeitung |
| pdf2image | MIT | PDF zu Bild-Konvertierung |
| pikepdf | MPL 2.0 | PDF-Zusammenfuehrung |
| requests | Apache 2.0 | Sprachpaket-Download |

Ausserdem gebundelt: **Tesseract OCR** (Apache 2.0) als portable Version.

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
pip install PySide6 pytesseract Pillow pdf2image pikepdf requests
```

Poppler must be available for `pdf2image` (via PATH variable or portable in the project folder).

## Usage

```bash
python PDFtoPDFocr_2.py
```

1. Add PDFs via file picker or drag & drop
2. Select OCR language (missing packs are downloaded automatically)
3. Click "Start" — done

## Dependencies

| Package | License | Purpose |
|---|---|---|
| PySide6 | LGPL v3 | GUI framework |
| pytesseract | Apache 2.0 | Tesseract OCR wrapper |
| Pillow | HPND | Image processing |
| pdf2image | MIT | PDF to image conversion |
| pikepdf | MPL 2.0 | PDF merging |
| requests | Apache 2.0 | Language pack download |

Also bundled: **Tesseract OCR** (Apache 2.0) as portable version.

## License

MIT License
