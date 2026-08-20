# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Behoben / Fixed
- **`build_exe.bat`: ungültiges `--specpath`-Flag entfernt** — PyInstaller lehnt diese Option
  ab, sobald ein bestehendes `.spec` übergeben wird ("option(s) not allowed: --specpath");
  der Build brach dadurch sofort ab. Fund + Fix im Rahmen der Windows-Store-Welle-1-Vorbereitung
  (T-20260816-296785081). Frischer Build verifiziert: EXE startet ohne Absturz, Pytest 53/1 grün.

### Hinzugefügt / Added
- **Discoverability, README-Design & Marketing (Pfad B)**: Badges in `README.md` & `README_de.md` um Testsuite (60 Passed, 100% grün), Version (`1.1.3`), Python (`>=3.10`), UI-Engine (`PySide6 | Qt`), Plattform (`Windows 10/11 | Linux | macOS`), Datenschutz (`100% Offline / Zero-Egress`), Sicherheit (`Local-First`), `doc-bricks` Ecosystem, `open-bricks` Umbrella und `llms.txt` Discovery synchronisiert.
- **Interaktive Mermaid-Diagramme**: (1) Systemarchitektur- und Komponenten-Workflow-Diagramm (Dokumenten-Input -> Poppler-Rasterizer -> Tesseract-Engine -> pikepdf-Assembler -> Durchsuchbare Ausgabe & Job-Manifest); (2) Lokaler Datenfluss- & Datenschutz-Isolations-Sequenzdiagramm mit 100% Offline- und Zero-Egress-Garantien in beiden Sprachfassungen integriert.
- **Zweisprachige Sicherheitsrichtlinie (`SECURITY.md`)**: Vollständige deutsch-englische Sicherheitsdokumentation mit Local-First & Zero-Egress Invarianten, kontrolliertem Netzwerkzugriff (ausschließlich bedarfsgerechte Tesseract-Sprachpakete), Originaldateischutz (verlustfreie Ausgabe via `_ocred.pdf`), Manifest-Isolation, Non-Elevation (Standard-Benutzerkontext) und privater Schwachstellenmeldung (`security@ellmos.ai` & GitHub Advisories) implementiert.
- **Geschwisterwerkzeuge-Matrix**: Umfassende Ökosystem-Tabelle über `doc-bricks` (DokuReader, MediaBrain, UniversalDocsGrabber, UniversalInvoiceMail, UniversalMailCleaner, CleanMarkdown, LitZentrum, MailProcessor), `file-bricks` (ProFiler, ExplorerPro), `dev-bricks` (DevCenter, CodeBox) und `open-bricks` in beiden README-Versionen eingebunden.
- **Metadaten- & Paritätstestsuite**: Neue automatisierte Testsuite `tests/test_metadata.py` für Manifest-, Badges-, Links-, Sicherheits- und `llms.txt`-Parität implementiert (6/6 Tests passed, Gesamtsuite 60/60 passed).
- **llms.txt & Schnelleinstieg**: `llms.txt` Last-checked Zeitstempel auf `2026-08-21` und 60 Tests aktualisiert; Schnelleinstieg-Tabelle in `README.md` und `README_de.md` ergänzt. [G 2026-08-21]
- **Windows-Store-Screenshot-Generator** (`scripts/generate_store_screenshots.py`): erzeugt die
  4 in `releases/windowsstore/SCREENSHOT_PLAN.md` geforderten Screenshots reproduzierbar aus
  neutralen Demo-Daten, mit demselben Tofu-/Font-Rendering-Selbsttest wie in ProSync/PromptBoard/
  Klangpult (bricht ab statt ein defektes Kästchen-Screenshot-Set stillschweigend zu erzeugen).

### Geändert / Changed
- **Technische Hygiene & Maintenance Check (Pfad A)**: `[tool.ruff]` und `[tool.ruff.lint]` Konfiguration in `pyproject.toml` integriert (`target-version = "py310"`, `line-length = 120`, `E501`/`E402`/`E722`/`E741`/`F841` ignore, `ruff check` 100% sauber), `llms.txt` Last-checked Zeitstempel auf `2026-08-16` aktualisiert, Testsuite (54/54 Pytest Tests passed) verifiziert. [G 2026-08-16]

## [1.1.3] - 2026-08-14

