# Privacy Policy / Datenschutzhinweise

**PDFtoPDFocr** — implementation notes updated: 2026-10-12

---

## English

PDFtoPDFocr is a desktop application that processes selected PDFs and images with local OCR and PDF tools. The following describes the application behavior visible in the project source; it is not a guarantee that the operating system, installed tools, or the surrounding environment block all network traffic.

- **Document processing:** The GUI reads the selected source files for OCR and writes output PDFs to the configured destination. The application code does not provide a document-upload feature.
- **Language data request:** If Tesseract data for the selected language is missing, the application can send an HTTPS GET request to GitHub for the corresponding public traineddata file. GitHub receives the requested model URL/language and ordinary connection and HTTP request metadata, including the source IP address. The request does not contain the selected PDF or its OCR text. This policy does not make claims about GitHub's retention practices.
- **Local preferences:** The application stores the selected UI language and, when configured, the export folder in a JSON file under the user's platform configuration directory.
- **Job manifests:** An exported job manifest can include local file paths, language, status, messages, and output hints. It does not embed PDF bytes. Review a manifest before sharing it because paths and metadata may identify files or users.
- **Telemetry:** The reviewed GUI source does not define an analytics or telemetry client. This source-level observation does not cover third-party libraries, operating-system services, or separately installed tools.

The application does not provide a firewall or sandbox. Network access is not blocked by this program.

---

## Deutsch

PDFtoPDFocr ist eine Desktop-Anwendung, die ausgewählte PDFs und Bilder mit lokalen OCR- und PDF-Werkzeugen verarbeitet. Die folgenden Hinweise beschreiben das im Projektquellcode sichtbare Verhalten. Sie garantieren nicht, dass Betriebssystem, installierte Werkzeuge oder die übrige Umgebung sämtlichen Netzwerkverkehr sperren.

- **Dokumentverarbeitung:** Die GUI liest ausgewählte Quelldateien für die OCR und schreibt Ergebnis-PDFs in den konfigurierten Zielordner. Der Anwendungscode bietet keine Funktion zum Hochladen von Dokumenten.
- **Sprachdatenabruf:** Fehlen Tesseract-Daten für die ausgewählte Sprache, kann die Anwendung per HTTPS-GET die passende öffentliche traineddata-Datei von GitHub abrufen. GitHub erhält dabei die angefragte Modell-URL/Sprache sowie übliche Verbindungs- und HTTP-Metadaten einschließlich der Quell-IP-Adresse. Die Anfrage enthält weder das ausgewählte PDF noch dessen OCR-Text. Diese Hinweise treffen keine Aussage zu GitHubs Aufbewahrung dieser Daten.
- **Lokale Einstellungen:** Die Anwendung speichert die UI-Sprache und, falls festgelegt, den Exportordner in einer JSON-Datei im plattformspezifischen Benutzer-Konfigurationsordner.
- **Job-Manifeste:** Ein exportiertes Job-Manifest kann lokale Dateipfade, Sprache, Status, Meldungen und Ausgabehinweise enthalten. Es enthält keine PDF-Bytes. Prüfen Sie ein Manifest vor der Weitergabe, da Pfade und Metadaten Dateien oder Personen erkennen lassen können.
- **Telemetrie:** Der geprüfte GUI-Quellcode enthält keinen Analytics- oder Telemetrie-Client. Diese Beobachtung auf Quellcodeebene umfasst keine Drittanbieterbibliotheken, Betriebssystemdienste oder separat installierten Werkzeuge.

Die Anwendung stellt keine Firewall und keine Sandbox bereit. Dieses Programm sperrt den Netzwerkzugriff nicht.

---

*Publisher identity for the Windows package: Geiger | CN=52596601-BAB4-4F3F-B182-E8F3F273B202*
