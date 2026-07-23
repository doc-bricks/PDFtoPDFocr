# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
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

### Behoben / Fixed
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
