# macOS/Linux Package Gate - PDFtoPDFocr

Stand: 2026-07-03

## Entscheidung

Eigene macOS- oder Linux-Desktop-Pakete werden für PDFtoPDFocr aktuell nicht gestartet.

Der bestehende Cross-Platform-Nachweis bleibt der Source-Smoke aus `source_platform_smoke.py` und der CI-Matrix für Ubuntu/macOS. Das ist absichtlich enger als ein Release-Versprechen: Die App kann aus dem Source geprüft werden, aber es gibt noch keinen DMG-, PKG-, AppImage-, Flatpak-, Snap-, Deb- oder RPM-Releasepfad.

## Warum kein Paket jetzt

- Der Hauptkanal ist weiterhin Windows Store, weil die App dort lokale OCR-Runtime, Tesseract/Poppler-Bundling, Privacy-Framing und Ein-Klick-Installation verbindet.
- Die zweite Linie ist die Web/PWA-Companion-Prüfung über `pdftopdfocr-job-v1.json`, weil sie mobile Job-Vorprüfung ohne PDF-Upload abdeckt.
- macOS/Linux-Paketierung hätte eigene Risiken: Tesseract/Poppler-Bundling, Signierung/Notarisierung, Desktop-Dateien, AppImage/Flatpak-Entscheidung und Support-Matrix.
- Ohne stabile Windows-Store- und PWA-Evidenz würde ein weiterer Paketkanal die Pflegefläche vergrößern, ohne einen belegten Nutzerbedarf zu schließen.

## Auslösekriterien

Ein macOS- oder Linux-Paketpfad darf erst geöffnet werden, wenn mindestens eines dieser Kriterien belegt ist:

1. Windows-Store-Pfad ist auf aktuellem Stand: EXE/MSIX, Store-Screenshots, Store-Listing, Datenschutz-/Supportseiten und WACK/Testprotokoll sind erneuert oder als externe Blocker dokumentiert.
2. Web/PWA-Companion ist mobil geprüft: Import, Filter/Suche, Dateiübergabe, Offline-Start und Icon-/Manifest-Verhalten sind auf Android oder iOS belegt.
3. Es gibt konkrete Nachfrage nach macOS/Linux-Distribution jenseits von Source-Nutzung.
4. CI-Smokes auf Ubuntu/macOS schlagen wegen paketierungsrelevanter Annahmen fehl und lassen sich nicht sinnvoll im Source-Pfad lösen.

## Mindestumfang beim Öffnen des Gates

Wenn das Gate später geöffnet wird, muss der erste Paket-Slice klein bleiben:

- macOS: DMG/ZIP oder PKG eindeutig wählen, Tesseract/Poppler-Bundling festlegen, Signierung/Notarisierung als Gate dokumentieren.
- Linux: AppImage, Flatpak, Snap oder Tarball bewusst wählen; keine parallelen Paketformate im ersten Lauf.
- Für beide Plattformen: `source_platform_smoke.py` vorher grün, Paket-Smoke auf frischem Profil, SHA256SUMS, README/RELEASES-Doku und klare Nicht-Unterstützung nativer Mobile-OCR.

## Aktueller Status

Status 2026-07-03: geschlossenes Gate. Source-Smokes sind die Grenze der aktuellen macOS-/Linux-Unterstützung; eigene Pakete bleiben nach Windows-Store- und PWA-Stabilisierung zu bewerten.
