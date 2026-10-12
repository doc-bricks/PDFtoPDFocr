# Sicherheitsrichtlinie / Security Policy

## Deutsch

### Umfang und technisches Verhalten

PDFtoPDFocr verarbeitet ausgewählte PDFs und Bilder mit lokalen Bibliotheken und Werkzeugen wie Poppler, Tesseract und pikepdf. Der Anwendungscode kann fehlende Tesseract-Sprachdaten für die ausgewählte Sprache von GitHub abrufen. Das Programm stellt keine Firewall, Netzwerksperre oder Sandbox bereit.

Die Anwendung speichert die UI-Sprache und den Exportordner in einer Konfigurationsdatei im Benutzerprofil. Ein exportiertes Job-Manifest kann lokale Pfade, Sprache, Statusmeldungen und Ausgabehinweise enthalten; es enthält keine PDF-Bytes. Prüfen Sie ein Manifest, bevor Sie es weitergeben.

Der Ausgabepfad wird gegen Quelldateien und Dateialiasse geprüft. Für unterstützte OCR- und Merge-Schreibvorgänge werden Staging-Dateien verwendet und die geschriebene PDF-Seitenzahl vor der Veröffentlichung geprüft. Diese implementierten Prüfungen sind kein Schutz gegen andere Prozesse, Datenträgerfehler oder manuelle Änderungen.

Gestartete externe Prozesse erben die Berechtigungen des aufrufenden Prozesses. PDFtoPDFocr setzt keine Betriebssystem-Sandbox und senkt keine Berechtigungen herab. Die tatsächliche Netzwerk- und Zugriffssteuerung hängt daher von Betriebssystem, Installation und Umgebung ab.

### Unterstützte Versionen

| Version | Status |
| --- | --- |
| Quellstand master (1.1.4) | Maintainer nehmen Meldungen zu Sicherheitsproblemen entgegen. |

### Sicherheitslücken melden

Wenn Sie eine Sicherheitslücke oder ein Datenschutzproblem finden, melden Sie dies bitte vertraulich:

1. **GitHub Private Vulnerability Reporting**: Nutzen Sie das vertrauliche Formular unter [GitHub Security Advisories](https://github.com/doc-bricks/PDFtoPDFocr/security/advisories/new).
2. **E-Mail**: Schreiben Sie an [security@doc-bricks.org](mailto:security@doc-bricks.org), [security@open-bricks.org](mailto:security@open-bricks.org), [security@ellmos.ai](mailto:security@ellmos.ai), [support@lukasgeiger.com](mailto:support@lukasgeiger.com) oder [lukas@open-bricks.org](mailto:lukas@open-bricks.org) mit dem Betreff [SECURITY] PDFtoPDFocr Vulnerability Report.
3. **Reaktionsrichtlinie**: Die Maintainer nennen derzeit Zielzeiten von 48 Stunden für eine Eingangsbestätigung und 5 Werktagen für eine erste qualifizierte Triage. Dies beschreibt die Maintainer-Richtlinie, keine zugesicherte Softwarefunktion.
4. Beschreiben Sie Reproduktionsschritte, betroffene Plattformen und Versionen sowie das mögliche Bedrohungsszenario.
5. Veröffentlichen Sie technische Details möglichst nicht in öffentlichen Issues, bevor eine Behebung bereitsteht.

---

## English

### Scope and technical behavior

PDFtoPDFocr processes selected PDFs and images with local libraries and tools such as Poppler, Tesseract, and pikepdf. The application source can retrieve missing Tesseract language data for the selected language from GitHub. The program does not provide a firewall, network block, or sandbox.

The application stores the UI language and export-folder preference in a configuration file under the user's profile. An exported job manifest can contain local paths, language, status messages, and output hints; it does not contain PDF bytes. Review a manifest before sharing it.

The output-path resolver checks source files and file aliases before choosing a destination. Supported OCR and merge writes use staging files and verify the written PDF page count before publication. These implemented checks do not protect against other processes, storage failures, or manual changes.

Launched external processes inherit the permissions of the process that starts them. PDFtoPDFocr does not provide an operating-system sandbox or drop privileges. Actual network and access controls therefore depend on the operating system, installation, and environment.

### Supported versions

| Version | Status |
| --- | --- |
| Source line master (1.1.4) | Maintainers accept reports about security issues. |

### Reporting a vulnerability

If you discover a security or privacy issue, please report it confidentially:

1. **GitHub Private Vulnerability Reporting**: Use the confidential form at [GitHub Security Advisories](https://github.com/doc-bricks/PDFtoPDFocr/security/advisories/new).
2. **Email**: Contact [security@doc-bricks.org](mailto:security@doc-bricks.org), [security@open-bricks.org](mailto:security@open-bricks.org), [security@ellmos.ai](mailto:security@ellmos.ai), [support@lukasgeiger.com](mailto:support@lukasgeiger.com), or [lukas@open-bricks.org](mailto:lukas@open-bricks.org) with the subject [SECURITY] PDFtoPDFocr Vulnerability Report.
3. **Response policy**: Maintainers currently state target times of 48 hours for acknowledging reports and 5 business days for initial qualified triage. This describes maintainer policy, not a software feature.
4. Include reproduction steps, affected platforms and versions, and the potential threat scenario.
5. Please avoid publishing technical details in public issues before a fix is available.
