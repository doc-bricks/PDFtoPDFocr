# Support — PDFtoPDFocr

## Deutsch

### Kontakt

Bei Fragen, Fehlermeldungen oder Verbesserungsvorschlägen:

- **GitHub Issues** (bevorzugt): https://github.com/doc-bricks/PDFtoPDFocr/issues
- **E-Mail**: lukasgeiger@googlemail.com

### Häufige Fragen

**Die Anwendung startet nicht.**
Stellen Sie sicher, dass Ihr System Windows 10/11 (64-bit) verwendet.
Prüfen Sie, ob das Microsoft Visual C++ Redistributable installiert ist.

**OCR liefert ungenaue oder unvollständige Ergebnisse.**
Stellen Sie sicher, dass das gescannte PDF eine Auflösung von mindestens 300 DPI besitzt.
Dokumente mit starkem Bildrauschen, schiefen Zeilen oder geringem Kontrast können die Erkennungsrate verringern.

**Wie installiere ich zusätzliche OCR-Sprachen?**
Die Anwendung lädt fehlende Tesseract-Traineddata-Dateien bei aktiver Internetverbindung automatisch von GitHub nach.
Alternativ können `.traineddata`-Dateien manuell in den Ordner `tessdata/` im Anwendungsverzeichnis abgelegt werden.

**Funktioniert die Anwendung offline?**
Ja. Sobald die gewünschten Sprachpakete vorhanden sind, läuft die gesamte Texterkennung vollständig lokal ohne Internetverbindung ab. Es werden keine Daten an externe Server übertragen.

**Was geschieht mit meinen Originaldateien?**
Ihre Originaldateien bleiben unberührt. Die durchsuchbare PDF-Datei wird standardmäßig als neue Datei mit dem Suffix `_ocred.pdf` im gewählten Ausgabeordner gespeichert.

### Versionsverlauf

Siehe `CHANGELOG.md` im Projektverzeichnis.

---

## English

### Contact

For questions, bug reports, or suggestions:

- **GitHub Issues** (preferred): https://github.com/doc-bricks/PDFtoPDFocr/issues
- **Email**: lukasgeiger@googlemail.com

### Frequently Asked Questions

**The application does not start.**
Ensure that your system runs Windows 10/11 (64-bit).
Verify that the Microsoft Visual C++ Redistributable is installed.

**OCR produces inaccurate or incomplete results.**
Ensure that the scanned document has a resolution of at least 300 DPI.
Images with heavy noise, skewed text, or low contrast can reduce recognition accuracy.

**How do I install additional OCR languages?**
The application automatically downloads missing Tesseract traineddata packages from GitHub when connected to the internet.
Alternatively, `.traineddata` files can be placed manually into the `tessdata/` folder in the application directory.

**Does the application work offline?**
Yes. Once the required language packages are downloaded, all OCR recognition runs completely locally without requiring an internet connection. No document data leaves your computer.

**What happens to my original files?**
Your original files remain untouched. The searchable PDF is saved as a new file with the suffix `_ocred.pdf` in the designated output folder.

### Version History

See `CHANGELOG.md` in the project directory.
