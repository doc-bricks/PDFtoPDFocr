# Changelog / Aenderungsprotokoll

Alle wesentlichen Aenderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Geaendert / Changed
- Migration von PyQt5 (GPL) zu PySide6 (LGPL) fuer MIT-Lizenzkompatibilitaet
- `app.exec_()` zu `app.exec()` (PySide6 API)
- `pyqtSignal` zu `Signal` (PySide6 API)

### Entfernt / Removed
- Katarakt-Funktionen entfernt (`get_katarakt_path`, `ensure_katarakt`) -- nicht verwendeter Dead Code

### Hinzugefuegt / Added
- CODE_OF_CONDUCT.md, SECURITY.md, CONTRIBUTING.md (Community Health Files)
- CHANGELOG.md

## [1.0.2] - 2026-03-15

### Behoben / Fixed
- requirements.txt befuellt und .gitignore aktualisiert

## [1.0.1] - 2026-03-14

### Behoben / Fixed
- Bare-except-Bloecke durch spezifische Exception-Handler ersetzt
- Encoding-Probleme behoben
- Sicherheits- und Robustheitsverbesserungen

## [1.0.0] - 2026-03-13

### Hinzugefuegt / Added
- Erstveroeffentlichung / Initial release
- GUI zur OCR-Verarbeitung von PDF-Dateien
- Automatischer Download fehlender Tesseract-Sprachpakete
- Unterstuetzung fuer portables Tesseract und Poppler
- Mehrsprachige GUI (Deutsch/Englisch)
