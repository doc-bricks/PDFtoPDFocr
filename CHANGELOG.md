# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- Pytest-Abdeckung für portable Tesseract- und tessdata-Erkennung ergänzt.
- GitHub-Actions-Testworkflow für Python 3.10 bis 3.12 ergänzt.

### Behoben / Fixed
- Tesseract wird beim Start bevorzugt aus `TESSERACT_CMD`, dem portablen Runtime-Ordner oder `PATH` konfiguriert.
- `TESSDATA_PREFIX` wird für gebündelte Sprachpakete gesetzt, damit portable Builds ohne globale Tesseract-Installation funktionieren.

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
