# Windows Store Preparation Guide — PDFtoPDFocr

**Stand:** 2026-07-26  
**App-Name:** PDFtoPDFocr  
**Publisher:** `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`  
**Identity:** `Geiger.PDFtoPDFocr`  
**Version:** `1.0.4.0`  

---

## 1. Übersicht & Store-Voraussetzungen

Diese Vorleitung beschreibt den Ablauf für die Einreichung von **PDFtoPDFocr** im Microsoft Partner Center / Windows Store.

### Erforderliche Artefakte:

- [x] `store_package.json` — Paket- und Identitätsmetadaten
- [x] `STORE_LISTING.md` — Beschreibungstexte & Keywords (DE + EN)
- [x] `PRIVACY_POLICY.md` — Datenschutzerklärung (DE + EN)
- [x] `SUPPORT.md` — Supportkanäle & FAQ
- [x] `THIRD_PARTY_LICENSES.txt` — Lizenznachweise (PySide6, Tesseract, Poppler, etc.)
- [x] `store_assets/` — Store-Icons (Square44x44, Square150x150, Wide310x150, Square310x310, StoreLogo)
- [x] Preflight-Audit-Skript — `scripts/check_store_readiness.py`
- [x] Automated Tests — `tests/test_store_materials.py`

---

## 2. Preflight-Check ausführen

Vor jedem Build und Release die Store-Readiness durchführen:

```powershell
python scripts/check_store_readiness.py
```

Oder via Pytest:

```powershell
python -m pytest tests/test_store_materials.py
```

---

## 3. Build & Verpackung

1. **Executable bauen:**
   ```powershell
   python build_release.py
   ```

2. **MSIX-Paketierung:**
   Nutze das `msixpackager` Tool oder den Windows App Packager, um aus `dist/PDFtoPDFocr` ein signiertes MSIX-Paket zu erstellen.

3. **WACK Test (Windows App Certification Kit):**
   Erhöhten WACK-Lauf als Administrator ausführen und das Ergebnis im Protokoll festhalten.
