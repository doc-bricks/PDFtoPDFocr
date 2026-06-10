# Exportformat - PDFtoPDFocr

Stand: 2026-06-02

## `pdftopdfocr-job-v1.json`

Dieses Format ist der Vertrag zwischen Desktop-App und Web/PWA-Companion. Es enthält keine PDF-Inhalte, sondern nur Einstellungen, lokale Pfadreferenzen, Metadaten und Ergebnis-Hinweise.

## Ziele

- Desktop-Jobs später reproduzierbar beschreiben.
- Mobile Vorprüfung und Web/PWA-Companion ermöglichen.
- Datenschutz wahren, indem PDF-Dateien nicht ungefragt eingebettet oder hochgeladen werden.
- Versionierte Grundlage für Android-/iOS-Wrapper schaffen.

## Aktueller Stand

- Desktop-Export ist in der App als Button `Job-Export` umgesetzt.
- Die JSON-Datei wird als UTF-8 ohne BOM geschrieben.
- Fehlende Dateien bleiben im Manifest sichtbar (`missing: true`), statt den Export abzubrechen.
- `web_companion/` liest das Format jetzt offline ein, filtert Status und kann Browser-Entwürfe im selben Schema exportieren.

## Schema

```json
{
  "schema": "pdftopdfocr-job-v1",
  "app": "PDFtoPDFocr",
  "app_version": "1.0.4",
  "created_at": "2026-05-28T00:00:00Z",
  "ocr_language": "deu",
  "input_files": [
    {
      "name": "scan.pdf",
      "local_path": "C:/Users/User/Documents/scan.pdf",
      "size_bytes": 123456,
      "missing": false
    }
  ],
  "outputs": [
    {
      "input_name": "scan.pdf",
      "input_local_path": "C:/Users/User/Documents/scan.pdf",
      "output_name": "scan_ocred.pdf",
      "status": "pending|success|failed",
      "message": "",
      "output_local_path": "C:/Users/User/Documents/scan_ocred.pdf",
      "output_exists": false
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
- `outputs[].input_local_path` darf zur eindeutigen Zuordnung gleichnamiger Dateien ergänzt werden.
- PDF-Dateien werden nicht als Base64 eingebettet.
- Mobile und Web-Clients müssen unbekannte Felder ignorieren.
- Lokale Pfade sind Hinweise für denselben Rechner und dürfen auf anderen Geräten fehlen.
- Fehlende Eingabedateien werden mit `missing: true` und `size_bytes: null` exportiert.

## Companion-Stand 2026-06-02

- Der Web/PWA-Companion zeigt OCR-Sprache, Status, fehlende Dateien und Ergebnis-Hinweise filterbar an.
- Browser-Dateien können als Entwurf mit Name und Größe in dasselbe Schema geschrieben werden.
- Im Browser bleiben PDF-Inhalte weiterhin ausgeschlossen; nur Metadaten und Job-Hinweise werden verwendet.

## Nächste sinnvolle Schritte

- Optionalen Desktop-Re-Import eines Job-Manifests prüfen.
- Browser-Grenzen für kleine PDF-/Bildmengen empirisch dokumentieren.
