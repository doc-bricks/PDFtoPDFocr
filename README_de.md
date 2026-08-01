# PDFtoPDFocr - PDF OCR Converter

Wandelt gescannte PDF-Dateien in durchsuchbare PDFs um: per OCR (Texterkennung) mit Tesseract. Batch-Verarbeitung, auswählbare OCR-Sprache, automatischer Sprachpaket-Download und portable Tesseract-Integration.

Maschinenlesbarer Projektkontext: [`llms.txt`](llms.txt) | [English Documentation](README.md)

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
4. Bei Bedarf `Job-Export` nutzen, um ein portables `pdftopdfocr-job-v1.json` mit Einstellungen, Dateimetadaten und Ergebnis-Hinweisen zu speichern.

Hinweis: PDFtoPDFocr erkennt die Dokumentsprache nicht automatisch. Wählen Sie vor dem Start die passende OCR-Sprache aus; fehlende Tesseract-Sprachpakete werden bei Bedarf nachgeladen.

## Tests / Verifikation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

Der aktuelle lokale Check deckt die Tesseract-Konfiguration über
`tests/test_tesseract_config.py` sowie den Job-Export über
`tests/test_export_format.py` ab und hält Packaging-/Runtime-Pfade
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

Die aktuelle Portierungsentscheidung steht in `PORTIERUNGSPLAN.md`: PDFtoPDFocr bleibt eine Desktop-first-OCR-App. Windows Store ist der wichtigste Release-Pfad, weil die App lokale Batch-OCR mit Tesseract, Poppler und PySide6 bündelt.

Der frühere Web/PWA-Companion wurde nach einem Usecase-Audit entfernt. Android, iOS, Web, native Mobile-Apps und App-eigene Synchronisierung sind keine aktiven Produktlinien, solange kein neuer konkreter Nutzer-Usecase dokumentiert ist.

macOS und Linux bleiben zunächst Source- und Smoke-Test-Ziele aus derselben Desktop-Codebasis. Eine eigene Desktop-Paketierung folgt erst, wenn der Windows-Store-Pfad aktuell ist oder echte macOS-/Linux-Nachfrage dokumentiert wurde.

## Lizenz

MIT License
