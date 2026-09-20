# Windows Store — Vorbereitung PDFtoPDFocr

Stand: 2026-09-08

---

## Identität

| Feld              | Wert                                         |
|-------------------|----------------------------------------------|
| Identity Name     | Geiger.PDFtoPDFocr                           |
| Publisher         | CN=52596601-BAB4-4F3F-B182-E8F3F273B202      |
| Publisher Display | Geiger                                       |
| Version           | 1.1.4.0                                      |
| Executable        | PDFtoPDFocr.exe                              |
| Execution Alias   | pdftopdfocr.exe                              |

Publisher-Identität identisch mit dem Microsoft Partner Center Konto. Werte stimmen exakt mit `store_package.json` überein.

---

## Checkliste: Vor Store-Einreichung

### Pflichtartefakte

- [x] `store_package.json` erstellt & validiert (2026-09-08)
- [x] `STORE_LISTING.md` erstellt — DE + EN Beschreibung, max. 7 Keywords (2026-09-08)
- [x] `PRIVACY_POLICY.md` erstellt & erreichbar
- [x] `SUPPORT.md` erstellt — zweisprachig DE/EN mit FAQ
- [x] `THIRD_PARTY_LICENSES.txt` als Lizenzinventur gepflegt
- [x] Store-Tile-Icons in `store_assets/` (44x44, 50x50, 150x150, 310x150, 310x310) vollständig vorhanden
- [x] Store-Readiness-Gate `scripts/check_store_readiness.py` & Testsuite `tests/test_store_readiness.py`

### GitHub-Repository

- [x] Repository `doc-bricks/PDFtoPDFocr` erstellt und `origin` auf `https://github.com/doc-bricks/PDFtoPDFocr.git` verifiziert
- [x] Privacy-URL und Support-URL in `store_package.json` auf das GitHub-Repository verifiziert

### Paketierung & Freigabe

- [x] Windows-EXE gebaut (`releases/GitHub/v1.1.0/PDFtoPDFocr.exe` bzw. `build_release.py`)
- [x] Store-Preflight `python scripts\check_store_readiness.py` ausführen (Bestanden)
- [ ] MSIX-Paket erzeugen (MakeAppx / WinStorePackager)
- [ ] WACK-Test (Windows App Certification Kit) bestehen
- [ ] Paket im Microsoft Partner Center einreichen (Manuelle Nutzer-Freigabe)

---

## Technische Hinweise

### Capabilities

- `runFullTrust`: Erforderlich für lokalen Dateisystemzugriff und Ausführung des Tesseract-OCR-Subprozesses.
- `internetClient`: Erlaubt den optionalen automatischen Download fehlender Tesseract-Sprachpakete von GitHub.

### Kategorie

Productivity — entspricht dem Funktionsprofil (PDF-Verarbeitung, Texterkennung, Dokumentenorganisation).

### Altersfreigabe

3+ — keine Gewalt, keine jugendgefährdenden Inhalte, keine In-App-Käufe.

### Anforderungen

- Windows 10 Version 1903 (Build 18362) oder höher
- x64-Prozessor
- Mindestens 4 GB RAM empfohlen (für hochauflösende OCR-Scans)
- Ca. 200 MB freier Festplattenspeicher (inkl. Tesseract-Sprachmodelle)

---

## Verwandte Dateien

- `store_package.json` — maschinenlesbare Paket-Metadaten
- `STORE_LISTING.md` — Store-Beschreibung DE/EN
- `PRIVACY_POLICY.md` — Datenschutzerklärung
- `SUPPORT.md` — Support- und Hilfeseite
- `THIRD_PARTY_LICENSES.txt` — Lizenzinventur der Drittanbieterkomponenten
- `scripts/check_store_readiness.py` — Automatisierter Preflight-Prüfer
- `tests/test_store_readiness.py` — Pytest-Vertragstests für Store-Metadaten
