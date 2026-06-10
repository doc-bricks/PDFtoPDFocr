# PDFtoPDFocr Web/PWA Companion

Stand: 2026-06-02

Dieser Ordner enthält jetzt einen lauffähigen PWA-Prototyp für die Companion-Linie von PDFtoPDFocr. Er ersetzt die Desktop-App nicht, sondern ergänzt sie um eine mobile und browserbasierte Vorprüfung für `pdftopdfocr-job-v1.json`.

## Enthaltene Funktionen

- Offline-Import eines Desktop-Manifests `pdftopdfocr-job-v1.json`
- Demo-Modus für schnelle Browser- und Mobile-Smokes
- Filterbare Ergebnisansicht nach Status, Suche und fehlenden Eingabedateien
- Browser-Entwurf für kleine lokale Vorab-Jobs aus Dateinamen, Größen und OCR-Sprache
- Export des aktuellen Browser- oder Desktop-Stands zurück als JSON
- Service Worker und Web App Manifest für PWA-Tests auf Android, iOS und Desktop

## Start

Für einen lokalen Test reicht ein einfacher statischer Server, zum Beispiel:

```bash
python -m http.server 8768
```

Dann `http://127.0.0.1:8768/web_companion/` öffnen oder `?demo=1` anhängen.

## Tests

```bash
node --test web_companion/tests/library.test.mjs
node --check web_companion/app.js
node --check web_companion/library.js
```

## Grenzen der ersten Stufe

- Keine echte OCR im Browser
- Keine PDF-Inhalte im Manifest oder Local Storage
- Keine automatische Server-OCR und kein Datei-Upload
- Keine native Android- oder iOS-Codebasis

## Nächste sinnvolle Schritte

1. Browser-Grenzen für kleine PDF- und Bildmengen empirisch testen.
2. Optionalen Re-Import in die Desktop-App bewerten.
3. Android/iOS-PWA-Smoke mit Kamera-/Dateiworkflow dokumentieren.
