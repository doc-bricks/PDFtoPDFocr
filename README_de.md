<img src="assets/banner.png" width="100%" alt="PDFtoPDFocr Banner">

[English](README.md) | [Deutsch](README_de.md)

# PDFtoPDFocr - Lokaler PDF OCR Konverter

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version 1.1.4](https://img.shields.io/badge/version-1.1.4-blue.svg)](pyproject.toml)
[![Lizenz MIT](https://img.shields.io/badge/lizenz-MIT-green.svg)](LICENSE)
[![UI Engine](https://img.shields.io/badge/UI%20Engine-PySide6%20%7C%20Qt-41cd52.svg)](https://www.qt.io/)
[![Plattform](https://img.shields.io/badge/plattform-Windows%2010%2F11%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](#voraussetzungen--plattformmatrix)
[![Datenschutz](https://img.shields.io/badge/datenschutz-100%25%20Offline%20%2F%20Zero--Egress-success.svg)](#datenschutz--sicherheitsmodell)
[![Sicherheit](https://img.shields.io/badge/sicherheit-Local--First-blue.svg)](SECURITY.md)
[![i18n](https://img.shields.io/badge/i18n-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-blue.svg)](#funktionen--features)
[![Pytest](https://img.shields.io/badge/pytest-121%20bestanden%20%7C%20100%25-brightgreen.svg)](tests/)
[![Drittanbieter-Lizenzen](https://img.shields.io/badge/Drittanbieter--Lizenzen-auditiert-green.svg)](THIRD_PARTY_LICENSES.md)
[![Marketing-Log](https://img.shields.io/badge/Marketing--Log-aktiv-blue.svg)](MARKETING-LOG.txt)
[![LLM-Bereit](https://img.shields.io/badge/LLM--Ready-llms.txt-blueviolet.svg)](llms.txt)
[![Ökosystem](https://img.shields.io/badge/%C3%96kosystem-doc--bricks-orange.svg)](https://github.com/doc-bricks)
[![Dachorganisation](https://img.shields.io/badge/Dachorganisation-open--bricks-blue.svg)](https://github.com/open-bricks)
[![Zuletzt geprüft](https://img.shields.io/badge/zuletzt%20gepr%C3%BCft-2026--09--20-informational.svg)](tests/)

Wandelt gescannte PDF-Dateien in durchsuchbare PDFs um: per OCR (optische Zeichenerkennung) mit Tesseract. Batch-Verarbeitung, auswählbare OCR-Sprache, automatischer Sprachpaket-Download, verlustfreier Erhalt der Originaldateien, barrierefreie Benutzeroberfläche und portable Tesseract/Poppler-Integration.

Maschinenlesbarer Projektkontext: [`llms.txt`](llms.txt) | [English Documentation](README.md) | [Sicherheitsrichtlinie](SECURITY.md)

> [!NOTE]
> **KI & LLM-Integration:** Dieses Repository enthält eine strukturierte [`llms.txt`](llms.txt)-Datei mit maschinenlesbarem Kontext, Architektur-Details, CLI/GUI-Schnittstellen und Test-Einstiegspunkten für autonome KI-Agenten und Entwickler-Workflows.

> [!TIP]
> **Datenschutz & Lokale Verarbeitung:** PDF- und Bilddateien werden zu 100% lokal auf Ihrem System verarbeitet. Dokumente und OCR-Texte werden niemals auf externe Server oder Cloud-APIs hochgeladen.

![PDFtoPDFocr Hauptfenster](README/screenshots/main.png)

## Schnellnavigation

1. [Systemarchitektur & Komponenten-Workflow](#systemarchitektur--komponenten-workflow)
2. [Lokaler Datenfluss & Datenschutz-Isolation](#lokaler-datenfluss--datenschutz-isolation)
3. [Schnelleinstieg & Kernabläufe](#schnelleinstieg--kernabläufe)
4. [Funktionen & Features](#funktionen--features)
5. [Zielgruppen & Auffindbarkeit](#zielgruppen--auffindbarkeit)
6. [Barrierefreiheit & Tastenkürzel](#barrierefreiheit--tastenkürzel)
7. [Voraussetzungen & Plattformmatrix](#voraussetzungen--plattformmatrix)
8. [Installation & Portables Setup](#installation--portables-setup)
9. [Nutzung & Ausführungsrichtlinien](#nutzung--ausführungsrichtlinien)
10. [Tests & Qualitätsprüfung](#tests--qualitätsprüfung)
11. [Geschwister-Tools & Ökosystem](#geschwister-tools--ökosystem)
12. [Drittanbieter-Lizenzen & Transparenz](#drittanbieter-lizenzen--transparenz)
13. [Datenschutz & Sicherheitsmodell](#datenschutz--sicherheitsmodell)
14. [EXE & Distributions-Packaging](#exe--distributions-packaging)
15. [Maschinenlesbarer LLM-Kontext](#maschinenlesbarer-llm-kontext)
16. [Mitwirken & Lizenz](#mitwirken--lizenz)

## Systemarchitektur & Komponenten-Workflow

```mermaid
graph TD
    A["Gescannte PDF / Bilder (JPG, PNG, TIFF)"] --> B["PySide6 Desktop GUI (Drag & Drop / Warteschlange)"]
    B --> C["Worker Thread (Asynchrone Verarbeitung)"]
    C --> D["pdf2image / Poppler Rasterizer"]
    D --> E["Portable Tesseract OCR Engine"]
    E --> F["pikepdf / PDF Assembler"]
    F --> G["Durchsuchbare PDF-Ausgabe (_ocred.pdf)"]
    C --> H["Job-Manifest-Exporter"]
    H --> I["pdftopdfocr-job-v1.json"]
    style G fill:#d4edda,stroke:#28a745,stroke-width:2px
    style I fill:#d1ecf1,stroke:#17a2b8,stroke-width:2px
```

## Lokaler Datenfluss & Datenschutz-Isolation

```mermaid
sequenceDiagram
    autonumber
    actor User as Benutzer / Batch-Operator
    participant GUI as PySide6 Desktop GUI
    participant Worker as Lokaler Worker Thread
    participant Poppler as Poppler / pdf2image
    participant Tesseract as Tesseract OCR Engine
    participant Assembler as pikepdf PDF-Assembler
    participant FS as Lokales Dateisystem

    User->>GUI: PDF- / Bilddateien hinzufügen (Drag & Drop)
    User->>GUI: OCR-Sprache auswählen (z.B. deu, eng)
    User->>GUI: Klick auf Stapelverarbeitung starten
    GUI->>Worker: Asynchronen Konvertierungsjob starten
    loop Für jedes Dokument
        Worker->>Poppler: PDF-Seiten in lokalen Arbeitsspeicher rasterisieren
        Poppler-->>Worker: Hochauflösende Seiten-Bitmaps zurückgeben
        Worker->>Tesseract: Textextraktion & Bounding-Boxes via lokaler Engine
        Tesseract-->>Worker: OCR-Text & hOCR-/PDF-Layer zurückgeben
        Worker->>Assembler: Durchsuchbare Textebene in PDF-Struktur injizieren
        Assembler->>FS: Speichern als <Original>_ocred.pdf (Verlustfrei)
        Worker-->>GUI: Fortschrittsbalken & Farbstatus-Badge aktualisieren
    end
    opt Portabler Job-Manifest-Export
        GUI->>FS: pdftopdfocr-job-v1.json schreiben (0 rohe PDF-Bytes)
    end
    Note over User,FS: 100% Local-First / Zero-Egress Betrieb (Kein Cloud-Upload)
```

## Schnelleinstieg & Kernabläufe

| Aufgabe | Schnittstelle / Befehl | Ausgabe / Ergebnis |
|---|---|---|
| **Desktop-App starten** | `python PDFtoPDFocr_2.py` oder `START.bat` | PySide6 Desktop-GUI mit Drag & Drop Warteschlange |
| **Gescannte PDFs umwandeln** | Dateien hinzufügen, Sprache wählen, "Start" (`Strg+Eingabetaste`) | Verlustfreie `*_ocred.pdf` mit Volltext-Suchlayer |
| **Direkte Bild-OCR** | JPG, PNG oder mehrseitige TIFF-Dateien hineinziehen | Zusammengefügtes durchsuchbares PDF-Dokument |
| **In Sammel-PDF vereinen** | "Auto-Merge" in Menüleiste aktivieren | Konsolidierte mehrseitige durchsuchbare Sammel-PDF |
| **Job-Manifest exportieren** | Klick auf "Job-Export" (`Strg+E`) | Portables `pdftopdfocr-job-v1.json` Manifest |
| **Testsuite ausführen** | `python -m pytest` | 110 verifizierte Unit-, Regressions-, Barrierefreiheits- und Metadaten-Tests |
| **Portablen Build erzeugen** | `python build_release.py --clean` | Eigenständige ausführbare Datei in `dist/PDFtoPDFocr/` |

## Funktionen & Features

- **Batch-Verarbeitung** – Mehrere PDFs und Bilder gleichzeitig konvertieren (Dateiauswahl oder Drag & Drop).
- **Direkter Bild-Import** – JPG, PNG und mehrseitige TIFF-Dateien direkt ohne Zwischenschritte per OCR in durchsuchbare PDFs umwandeln.
- **Auswählbare OCR-Sprache** – Schnellwahl für Deutsch, Englisch, Französisch, Spanisch und dutzende weitere Sprachen.
- **Auto-Download** – Fehlende Tesseract-Sprachpakete (`.traineddata`) werden bei Bedarf automatisch von offiziellen GitHub-Repositories geladen.
- **Auto-Merge & Stapeln** – Mehrere verarbeitete OCR-Ergebnisse zu einer konsolidierten Sammel-PDF zusammenfassen.
- **Portable Tesseract & Poppler** – Tesseract OCR ist integriert; keine globale Systeminstallation nötig.
- **Originaldatei erhalten** – Ergebnisse werden als neue Datei mit Suffix `_ocred.pdf` oder im konfigurierten Ausgabeverzeichnis gespeichert; Originale bleiben unberührt.
- **Job-Manifest-Export** – Über `Job-Export` ein portables `pdftopdfocr-job-v1.json` mit Einstellungen, Ausführungsstatus und Dateimetadaten speichern.
- **Vollständige Barrierefreiheit (A11y) & Ergonomie** – Screenreader-fähige Namen (`AccessibleName`) und Beschreibungen (`AccessibleDescription`) auf allen Steuerelementen, kontextsensitive Tooltips in aktiver Sprache und vollständige Tastaturkürzel (`Strg+O`, `Strg+Eingabetaste`, `Strg+E`, `F5`, `Strg+Umschalt+O`, `Entf`/`Rückschritt`).
- **Kontraststarke Statusanzeige** – WCAG-konforme Farbgebung (`#0b6e4f` / `#b45309`) und dateiindividuelle Hover-Tooltips mit aktuellem Verarbeitungsstatus.

## Zielgruppen & Auffindbarkeit

| Zielgruppe / Persona | Typische Herausforderung | Lösung durch PDFtoPDFocr |
|---|---|---|
| **Rechtswesen, Medizin & Compliance** | Cloud-OCR-Dienste verletzen DSGVO/HIPAA-Vorgaben; Risiko von Dokumentenleaks auf externen Servern. | 100% lokale, abgeschirmte OCR-Verarbeitung auf dem eigenen Gerät. Quelldateien bleiben unberührt (`_ocred.pdf`). |
| **Archivare & Wissenschaftler** | Digitalisierung umfangreicher Scans und mehrseitiger TIFFs verursacht unkalkulierbare SaaS-Kosten. | Schnelle Stapelverarbeitung, Multi-Format-Bildwarteschlange, mehrsprachige Tesseract-Modelle, automatisches Zusammenführen. |
| **Datenschutzbewusste Wissensarbeiter** | Proprietäre Programme (Adobe Acrobat, ABBYY) erfordern teure Abos, Cloud-Zwang und Administratorrechte. | Kostenloses MIT-Werkzeug, Ausführung im unprivilegierten Standardbenutzer-Modus, null Telemetrie, portables Paket. |
| **Tooling- & Pipeline-Entwickler** | Desktop-GUIs bieten selten überprüfbare Ausführungsnachweise oder maschinenlesbare Schnittstellen. | Strukturierter Job-Manifest-Export (`pdftopdfocr-job-v1.json`), deterministische Exit-Codes und `llms.txt`. |

## Barrierefreiheit & Tastenkürzel

| Aktion | Tastaturkürzel | Beschreibung |
|---|---|---|
| **Dateien hinzufügen** | `Strg+O` | Öffnet den Dateiauswahldialog |
| **OCR starten** | `Strg+Eingabetaste` | Startet die Stapelverarbeitung |
| **Job-Manifest exportieren** | `Strg+E` | Exportiert den Auftragsstatus als JSON-Manifest |
| **Liste leeren / Reset** | `F5` | Setzt Dateiliste und Statusanzeige zurück |
| **Ausgabeordner wählen** | `Strg+Umschalt+O` | Wählt ein individuelles Zielverzeichnis |
| **Eintrag entfernen** | `Entf` oder `Rückschritt` | Entfernt ausgewählte Datei aus der Liste |

## Voraussetzungen & Plattformmatrix

- Python 3.10+
- Windows 10/11 (Primäre Release-Plattform)
- macOS / Linux (Quellcode- und Smoke-Test-Ziele)

## Installation & Portables Setup

```bash
pip install -r requirements.txt
```

Poppler muss für `pdf2image` verfügbar sein (als PATH-Variable oder portable im Projektordner).

## Nutzung & Ausführungsrichtlinien

```bash
python PDFtoPDFocr_2.py
```

Unter Windows funktioniert außerdem `START.bat` als Doppelklick-Einstieg.

1. PDFs oder Bilder per Dateiauswahl oder Drag & Drop hinzufügen.
2. OCR-Sprache auswählen (fehlende Pakete werden automatisch geladen).
3. "Start" klicken – fertig.
4. Bei Bedarf `Job-Export` nutzen, um ein portables `pdftopdfocr-job-v1.json` mit Einstellungen und Dateimetadaten zu sichern.

## Tests & Qualitätsprüfung

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

Die Test-Suite deckt folgende Kernbereiche ab:
- **UI-Barrierefreiheit & Tastaturkürzel** (`tests/test_ui_accessibility.py`)
- **Tesseract-Konfiguration** (`tests/test_tesseract_config.py`)
- **Job-Export-Format & Manifest-Schema** (`tests/test_export_format.py`)
- **Sprachumschaltung & Multi-Language-Support** (`tests/test_language_switch.py`)
- **Bug-Regressionen & Ressourcen-Lifecycle** (`tests/test_bug_regressions.py`)
- **App-Icons & Visuelle Asset-Prüfung** (`tests/test_app_assets.py`)
- **Plattform-Paketierung & Release-Build-Validierung** (`tests/test_build_release.py`, `tests/test_platform_package_gate.py`)
- **Metadaten-, Sicherheits- & Paritäts-Governance** (`tests/test_metadata.py`, `tests/test_security_license_contract.py`)

## Geschwister-Tools & Ökosystem

PDFtoPDFocr ist Teil der **doc-bricks** Dokumentenwerkzeuge-Familie und des übergreifenden **open-bricks** Open-Source-Ökosystems:

| Werkzeug | Ökosystem | Zweck | Repository |
|---|---|---|---|
| **DokuReader** | `doc-bricks` | Lokale Dokumentenbibliothek, Leseumgebung & viewer für diverse Formate | [doc-bricks/DokuReader](https://github.com/doc-bricks/DokuReader) |
| **MediaBrain** | `doc-bricks` | Lokaler Medien-Metadaten-Inspektor, EXIF-Analyzer & Stapelklassifizierer | [doc-bricks/MediaBrain](https://github.com/doc-bricks/MediaBrain) |
| **UniversalDocsGrabber** | `doc-bricks` | Automatisierte E-Mail-Dokumentenextraktion & OCR-Stapelerfassungs-Pipeline | [doc-bricks/UniversalDocsGrabber](https://github.com/doc-bricks/UniversalDocsGrabber) |
| **UniversalInvoiceMail** | `doc-bricks` | Intelligente Rechnungsextraktion, Datums-/Betragsparameter & DATEV-Export | [doc-bricks/UniversalInvoiceMail](https://github.com/doc-bricks/UniversalInvoiceMail) |
| **UniversalMailCleaner** | `doc-bricks` | Datenschutzorientierter Postfach-Bereiniger, Newsletter-Abmelder & Filter | [doc-bricks/UniversalMailCleaner](https://github.com/doc-bricks/UniversalMailCleaner) |
| **CleanMarkdown** | `doc-bricks` | Markdown-Bereinigung, Tabellenformatierung & Dokumentations-Linter | [doc-bricks/CleanMarkdown](https://github.com/doc-bricks/CleanMarkdown) |
| **LitZentrum** | `doc-bricks` | Akademischer Literaturmanager, BibTeX-Zitationsverwaltung & Recherche-Hub | [doc-bricks/LitZentrum](https://github.com/doc-bricks/LitZentrum) |
| **MailProcessor** | `doc-bricks` | Regelbasierte lokale E-Mail-Archivierung, Anhang-Filterung & Sortier-Engine | [doc-bricks/MailProcessor](https://github.com/doc-bricks/MailProcessor) |
| **ProFiler** | `file-bricks` | Schnelle Mehrkriterien-Dateisuche, Regex-Filterung & Stapel-Umbenennung | [file-bricks/ProFiler](https://github.com/file-bricks/ProFiler) |
| **ExplorerPro** | `file-bricks` | Zweifenster-Desktop-Dateimanager mit Tabs, Lesezeichen & Hex-Vorschau | [file-bricks/ExplorerPro](https://github.com/file-bricks/ExplorerPro) |
| **DevCenter** | `dev-bricks` | Entwickler-Umgebungsmanager, Toolchain-Orchestrator & Projekt-Starter | [dev-bricks/DevCenter](https://github.com/dev-bricks/DevCenter) |
| **CodeBox** | `dev-bricks` | Offline Multi-Language Code Playground, Snippet-Sammlung & Sandbox | [dev-bricks/CodeBox](https://github.com/dev-bricks/CodeBox) |
| **open-bricks** | `open-bricks` | Dachorganisation & kuratierter Katalog datenschutzorientierter Desktop-Apps | [open-bricks](https://github.com/open-bricks) |

## Drittanbieter-Lizenzen & Transparenz

PDFtoPDFocr setzt auf vollständige Open-Source-Transparenz und verifizierte Lizenz-Compliance:
- **Keine AGPL / SSPL Kontamination:** Sämtliche Abhängigkeiten sind frei von restriktiven Copyleft- oder kommerziellen Dual-Lizenz-Modellen.
- **Dynamische Verlinkung & LGPL-3.0:** `PySide6` (Qt für Python) wird gemäß LGPLv3 dynamisch verlinkt; Benutzer können eigene Qt-Builds einbinden.
- **Strikte Subprozess-Trennung:** Externe Werkzeuge (`Poppler`-Utilities wie `pdftoppm` und `pdfinfo`) werden ausschließlich über isolierte Betriebssystem-Subprozesse mit bereinigten Argumenten aufgerufen, sodass kein GPL-Code in den Anwendungsspeicher eingebunden wird.
- **Permissive Kernbibliotheken:** `pytesseract` (Apache-2.0), `Pillow` (HPND), `pdf2image` (MIT), `pikepdf` (MPL-2.0) und `requests` (Apache-2.0) harmonieren vollständig mit der primären **MIT-Lizenz**.

Detaillierte Lizenztexte, Versionsgrenzen und Governance-Invarianten sind in [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) und [`MARKETING-LOG.txt`](MARKETING-LOG.txt) dokumentiert.

## Datenschutz & Sicherheitsmodell

PDF-Dateien und Bilder werden lokal verarbeitet und zu keinem Zeitpunkt hochgeladen. Netzwerkzugriff ist strikt auf das Herunterladen fehlender öffentlicher Tesseract-Sprachdateien von GitHub beschränkt. Siehe [`SECURITY.md`](SECURITY.md) für die vollständige Sicherheits- und Datenschutzrichtlinie.

## EXE & Distributions-Packaging

```bash
python build_release.py --clean

# oder unter Windows via Doppelklick / Terminal:
build_exe.bat

# oder direkt über PyInstaller bei installierten Abhängigkeiten:
python -m PyInstaller --noconfirm --clean PDFtoPDFocr.spec
```

Der fertige Build wird in `dist/PDFtoPDFocr/` erzeugt. Vorhandene Ordner `tesseract_portable/` und `poppler/` werden automatisch gebündelt.

## Maschinenlesbarer LLM-Kontext

Für autonome KI-Coding-Agenten, Pair-Programming-Assistenten und CI-Automatisierungen stellt dieses Repository eine optimierte [`llms.txt`](llms.txt)-Datei bereit. Diese enthält:
- Architekturüberblick und Komponenten-Rollen
- Testsuite-Befehle und Validierungs-Gates
- Sicherheits- und Laufzeit-Invarianten (`INV-LOCAL-01` bis `INV-SLA-10`)
- Verzeichnis- und Abhängigkeitsübersicht

## Mitwirken & Lizenz

Beiträge, Fehlerberichte und Pull Requests sind herzlich willkommen! Bitte stellen Sie vor dem Einreichen sicher, dass `pytest` und `ruff check .` fehlerfrei durchlaufen.

Dieses Projekt ist unter der [MIT-Lizenz](LICENSE) lizenziert.
