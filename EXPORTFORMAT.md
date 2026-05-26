# Exportformat - PDFtoPDFocr

Stand: 2026-05-26

## `pdftopdfocr-job-v1.json`

Dieses Format ist der geplante Vertrag zwischen Desktop-App und Web/PWA-Companion. Es enthält keine PDF-Inhalte, sondern nur Einstellungen, lokale Pfadreferenzen, Metadaten und Ergebnis-Hinweise.

## Ziele

- Desktop-Jobs später reproduzierbar beschreiben.
- Mobile Vorprüfung und Web/PWA-Companion ermöglichen.
- Datenschutz wahren, indem PDF-Dateien nicht ungefragt eingebettet oder hochgeladen werden.
- Versionierte Grundlage für Android-/iOS-Wrapper schaffen.

## Entwurf

```json
{
  "schema": "pdftopdfocr-job-v1",
  "app": "PDFtoPDFocr",
  "created_at": "2026-05-26T00:00:00Z",
  "ocr_language": "deu",
  "input_files": [
    {
      "name": "scan.pdf",
      "local_path": "C:/Users/User/Documents/scan.pdf",
      "size_bytes": 123456,
      "sha256": "optional"
    }
  ],
  "outputs": [
    {
      "input_name": "scan.pdf",
      "output_name": "scan_ocred.pdf",
      "status": "pending|success|failed",
      "message": ""
    }
  ],
  "settings": {
    "dpi": 300,
    "preserve_original": true,
    "download_missing_language_pack": true
  }
}
```

## Stabilitätsregeln

- `schema` bleibt für die v1-Linie exakt `pdftopdfocr-job-v1`.
- Neue Felder dürfen ergänzt werden, bestehende Felder behalten ihre Bedeutung.
- PDF-Dateien werden nicht als Base64 eingebettet.
- Mobile und Web-Clients müssen unbekannte Felder ignorieren.
- Lokale Pfade sind Hinweise für denselben Rechner und dürfen auf anderen Geräten fehlen.

## Offene Umsetzung

- Desktop-Menüpunkt für Job-Export ergänzen.
- Import eines Job-Manifests optional prüfen.
- PWA kann mit denselben Feldern kleine Browser-Jobs vorbereiten oder Ergebnislisten anzeigen.
