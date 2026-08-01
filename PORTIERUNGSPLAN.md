# Portierungsplan - PDFtoPDFocr

Stand: 2026-08-01

## Kurzentscheidung

PDFtoPDFocr bleibt eine lokale Desktop-App. Windows ist die Referenz- und Store-Linie; macOS und Linux bleiben Source-/Smoke-Ziele derselben Codebasis. Web/PWA, Android, iOS, native Mobile-Apps und direkte Synchronisierung sind nach dem Usecase-Audit vom 2026-07-23/24 keine aktiven Produktlinien mehr.

Der frühere `web_companion/`-Ansatz wurde bewusst entfernt. Er darf durch Icon-, i18n-, Transfer- oder Plattform-Automationen nicht wieder aufgebaut werden, solange kein neuer konkreter Nutzer-Usecase dokumentiert ist.

## Feature-zu-Usecase-Ableitung

| Feature der besten Version | Wann braucht man das? | Usecase |
|---|---|---|
| Lokale Batch-OCR für PDFs und Bilder | Gescannte Unterlagen sollen lokal durchsuchbar gemacht, sortiert, gemergt und archiviert werden | Desktop-OCR-Arbeitsplatz |
| Drag&Drop für Dateien und Ordner | Nutzer wollen viele Einzelbilder oder PDFs ohne manuelle Einzelauswahl verarbeiten | Schneller Desktop-Import |
| Stapeln und "Markierte mergen" | OCR-Ergebnisse sollen in einer gewünschten Reihenfolge zu einem Sammel-PDF zusammengeführt werden | Desktop-Nachbearbeitung |
| Konfigurierbarer Exportordner | Ergebnisse sollen wahlweise neben der Quelle oder an einem festen Zielort landen | Lokale Ablagekontrolle |
| Tesseract-/Poppler-/PySide6-Bündelung | Nutzer sollen ohne manuelle Systeminstallation arbeiten können | Windows-Store-Distribution |
| OCR-Sprache, Status und Job-Export | Nutzer oder Agenten sollen Verarbeitungseinstellungen und Ergebnis-Hinweise nachvollziehen können | Lokales Protokoll und Automationsvertrag |
| Source-Platform-Smoke für macOS/Linux | Entwickler und Power-User sollen prüfen können, ob die Codebasis ohne Windows-only-Annahmen importierbar bleibt | Source-/CI-Portabilität |

## Usecase-Settings

### Setting 1: Desktop-OCR-Arbeitsplatz

Die Nutzer arbeiten mit vertraulichen lokalen PDFs/Bildern, Tesseract/Poppler, Dateidialogen, Batch-Status, Exportordnern und erzeugten Ergebnisdateien. Dieses Setting braucht eine vollwertige Desktop-App. Windows bleibt die Referenzplattform und der erste Store-Kanal.

### Setting 2: Entwickler-/Power-User-Source-Prüfung

Entwickler oder technisch starke Nutzer prüfen die Codebasis auf macOS/Linux aus dem Source. Das ist ein Prüf- und Beitragssetting, keine eigene Endnutzer-Paketlinie. Die Grenze bleibt `source_platform_smoke.py` plus CI-Matrix, bis konkrete Nachfrage nach DMG/PKG/AppImage/Flatpak/Snap/Deb/RPM vorliegt.

## Plattformbewertung

| Plattform | Bewertung | Entscheidung |
|---|---|---|
| Windows Store | Sinnvoller Hauptkanal, weil die App lokale OCR-Runtime, Privacy-Framing, One-click-Installation und Store-Assets verbindet. Offen bleiben aktueller Build, Store-Screenshot, WACK/Testprotokoll und Quellcode-/Store-Konformität. | P0: Windows-Store-Pfad weiterführen |
| Windows Direct/GitHub privat | Bereits reale Arbeitslinie für Entwicklung, Tests und private Distribution. | Beibehalten |
| macOS | Fachlich plausibel für Source-Nutzer, aber Tesseract/Poppler-Bundling, Signierung und Notarisierung sind eigener Release-Aufwand. | P3: Source-Smoke, kein Paket |
| Linux | Technisch plausibel für Power-User mit Systempaketen. | P3: Source-Smoke, kein Paket |
| Web/PWA | Entfernt. Reine Job-Manifest-Vorprüfung ohne PDF-Inhalt hat keinen tragenden Aktionsnutzen. | Nicht-Ziel |
| Android | Keine eigenständige OCR-Voll-App und keine PWA-Linie. Normale Dateiwege wie Cloud-Ordner, USB, Mail-Anhang oder Geräte-Import bleiben Nutzerentscheidung außerhalb der App. | Nicht-Ziel |
| iOS | Gleiche Bewertung wie Android; zusätzliche Sandbox-Grenzen verstärken den Nicht-Ziel-Status. | Nicht-Ziel |

## Zielarchitektur