### Hinzugefügt / Added
- **App-Icon-Modernisierung & Asset-Set**: Master-App-Icon (512x512 PNG, RGB/RGBA) mit modernem PDF/OCR-Scanner-Motiv generiert und unter `assets/icon.png` sowie `PDFtoPDFocr.png` abgelegt. Multi-Resolution Windows-ICO-Dateien (`PDFtoPDFocr.ico`, `assets/app_icon.ico`, `assets/icon.ico`) mit allen Standardauflösungen (256x256, 128x128, 64x64, 48x48, 32x32, 24x24, 16x16) und `assets/favicon.ico` erzeugt. Standard-Kachel- und Store-Icons unter `assets/icons/` (`icon_44x44.png`, `icon_50x50.png`, `icon_150x150.png`, `icon_310x150.png`, `icon_310x310.png`) und `store_assets/` synchronisiert.
- **Runtime-Icon-Anbindung**: `get_project_root()`, `get_app_icon_path()` und `get_app_icon()` in `PDFtoPDFocr_2.py` implementiert; `OCRConverterGUI` und `QApplication` binden das Anwendungs-Icon verlässlich ein.
- **PyInstaller-Spec & Build**: `PDFtoPDFocr.spec` bindet `assets/` über `datas` ein und wählt prioritär `PDFtoPDFocr.ico`; `build_exe.bat` auf `.SOFTWARE`-Standard mit isoliertem Build-Root `C:\_Local_DEV\BUILDS\PDFtoPDFocr\1.1.3` modernisiert.
- **Asset-Testsuite**: Neue Testsuite `tests/test_app_assets.py` mit 5 Tests für Icon-Integrität, Formate, Auflösungen und GUI-Laufzeitbindung implementiert (54/54 passed, 100% grün).

### Behoben / Fixed
- **Bug-Regression BS-3 (pikepdf Lazy Page Lifecycle in `merge_ocr_outputs`)**: In `merge_ocr_outputs` wurden geöffnete Quell-PDF-Instanzen (`src_pdf`) bisher innerhalb der Schleife vor `merged.save()` geschlossen. Da `pikepdf` Seiteninhalte lazy referenziert, führte das vorzeitige Schließen zu potenziellen Stream- und Deskriptor-Fehlern beim Speichern der Sammel-PDF. Geöffnete Quell-PDFs werden nun bis nach dem Speichern offengehalten und sauber im äußeren `finally`-Block geschlossen. [G 2026-08-14]
- **Testabdeckung**: Regressionstests `test_bs3_merge_ocr_outputs_sources_kept_open_until_save` und `test_bs3_merge_ocr_outputs_functional_execution` in `tests/test_bug_regressions.py` ergänzt; Pytest-Suite auf 54/54 passed aktualisiert. [G 2026-08-14]

## [1.1.2] - 2026-08-04

### Geändert / Changed
- **Technische Hygiene & Maintenance Check (Pfad A)**: `pythonpath = ["."]` in `pyproject.toml` (`[tool.pytest.ini_options]`) und `pytest.ini` für Standalone-Testausführung ergänzt, Paketversion auf `1.1.2` synchronisiert, `llms.txt` Last-checked Zeitstempel auf `2026-08-04` aktualisiert. [G 2026-08-04]

## [1.1.2] - 2026-07-29

### Hinzugefügt / Added
- **Discoverability & Marketing Refresh (Pfad B)**: `llms.txt` Index-Header auf `Last-checked: 2026-07-29` und 47 verifizierte Pytest-Tests aktualisiert, Pytest-Badges in `README.md` und `README_de.md` auf 47 passed synchronisiert, Paketversion in `pyproject.toml` auf `1.1.1` angeglichen. [G 2026-07-29]

### Korrigiert / Fixed
- **TASKPLAN 1376 — Git-Konsolidierung**: Die durch Commit `98bd6b8` versehentlich wieder eingeführte Verzeichnisstruktur `web_companion/` erneut entfernt und damit den dokumentierten E04-Entscheid für eine Desktop-only-Anwendung wiederhergestellt.
- **TASKPLAN 1377 — Plattform-Paket-Gate**: Den vorhandenen `skipif`-Schutz für die bewusst nicht versionierte `AUFGABEN.txt` bestätigt; Zieltest (`2 passed`), Gesamtsuite (`47 passed`) und Source-Platform-Smoke sind grün.

## [1.1.1] - 2026-07-27

