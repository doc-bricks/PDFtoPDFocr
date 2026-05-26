# Portierungsplan - PDFtoPDFocr

Stand: 2026-05-26

## Kurzentscheidung

PDFtoPDFocr bleibt zuerst eine lokale Desktop-App für Windows, weil der Kernnutzen aus datenschutzfreundlicher Batch-OCR mit Tesseract, Poppler und lokalen PDF-Dateien entsteht. Die plattformübergreifende Erweiterung soll nicht als kompletter nativer Mobile-Clone starten, sondern als Web/PWA-Companion für kleine OCR-Jobs, Job-Manifeste und mobile Vorprüfung.

## Zweck und Nachfrage

Das Projekt richtet sich an Nutzer, die gescannte Verträge, Rechnungen, Briefe oder Formulare lokal in durchsuchbare PDFs umwandeln wollen. Der Bedarf ist hoch, weil solche Dokumente häufig mobil entstehen, aber später am Desktop archiviert, durchsucht oder weiterverarbeitet werden.

Wichtig sind dabei:

- Datenschutz: PDF-Dateien sollen standardmäßig lokal bleiben.
- Mobilität: Nutzer fotografieren oder erhalten Dokumente oft auf Smartphone oder Tablet.
- Archiv-Workflow: Ergebnisdateien müssen auf Desktop, NAS, Cloud-Ordner oder Dokumenten-Tools übertragbar sein.
- Einfache Distribution: Windows Store und später PWA senken die Einstiegshürde.

## Plattformbewertung

| Option | Bewertung | Entscheidung |
|---|---|---|
| Windows Store | Sehr sinnvoll: Kernplattform, vorhandenes MSIX, vorhandene Store-Artefakte. | P0: Store-Einreichung vorbereiten, öffentliches Repo und WACK/Testprotokoll abschließen. |
| Android | Sinnvoll für Scan- und Kurz-OCR-Workflows, aber native Tesseract/Poppler-Portierung wäre hoher Aufwand. | P2: zunächst über PWA/Capacitor prüfen, keine native Android-Codebasis starten. |
| Webapp | Sinnvoll als gemeinsame Linie für Web, Android und iOS; bei kleinen Dateien optional clientseitig. | P1/P2: Web/PWA-Companion planen, später prototypisieren. |
| iOS | Gleicher Bedarf wie Android, native Datei-/OCR-Integration aber aufwendig. | P2: über PWA testen, native App nur bei echter Nachfrage. |
| Mac App | Technisch möglich, aber Tesseract/Poppler-Bundling und Signierung erhöhen Aufwand. | P3: Source-/Build-Smoke-Test, keine eigene App-Linie vor Windows Store. |
| Linux Version | Technisch naheliegend durch Python/PySide6 und systemweite OCR-Pakete. | P3: Source-Smoke-Test und Installationshinweise, keine eigene Release-Linie vor Windows Store. |

## Zielarchitektur

1. Desktop bleibt autoritativ: PySide6-App, lokale OCR, Batch-Verarbeitung, portable Runtime.
2. Gemeinsames Austauschformat `pdftopdfocr-job-v1.json` beschreibt Job-Einstellungen, Quellen-Metadaten, Sprache, Status und Ergebnis-Hinweise ohne PDF-Inhalte.
3. Web/PWA-Companion startet als kleine Oberfläche für mobile Job-Vorbereitung und optional kleine clientseitige OCR-Tests.
4. Android/iOS nutzen dieselbe PWA-Linie; Capacitor wird erst geprüft, wenn Kamera-/Datei-Workflows stabil sind.
5. macOS/Linux bleiben Source-/Smoke-Ziele aus derselben Desktop-Codebasis.

## Umsetzungspfad

### P0 - Windows Store finalisieren

- Öffentliches GitHub-Repo oder Store-konforme Quellcode-Zugänglichkeit klären.
- Store-Screenshot-Set vervollständigen.
- WACK/Testprotokoll mit aktuellem Build durchführen.
- `STORE_LISTING.md`, `PRIVACY_POLICY.md` und `store_package.json` vor Einreichung final prüfen.

### P1 - Austauschformat stabilisieren

- `EXPORTFORMAT.md` als Vertrag für `pdftopdfocr-job-v1.json` pflegen.
- Desktop-Export für Job-Profil und letzte Ergebnisliste planen.
- Keine PDF-Inhalte in JSON schreiben; nur Metadaten und lokale Pfadreferenzen.

### P2 - Web/PWA-Companion

- `web_companion/` als Planungs- und späterer Prototypordner nutzen.
- PWA zuerst für kleine Dateien, Spracheinstellung, Job-Vorbereitung und Ergebnis-Check.
- Android/iOS als PWA-Testziele aufnehmen; Capacitor erst nach PWA-Smoke-Test.

### P3 - macOS/Linux

- Start- und Import-Smoke-Tests für PySide6, Tesseract und Poppler dokumentieren.
- macOS-Bundling und Linux-AppImage/Flatpak nur prüfen, wenn Windows Store und PWA stabil sind.

## Risiken

- Große PDFs sind im Browser speicher- und laufzeitkritisch.
- Native Mobile-OCR dupliziert viel Runtime- und Dateisystemarbeit.
- Store-Veröffentlichung braucht saubere Datenschutz- und Drittanbieter-Lizenzkommunikation, insbesondere für gebündelte Runtime-Komponenten.
- Das bestehende Projekt ist als privates Release geführt; Store-Einreichung erfordert vorab eine klare Veröffentlichungsentscheidung.

## Nächster konkreter Schritt

Als nächstes sollte der Desktop einen kleinen JSON-Export für Job-Voreinstellungen und Ergebnis-Metadaten erhalten. Das ist der günstigste Brückenschritt zu Web/PWA, ohne den OCR-Kern zu duplizieren.
