# Releases

## v1.1.0 - 2026-07-24

Welle-1-Usertest-Feature-Paket: Bild-Import (U1), Stapeln/Mergen (U2/U3),
Exportordner-Einstellung (U4), automatischer Ordner-Merge (U5) und
Paket-Hygiene für `tesseract_portable` (U7). Details: `CHANGELOG.md`.

### GitHub

- Repository: [doc-bricks/PDFtoPDFocr](https://github.com/doc-bricks/PDFtoPDFocr)
- Tag: `v1.1.0`
- Type: private Windows desktop release

### Local release artifacts

- `releases/GitHub/v1.1.0/PDFtoPDFocr-1.1.0-desktop.exe`
- `releases/GitHub/v1.1.0/PDFtoPDFocr-1.1.0-desktop.zip`
- `releases/GitHub/v1.1.0/PDFtoPDFocr-1.1.0-source.zip`
- `releases/GitHub/v1.1.0/CHANGELOG.md`
- `releases/GitHub/v1.1.0/SHA256SUMS.txt`

### Notes

- Funktional verifiziert mit dem gebündelten `tesseract_portable\tesseract.exe`
  (echter OCR-Lauf auf einem Testbild, Text-Layer im Ergebnis-PDF bestätigt).
- Start-Smoke: die gebaute EXE öffnet ihr Hauptfenster ("PDF OCR Werkzeug")
  ohne Absturz.
- U7-Ausschlussliste verifiziert: Trainingstools/Deinstaller fehlen im
  gebauten Paket (`dist/PDFtoPDFocr/_internal/tesseract_portable/`),
  Laufzeit-Binaries (tesseract.exe, libtesseract-5.dll, libleptonica-6.dll,
  Sprachpakete) sind vorhanden.

## v1.0.4 - 2026-05-01

### GitHub

- Repository: [doc-bricks/PDFtoPDFocr](https://github.com/doc-bricks/PDFtoPDFocr)
- Tag: `v1.0.4`
- Type: private Windows desktop release

### Local release artifacts

- `releases/GitHub/v1.0.4/PDFtoPDFocr-1.0.4-desktop.exe`
- `releases/GitHub/v1.0.4/PDFtoPDFocr-1.0.4-desktop.zip`
- `releases/GitHub/v1.0.4/PDFtoPDFocr-1.0.4-source.zip`
- `releases/GitHub/v1.0.4/CHANGELOG.md`
- `releases/GitHub/v1.0.4/SHA256SUMS.txt`

### Notes

- The Windows build is produced from `PDFtoPDFocr.spec` via `build_release.py`.
- The desktop ZIP contains the packaged application directory for portable local use.
- The source archive is created from the current working tree so the local release bundle matches the current repository state.
- Local release artifacts stay ignored by Git and are listed here only as the expected release layout.