### Hinzugefügt / Added
- **Discoverability, SEO & README-Design Audit (Pfad B)**: Shields.io Status-Badges (Python 3.10+, License MIT, Pytest 51 passed, LLM-Ready, Ecosystem doc-bricks, Umbrella open-bricks), GFM-Hinweisboxen (`> [!NOTE]` für KI/LLM-Kontext, `> [!TIP]` für Datenschutz & lokale Offline-Verarbeitung), Sprachwechsler-Navigation (`[English](README.md) | [Deutsch](README_de.md)`) und Mermaid-Systemarchitektur- & Datenflussdiagramm in `README.md` und `README_de.md` eingebunden.
- **PEP 621 Standardisierung**: `pyproject.toml` mit vollständigen Metadaten, PyPI-Classifiers, Build-System (`setuptools`) und `[tool.pytest.ini_options]` Test-Konfiguration erstellt.
- **llms.txt Update**: Index-Header auf `Last-checked: 2026-07-27` und 52 verifizierte Pytest-Tests aktualisiert.

## [1.1.1] - 2026-07-25

### Hinzugefügt / Added
- **PEP 621 `pyproject.toml`**: Standardisierte Paketkonfiguration mit Metadaten (Name, Version, Lizenz, Keywords, URLs), Abhängigkeiten und Pytest-Pfadkonfiguration (`pythonpath = "."`) angelegt.
- **Shields.io Badges**: Python-Version, Pytest-Status (47 passed), MIT-Lizenz, Windows 10/11 Plattform, Tesseract 5 OCR Engine und LLM-Ready Badges in `README.md` und `README_de.md` integriert.
- **KI/LLM-Integrationshinweise & Architekturdiagramm**: `> [!NOTE]` Callout für KI-Agenten und offline Automatisierungsworkflows sowie Mermaid Architektur- & Datenfluss-Diagramm in `README.md` und `README_de.md` ergänzt.

### Geändert / Changed
- `llms.txt` Header auf `Last-checked: 2026-07-25` und 47 passing pytest unit/integration tests aktualisiert.


## [1.1.0] - 2026-07-24

Welle-1-Usertest-Feature-Paket (U1-U7): Bild-Import, Stapeln/Mergen und
Paket-Hygiene für den Windows-Store-Anlauf.

### Hinzugefügt / Added
- **U1 — Bild-Import**: JPG/PNG/TIFF können jetzt direkt (ohne PDF-Umweg) per OCR
  in ein durchsuchbares PDF umgewandelt werden. Mehrseitige TIFFs erzeugen eine
  Seite pro Frame. Keine neuen Abhängigkeiten (Pillow + `pytesseract.image_to_pdf_or_hocr`
  reichen), kein PyMuPDF, keine AGPL-Komponenten.
- **U2 — Stapeln/Mergen**: Kontextmenü „Markierte mergen" auf der Dateiliste
  fasst ausgewählte, bereits OCR-verarbeitete Ergebnisse zu einer Sammel-PDF
  zusammen; Drag-Umsortieren innerhalb der Liste bestimmt die Stapel-/Seitenreihenfolge.
- **U3 — Merge-Ablage**: Beim Merge wandern die einzelnen OCR-Ergebnis-PDFs in
  einen Unterordner „Einzeldateien", die Sammel-PDF landet auf Root-Ebene des
  Exportordners (Default: Ordner der Quelldatei).
- **U4 — Exportordner-Einstellung**: Konfigurierbarer Exportordner mit
  Zurücksetzen-Option; Fallback ist immer der Ordner der jeweiligen Quelldatei.
  Persistenz teilt sich die `config.json` mit der U6-Sprachauswahl (kein
  QSettings/Registry, bleibt Store-Sandboxing-konform).
- **U5 — Ordner-Import als Auto-Merge**: Wird ein ganzer Ordner hineingezogen,
  werden alle enthaltenen Bilder/PDFs als ein Batch getaggt; sobald alle
  Dateien des Batches verarbeitet sind, entsteht automatisch eine Sammel-PDF
  plus Unterordner mit den Einzeldateien.
