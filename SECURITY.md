# Sicherheitsrichtlinie / Security Policy

## Deutsch

### Sicherheitsmodell & Invarianten

PDFtoPDFocr ist als lokales, datenschutzorientiertes Desktop-Werkzeug zur OCR-Texterkennung und Durchsuchbarmachung von PDF-Dokumenten und Bilddateien für Windows (sowie macOS/Linux aus Quellcode) konzipiert. Folgende Sicherheits- und Datenschutzprinzipien sind fest in der Architektur verankert:

1. **100% Lokale Verarbeitung & Zero-Egress für Dokumentendaten**: Sämtliche Dokumenten-, Bild- und OCR-Verarbeitungsoperationen (Seitenrasterisierung mit Poppler, OCR-Textextraktion mit Tesseract, PDF-Assemblierung mit pikepdf) finden zu 100% lokal auf dem Rechner des Benutzers statt. Es findet keinerlei Übertragung von Dokumenten, Dateinamen, extrahiertem Text oder Telemetriedaten an Cloud-Server statt.
2. **Kontrollierter Netzwerkzugriff (Nur Sprachpakete)**: Die Anwendung initiiert ausschließlich dann ausgehende HTTPS-Netzwerkverbindungen, wenn der Benutzer ein noch nicht lokal vorhandenes Tesseract-Sprachpaket auswählt und dieses von den offiziellen öffentlichen GitHub-Tesseract-Repositories geladen werden muss.
3. **Originaldatei-Schutz (Non-Destructive Processing)**: Originale Quelldokumente werden niemals verändert oder überschrieben. OCR-Ergebnisse werden stets als separate Dateien (Standard: Suffix `_ocred.pdf`) oder in einem explizit gewählten Zielverzeichnis gespeichert.
4. **Zustands- & Job-Manifest-Isolation**: Über die Job-Export-Funktion erstellte Manifeste (`pdftopdfocr-job-v1.json`) enthalten strukturierte Pfadreferenzen und Auftragsmetadaten. Es werden niemals rohe PDF-Binärdaten oder Base64-Inhalte in Manifesten abgelegt.
5. **Non-Elevation & Least Privilege**: PDFtoPDFocr läuft vollständig im Standard-Benutzerkontext und erfordert zu keinem Zeitpunkt Administrator- oder Root-Rechte.

### Unterstützte Versionen

| Version | Status |
| --- | --- |
| Aktueller `master` (1.1.3) | Unterstützt (Security Fixes & Updates) |

### Sicherheitslücken melden

Wenn Sie eine Sicherheitslücke oder ein Datenschutzproblem finden, melden Sie dies bitte verantwortungsvoll und vertraulich:

1. **GitHub Private Vulnerability Reporting**: Navigieren Sie zu `Security` -> `Advisories` -> `Report a vulnerability`.
2. **Direkte Sicherheits-E-Mail**: Schreiben Sie vertraulich an [security@ellmos.ai](mailto:security@ellmos.ai) mit dem Betreff `[SECURITY] PDFtoPDFocr Vulnerability Report`.
3. Beschreiben Sie Reproduktionsschritte, betroffene Plattformen/Versionen und das Bedrohungsszenario.
4. Bitte veröffentlichen Sie keine technischen Details in öffentlichen GitHub-Issues, bis eine Behebung bereitsteht.

---

## English

### Security Model & Invariants

PDFtoPDFocr is designed as a local-first, privacy-focused desktop application for OCR text recognition and searchable PDF creation on Windows (as well as macOS/Linux from source). The following core security and privacy invariants guide its design:

1. **100% Local Processing & Zero-Egress for Document Data**: All document, image, and OCR operations (page rasterization via Poppler, text extraction via Tesseract, PDF assembly via pikepdf) execute 100% locally on the user's machine. No documents, filenames, extracted text, or telemetry data are ever transmitted to remote servers or cloud services.
2. **Controlled Network Access (Language Packs Only)**: Network access is strictly restricted to downloading missing public Tesseract language data (`.traineddata`) from official GitHub repositories upon explicit user selection.
3. **Non-Destructive File Safety**: Source PDF and image files are never altered or overwritten. Output files are saved alongside the original with the `_ocred.pdf` suffix or in a configured output directory.
4. **Structured Manifest Isolation**: Exported job manifests (`pdftopdfocr-job-v1.json`) contain structured path references and job metadata without embedding raw binary document contents or Base64 payloads.
5. **Non-Elevation & Least Privilege**: PDFtoPDFocr runs entirely in standard user mode without requiring administrative elevation.

### Supported Versions

| Version | Status |
| --- | --- |
| Current `master` (1.1.3) | Supported (Security Fixes & Updates) |

### Reporting a Vulnerability

If you discover a potential vulnerability or security issue, please report it responsibly and confidentially:

1. **GitHub Private Vulnerability Reporting**: Go to `Security` -> `Advisories` -> `Report a vulnerability`.
2. **Direct Security Email**: Send details confidentially to [security@ellmos.ai](mailto:security@ellmos.ai) with subject `[SECURITY] PDFtoPDFocr Vulnerability Report`.
3. Include clear reproduction steps, affected environment/version, and an impact assessment.
4. Please do not publish exploit details in public issues before a patch is available.
