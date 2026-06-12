# Portierungsplan - PDFtoPDFocr

Stand: 2026-06-12

## Kurzentscheidung

PDFtoPDFocr bleibt zuerst eine lokale Desktop-App für Windows, weil der Kernnutzen aus datenschutzfreundlicher Batch-OCR mit Tesseract, Poppler, PySide6 und lokalen PDF-Dateien entsteht. Die plattformübergreifende Erweiterung ist keine native Mobile-Voll-App, sondern ein Web/PWA-Companion für Job-Manifeste, mobile Vorprüfung und kleine Browser-Entwürfe über `pdftopdfocr-job-v1.json`.

## Feature-zu-Usecase-Ableitung

| Feature der besten Version | Wann braucht man das? | Usecase |
|---|---|---|
| Lokale Batch-OCR für mehrere PDFs | Gescannte Unterlagen sollen lokal durchsuchbar gemacht und archiviert werden | Desktop-OCR-Arbeitsplatz |
| Tesseract-/Poppler-/PySide6-Bündelung | Nutzer sollen ohne manuelle Systeminstallation arbeiten können | Windows-Store-Distribution |
| OCR-Sprache und Ergebnisstatus | Nutzer müssen Jobs reproduzierbar dokumentieren und Fehler nachverfolgen | Job-Protokoll und Wiederaufnahme |
| `pdftopdfocr-job-v1.json` ohne PDF-Inhalte | Ein Desktop-Job soll auf anderem Gerät geprüft oder vorbereitet werden, ohne Dokumente hochzuladen | Datei-Companion und mobiler Review |
| Web/PWA-Companion mit Offline-Import und Demo-Modus | Smartphone, Tablet oder Browser sollen kleine Job-Stände anzeigen, filtern und vorbereiten | Read-mostly Mobile/Web-Companion |
| Source-Platform-Smoke für Linux/macOS | Entwickler und Power-User sollen die Codebasis ohne eigene Desktop-Paketlinie prüfen können | Source-/CI-Portabilität |

## Usecase-Settings

### Setting 1: Desktop-OCR-Arbeitsplatz

Nutzer arbeiten mit lokalen PDFs, Tesseract/Poppler, Dateidialogen, Batch-Status und Ergebnisdateien. Dieses Setting braucht eine vollwertige Desktop-App. Windows ist die Referenzplattform und der erste Store-Kanal; macOS und Linux bleiben zunächst Source-/Smoke-Ziele derselben Codebasis.

### Setting 2: Mobiler oder browserbasierter Job-Review

Dieselben Nutzer wollen unterwegs oder auf einem zweiten Gerät Job-Stände ansehen, Sprache/Dateiliste prüfen, fehlende Eingaben erkennen und kleine Entwürfe exportieren. Dieses Setting braucht keinen nativen Mobile-Klon, sondern einen secrets- und PDF-freien Companion. Der Austausch ist dateibasiert über `pdftopdfocr-job-v1.json`; direkte Server-Synchronisierung ist aktuell kein Usecase.

## Plattformbewertung

| Plattform | Bewertung | Entscheidung |
|---|---|---|
| Windows Store | Sinnvoller Hauptkanal, weil die App lokale OCR-Runtime, Privacy-Framing und Ein-Klick-Installation braucht. Store-Artefakte sind vorhanden; offen bleiben aktuelle Screenshots, WACK/Testprotokoll und Quellcode-/Store-Konformität. | P0: Windows-Store-Pfad weiterführen |
| Web/PWA | Bereits als statischer Offline-Companion umgesetzt: Manifest-Import, Demo-Modus, Filteransicht, Browser-Entwurf und JSON-Export ohne PDF-Inhalte. | P1: Companion beibehalten und per Browser-/Mobile-Smokes härten |
| Android | Sinnvoll für Job-Vorprüfung, Kamera-/Dateiübergabe und Statusansicht; native OCR wäre hoher Runtime- und Wartungsaufwand. | P2: über PWA/Capacitor prüfen, keine native Voll-App starten |
| iOS | Gleicher Review-Usecase wie Android, aber mit stärkerem Sandbox-/Dateizugriffslimit. | P2: Safari-PWA und später optional Capacitor/TestFlight, keine native Voll-App |
| macOS | Fachlich plausibel für Desktop-Nutzer, aber Tesseract/Poppler-Bundling, Signierung und Notarisierung sind eigener Aufwand. | P3: Source-Smoke vorhanden; Paketierung erst nach Store/PWA-Stabilität |
| Linux | Technisch naheliegend für Power-User mit Systempaketen. | P3: Source-Smoke vorhanden; AppImage/Flatpak nur bei belegtem Bedarf |