- **U7 — Paket-Hygiene**: `build_release.collect_tesseract_portable_files()`
  schließt Tesseract-Trainingstools (`lstmtraining`, `cntraining`, `text2image`, …)
  und `tesseract-uninstall.exe` von der Paketierung aus (Build-/Paketkonfiguration
  betroffen, Quellordner unangetastet); reduziert unnötige WACK-relevante
  Executables im Store-Paket. Leptonica (Tesseract-Bildverarbeitungs-Unterbau,
  `libleptonica-6.dll`) hat jetzt einen eigenen Eintrag in
  `THIRD_PARTY_LICENSES.txt` (per Recherche verifiziert: zlib-artige,
  GPL-kompatible Eigenlizenz).
- **Welle-1 U1 — sichtbarer DE/EN-Anzeigesprachschalter**: Neue Combobox „Anzeigesprache / Display language" (Deutsch/English) oben im Fenster, klar getrennt von der bestehenden OCR-Sprachauswahl. Die Oberfläche stellt sofort um (`retranslate_ui`), die Auswahl wird pro Benutzer in `%APPDATA%\PDFtoPDFocr\config.json` (XDG-Fallback) persistiert und beim Start geladen. Das vorhandene `tr()`/`translations.json`-System ist damit erstmals über ein sichtbares Bedienelement erreichbar. Regressionstests: `tests/test_language_switch.py`.
- `Job-Export` in der Desktop-App ergänzt; die App schreibt jetzt `pdftopdfocr-job-v1.json` mit OCR-Sprache, Datei-Metadaten, Status und Ergebnis-Hinweisen ohne PDF-Inhalte.
- `llms.txt` als maschinenlesbaren Projektkontext für Repo-Checks und LLM-Crawler ergänzt.
- Regressionstests für Export-Schema, UTF-8 ohne BOM, fehlende Dateien, relative Pfade und leeren Projektstand ergänzt.
- `web_companion/` als statischen Offline-Prototyp ergänzt: Import von `pdftopdfocr-job-v1.json`, Demo-Modus, Filteransicht, Browser-Entwurf aus lokalen Dateimetadaten, Service Worker und Node-Tests.
- macOS/Linux source-platform smoke CI ergänzt: `source_platform_smoke.py` testet Source-Platform-Builds ohne Tesseract/Poppler-Binärdateien; `.github/workflows/source-platform-smoke.yml` führt die Checks auf ubuntu-latest und macos-latest aus.
- `MACOS_LINUX_PACKAGE_GATE.md` ergänzt; das Gate hält fest, dass eigene macOS-/Linux-Pakete erst nach Windows-Store- und PWA-Stabilität oder belegter Nachfrage gestartet werden.

### Geändert / Changed
- README und Store-Listing präzisieren auswählbare OCR-Sprache statt automatischer Spracherkennung.
- Datenschutz-, Release- und Drittanbieter-Hinweise auf den Wartungscheck vom 2026-05-15 synchronisiert.
- Deutsche Endnutzertexte auf echte Umlaute geprüft und bereinigt.
- Portierungsstrategie ergänzt: Windows Store zuerst, Web/PWA-Companion mit `pdftopdfocr-job-v1.json`, Android/iOS über PWA-Testpfad, macOS/Linux als Source-Smoke-Ziele.
- Exportformat und Companion-Doku beschreiben jetzt den realen Browser-Prototyp statt nur eines Platzhalters.
- Portierungsplan auf den macOS-/Linux-Package-Gate synchronisiert; aktuelle Unterstützung bleibt Source-Smoke, keine DMG-/PKG-/AppImage-/Flatpak-/Snap-Linie.
- `web_companion/` vollständig entfernt (kein belegter Usecase laut Audit 2026-07-23/24); die Desktop-App bleibt die primäre Plattform.

### Entfernt / Removed
- `web_companion/` (Web/PWA-Prototyp) inklusive Node-Tests -- siehe Begründung oben.