1. Desktop bleibt autoritativ: PySide6-App, lokale OCR, Datei-/Ordnerimport, Batch-Verarbeitung, Merge und portable Runtime.
2. `pdftopdfocr-job-v1.json` bleibt ein lokaler Desktop-Export für Einstellungen, Quellen-Metadaten, OCR-Sprache, Status und Ergebnis-Hinweise ohne PDF-Inhalte.
3. Keine App-eigene Geräte-Synchronisierung und kein Server. Dateiaustausch bleibt bewusste Nutzerhandlung außerhalb der App.
4. macOS/Linux bleiben Source-/Smoke-Ziele aus derselben Codebasis, keine eigene Paketlinie vor belegtem Bedarf.
5. Entfernte Web-/Mobile-Dateien werden nicht rekonstruiert; Altverweise bleiben nur als Historie oder als ENTFERNT-Entscheidung zulässig.

## Umsetzungsstatus

| Bereich | Status | Nächster Schritt |
|---|---|---|
| Desktop Windows | vorhanden; v1.0.4 privat released, v1.1.x-Funktionsstand im Git-Verlauf, Store-Basis vorhanden | aktuellen EXE-/MSIX-Build, Store-Screenshot und WACK/Testprotokoll erneuern |
| Bild-/Ordnerimport und Merge | Welle-1-Features umgesetzt und dokumentiert | Store-/Build-Readback für den aktuellen Stand erstellen |
| Exportformat | implementiert und dokumentiert | als lokales Protokoll führen; kein Companion-Roundtrip |
| Web/PWA | ENTFERNT 2026-07-23/24 | nicht wieder anlegen; Altverweise nur bereinigen |
| Android/iOS | keine Produktlinie | keine PWA-/Capacitor-/native Mobile-Aufgaben starten |
| macOS/Linux | `source_platform_smoke.py`, GitHub-Actions-Matrix für Ubuntu/macOS und `MACOS_LINUX_PACKAGE_GATE.md` vorhanden | CI-/Smoke-Ergebnisse beobachten; Paket-Gate nur bei Nachfrage öffnen |
| Direkte Synchronisierung | nicht umgesetzt | Nicht-Ziel |

## Nicht-Ziele

- Keine öffentliche Upload-Webapp für vertrauliche PDFs.
- Kein Web/PWA-Companion für Job-Manifeste.
- Keine native Android-/iOS-Voll-App mit OCR-Runtime.
- Keine App-eigene direkte Server- oder Geräte-Synchronisierung.
- Keine macOS-/Linux-Paketlinie, solange Source-Smokes und Windows den belegten Bedarf decken.

## Risiken

- Store-Veröffentlichung braucht klare Quellcode-/Lizenzkommunikation, aktuelle Datenschutz-/Support-URLs, Build-Provenienz und WACK-Evidenz.
- Native Mobile-OCR würde Tesseract/Poppler-Bündelung und Dateisystemlogik duplizieren, ohne aktuellen Usecase.
- Web/PWA ohne PDF-Verarbeitung erzeugt nur Status-/Vorschauflächen und war laut Audit kein tragender Alltagsnutzen.
- macOS-/Linux-Paketierung hätte eigene Wartungsrisiken: Runtime-Bundling, Signierung/Notarisierung, Desktop-Dateien und Support-Matrix.

## Priorisierte Aufgaben

1. DONE 2026-05-28: Desktop-Export `pdftopdfocr-job-v1.json` implementiert.
2. DONE 2026-07-24: Welle-1-Features für Bildimport, Ordnerimport, Merge/Stapelung, Exportordner, Sprache und Paket-Hygiene umgesetzt.
3. DONE 2026-07-24: `web_companion/` entfernt; Companion/PWA/Mobile-Review ist kein aktiver Usecase mehr.
4. P0: Aktuellen EXE-/MSIX-Buildpfad und WACK/Testprotokoll für den aktuellen Stand erneuern.
5. P0: Ein aktuelles, privacy-sicheres Store-Screenshot-Set aus dem aktuellen Desktop-Stand erstellen.
6. P0: Store-Quellcode-, Lizenz-, Publisher- und Supportpfad final entscheiden.
7. P2: Source-Smoke-/CI-Grenze für macOS/Linux beobachten; Paket-Gate nur bei Nachfrage öffnen.
8. P3: Desktop-Re-Import von Job-Manifesten nur separat bewerten, wenn ein realer Desktop-Automationsnutzen belegt wird; nicht als Companion-Roundtrip.

## Nachtrag 2026-07-24 - Companion-Rückbau

ENTFERNT: `web_companion/` - "Job-Manifeste mobil vorprüfen" ohne PDF-Inhalt ist kein tragender Alltagsmoment und kein ausreichender Aktionsnutzen. PDFtoPDFocr bleibt Desktop-only. Archivkopie: `C:\_Local_DEV\companion_removals_20260723\RDY_PDFtoPDFocr\`.

## Nachtrag 2026-08-01 - SNW-Recheck

Der Hauptplan wurde an den ENTFERNT-Vermerk angepasst. Frühere PWA-, Android-/iOS-PWA-Smoke- und read-mostly-Companion-Aufgaben sind geschlossen bzw. ersetzt durch Desktop-/Store- und Source-Smoke-Gates. Entfernte Companion-Dateien werden nicht neu angelegt.