## Zielarchitektur

1. Desktop bleibt autoritativ: PySide6-App, lokale OCR, Batch-Verarbeitung, portable Runtime.
2. `pdftopdfocr-job-v1.json` beschreibt Job-Einstellungen, Quellen-Metadaten, OCR-Sprache, Status und Ergebnis-Hinweise ohne PDF-Inhalte.
3. Web/PWA importiert und exportiert dasselbe Schema offline; LocalStorage und Manifest dürfen keine PDF-Inhalte speichern.
4. Android/iOS nutzen zunächst dieselbe PWA-Linie; Capacitor wird erst geprüft, wenn Kamera-/Datei-Smokes stabil sind.
5. macOS/Linux bleiben Source-/Smoke-Ziele aus derselben Codebasis, keine eigene Paketlinie vor belegtem Bedarf.

## Umsetzungsstatus

| Bereich | Status | Nächster Schritt |
|---|---|---|
| Desktop Windows | vorhanden; v1.0.4 privat released, Store-Basis vorhanden | aktuelle Store-Screenshots, EXE/MSIX und WACK/Testprotokoll erneuern |
| Exportformat | implementiert und dokumentiert | optionalen Desktop-Re-Import eines Job-Manifests bewerten |
| Web/PWA | Prototyp umgesetzt; Import, Filter, Demo, Browser-Entwurf, Export, Manifest und Service Worker vorhanden | Browser-Grenzen und echte Android-/iOS-PWA-Smokes dokumentieren |
| Android/iOS | über PWA-Testpfad geplant | Import, Suche/Filter, Dateiübergabe und Offline-Start auf echten Geräten prüfen |
| macOS/Linux | `source_platform_smoke.py` und GitHub-Actions-Matrix für Ubuntu/macOS vorhanden | CI-Ergebnisse beobachten; eigene Builds nur bei Nachfrage |
| Direkte Synchronisierung | nicht umgesetzt | Nicht-Ziel bis ein echter Mehrgeräte-Live-Usecase belegt ist |

## Nicht-Ziele

- Keine öffentliche Upload-Webapp für vertrauliche PDFs.
- Kein nativer Android-/iOS-Vollklon mit gebündelter OCR-Runtime.
- Keine direkte Server-Synchronisierung für PDF-Jobs ohne separate Datenschutz-, Konflikt- und Kostenstrategie.
- Keine macOS-/Linux-Paketlinie, solange Source-Smokes und Windows/PWA den Bedarf decken.

## Risiken

- Große PDFs sind im Browser speicher- und laufzeitkritisch.
- Native Mobile-OCR würde Tesseract/Poppler-Bündelung und Dateisystemlogik duplizieren.
- Store-Veröffentlichung braucht klare Quellcode-/Lizenzkommunikation und aktuelle Datenschutz-/Support-URLs.
- Lokale Pfade im Job-Manifest sind nur Hinweise und auf anderen Geräten nicht garantiert auflösbar.

## Priorisierte Aufgaben

1. DONE 2026-05-28: Desktop-Export `pdftopdfocr-job-v1.json` implementiert.
2. DONE 2026-06-02: Web/PWA-Companion als statischer Offline-Prototyp umgesetzt.
3. DONE 2026-06-04: Job-Manifest und Companion trennen gleichnamige Quelldateien über `outputs[].input_local_path`.
4. DONE 2026-06-07: Source-Platform-Smoke für Ubuntu/macOS ergänzt.
5. P0: Aktuelles Store-Screenshot-Set erstellen.
6. P0: Reproduzierbaren EXE-/MSIX-Buildpfad und WACK/Testprotokoll für den aktuellen Stand erneuern.
7. P2: Echte Android-/iOS-PWA-Smokes für Import, Filter/Suche, Dateiübergabe und Offline-Start durchführen.
8. P3: Optionalen Desktop-Re-Import und spätere Roundtrip-Strategie bewerten; bis dahin bleibt der Companion read-mostly.