### Behoben / Fixed
- pikepdf-Quell-PDFs (und ihre Temp-Dateien) werden jetzt erst NACH `out_pdf.save()` geschlossen/aufgeräumt, nicht mehr davor -- verhinderte korrupte/fehlende OCR-Seiten bei lazy Page-Kopien.
- OCR-Fehler landen im Logging statt in `print()`; unter PyInstaller windowed (`sys.stdout is None`) hätte `print()` den Worker-Thread zum Absturz gebracht (GUI blieb mit dauerhaft deaktiviertem Start-Button hängen).
- Die Desktop-Dateiliste lässt sich jetzt auch per `Entf`-Taste bereinigen; Dateiliste und Löschaktion exponieren dafür klaren Accessible Context, ohne die kompakte Oberfläche sichtbar zu vergrößern.
- web_companion bugsweep (8 Bugs): `caches.match` ohne `{ignoreSearch: true}`, fehlendes `skipWaiting()` und `clients.claim()` im Service Worker, `escHtml` in `renderResults` (`entry.name`, `output.message`) und `buildStatCards` (`ocr_language`) fehlte, 4 Manifest-Icons (any+maskable 192/512 px) fehlten in `manifest.webmanifest`, `apple-touch-icon` fehlte, `exportCurrentState`-Anchor wurde nicht ins DOM eingehängt.
- Gleichnamige Quelldateien aus verschiedenen Ordnern kollidieren im Job-Export und Web-Companion nicht mehr; `outputs[].input_local_path` ordnet Status und Ausgabepfade jetzt eindeutig dem jeweiligen Input zu.
- BUG-W1: Service-Worker-`fetch` fängt jetzt Netzwerkfehler ab und liefert eine 503-Offline-Antwort statt einer ungefangenen Exception; Cache-Version auf v3 gebumpt.
- BUG-W2: `localStorage.setItem` in `persistState()` steht jetzt in try/catch, damit `QuotaExceededError` (z. B. Safari Private Browsing) den Aufrufer nicht crasht.
- `tests/test_platform_package_gate.py`: Der Synchronisationstest gegen `AUFGABEN.txt` (bewusst lokal/gitignored) wird jetzt per `pytest.mark.skipif` übersprungen, statt auf jedem Checkout ohne lokale Kopie fehlzuschlagen.

## [1.0.4] - 2026-05-01

### Hinzugefügt / Added
- Pytest-Abdeckung für portable Tesseract- und tessdata-Erkennung ergänzt.
- GitHub-Actions-Testworkflow für Python 3.10 bis 3.12 und `requirements-dev.txt` ergänzt.

### Behoben / Fixed
- Tesseract wird beim Start bevorzugt aus `TESSERACT_CMD`, dem portablen Runtime-Ordner oder `PATH` konfiguriert.
- `TESSDATA_PREFIX` wird für gebündelte Sprachpakete gesetzt, damit portable Builds ohne globale Tesseract-Installation funktionieren.
- Datenschutz-, Store- und Drittanbieter-Lizenzdateien an PySide6, optionale Sprachpaket-Downloads und den aktuellen EXE-Namen angepasst.

## [1.0.3] - 2026-05-01

### Behoben / Fixed
- Build-Script nutzt im isolierten venv konsequent `python -m pip`, damit Pip-Upgrades und Paketinstallationen den richtigen Interpreter verwenden.

### Geändert / Changed
- README mit Screenshot, `requirements.txt`-Installation und aktuellem Build-Workflow ergänzt
- `.gitignore` für lokale Secrets, Test-Locks und Build-venv erweitert; `PDFtoPDFocr.spec` bleibt als Build-Konfiguration trackbar
- PyInstaller-Spec an vorhandenes Root-Icon `ICO.ico` angepasst
- Migration von PyQt5 (GPL) zu PySide6 (LGPL) für MIT-Lizenzkompatibilität
- `app.exec_()` zu `app.exec()` (PySide6 API)
- `pyqtSignal` zu `Signal` (PySide6 API)

### Entfernt / Removed
- Katarakt-Funktionen entfernt (`get_katarakt_path`, `ensure_katarakt`) -- nicht verwendeter Dead Code

### Hinzugefügt / Added
- CODE_OF_CONDUCT.md, SECURITY.md, CONTRIBUTING.md (Community Health Files)
- CHANGELOG.md

## [1.0.2] - 2026-03-15

### Behoben / Fixed
- requirements.txt befüllt und .gitignore aktualisiert

## [1.0.1] - 2026-03-14

### Behoben / Fixed
- Bare-except-Blöcke durch spezifische Exception-Handler ersetzt
- Encoding-Probleme behoben
- Sicherheits- und Robustheitsverbesserungen

## [1.0.0] - 2026-03-13

### Hinzugefügt / Added
- Erstveröffentlichung / Initial release
- GUI zur OCR-Verarbeitung von PDF-Dateien
- Automatischer Download fehlender Tesseract-Sprachpakete
- Unterstützung für portables Tesseract und Poppler
- Mehrsprachige GUI (Deutsch/Englisch)
