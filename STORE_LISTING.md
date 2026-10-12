# Store Listing Draft — PDFtoPDFocr

This file is a listing draft. Package contents depend on the specific Windows build; no Store submission is recorded here.

## Deutsch

### Kurzbeschreibung (max. 100 Zeichen)
Gescannte PDFs mit OCR durchsuchbar machen

### Beschreibung

PDFtoPDFocr wandelt gescannte PDF-Dateien und Bilder in durchsuchbare PDFs um. Die OCR nutzt Tesseract; PDF-Seiten werden mit den lokal verfügbaren PDF-Werkzeugen verarbeitet.

**Funktionen**
- Mehrere PDFs per Dateiauswahl oder Drag-and-drop zur Verarbeitung hinzufügen
- OCR-Sprache auswählen
- Fortschritt und Ergebnisstatus für jede Datei anzeigen
- Ergebnisdateien standardmäßig mit dem Suffix _ocred.pdf speichern
- Exportordner und Anzeigesprache konfigurieren
- In Builds mit gebündelten Werkzeugen kann die Anwendung portable Tesseract- und Poppler-Dateien verwenden

Die Anwendung verarbeitet ausgewählte Dokumente im lokalen OCR-Ablauf. Fehlen Tesseract-Sprachdaten für die ausgewählte Sprache, kann die Anwendung diese öffentliche Datei von GitHub herunterladen. Die Anwendung blockiert den Netzwerkzugriff nicht. Offline-Verarbeitung ist möglich, wenn die benötigten Werkzeuge und Sprachdaten bereits lokal vorhanden sind.

Für gescannte Dokumente, Briefe, Rechnungen, Formulare und Archivmaterial, die durchsuchbar gemacht werden sollen. Das Projekt steht unter der MIT-Lizenz; siehe LICENSE.

### Schlüsselwörter
PDF, OCR, Texterkennung, Scanner, Konverter, durchsuchbar, Tesseract

### Kategorie
Productivity

---

## English

### Short description (max. 100 characters)
Make scanned PDFs searchable with OCR

### Description

PDFtoPDFocr converts scanned PDFs and images into searchable PDFs. OCR uses Tesseract, and PDF pages are processed with locally available PDF tools.

**Features**
- Add multiple PDFs through a file picker or drag and drop
- Select an OCR language
- View per-file progress and result status
- Save output files with the _ocred.pdf suffix by default
- Configure the export folder and display language
- Builds that include the portable tools can use bundled Tesseract and Poppler files

The application processes selected documents in its local OCR workflow. If Tesseract data for the selected language is missing, the application can download that public file from GitHub. The application does not block network access. Offline processing is possible when the required tools and language data are already available locally.

For scanned documents, letters, invoices, forms, and archive material that need searchable text. The project is licensed under MIT; see LICENSE.

### Keywords
PDF, OCR, text recognition, scanner, converter, searchable, Tesseract

### Category
Productivity