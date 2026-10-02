# Vollständige Seiten und sicheres Speichern

Stand: 2026-10-02. Version 1.1.4 bleibt unverändert.

PDFtoPDFocr veröffentlicht eine OCR-Ausgabe erst, wenn alle gerenderten
Quellseiten beziehungsweise Bildframes jeweils genau eine gültige OCR-PDF-Seite
ergeben haben. Bei PDFs muss die Anzahl gerenderter Seiten zur Quell-PDF passen.
Das fertig geschriebene OCR-/Merge-PDF wird vor der Veröffentlichung erneut
geöffnet und seine Seitenzahl geprüft.
Eine leere OCR-Antwort wird als Fehler behandelt; sie darf keine unvollständige
Ausgabe mit Erfolgsstatus erzeugen. OCR-Erkennungsgenauigkeit ist davon getrennt.

OCR-Ausgaben, Sammel-PDFs und Job-Manifeste werden vollständig in einem privaten
temporären Verzeichnis neben der Ausgabe vorbereitet. Die bisherigen Ausgabebytes
bleiben bei Schreib- oder Ersetzungsfehlern erhalten. Die temporären pikepdf-Quellen
und BytesIO-Puffer bleiben während des Speicherns offen und werden vor dem
Ersetzen geschlossen. Auch ein beschädigter OCR-Disk-Fallback bleibt innerhalb
des privaten Verzeichnisses und wird bereinigt.

Ein Bereinigungsfehler wird gesondert protokolliert. Er verdeckt keinen
Verarbeitungsfehler und macht einen bereits gespeicherten Export nicht rückgängig.
Ein Absturz oder Stromausfall garantiert keine Bereinigung. Es wird keine
Transaktion über die gesamte Batch-Verarbeitung behauptet.

## Sammel-PDF und anschließende Archivierung

Eine Sammel-PDF darf keine ihrer Eingaben ersetzen, auch nicht über einen
aufgelösten Pfad oder Hardlink. Nach erfolgreicher Veröffentlichung werden
Einzeldateien jeweils vollständig vorbereitet, ins Archiv übernommen und erst
dann am alten Ort entfernt. Bei einem Kopierfehler bleibt das Original erhalten;
bei einem Löschfehler bleiben Original und Archivkopie erhalten.

Die Archivierung mehrerer Einzeldateien ist keine gemeinsame Transaktion.
Bei einem späteren Archivierungsfehler kann die Sammel-PDF bereits gültig
gespeichert sein und ein Teil der Einzeldateien bereits im Archiv liegen. Die GUI
zeigt dies als Warnung zusätzlich zur gespeicherten Sammel-PDF an. API-Aufrufer
können `archive_warnings` übergeben; ohne diese Liste signalisiert
`MergeArchiveError.merged_path` das bereits veröffentlichte Ergebnis.

Manifestfehler werden im GUI-Slot abgefangen. Er zeigt einen Fehler und meldet
keinen Speicherefolg; das vorherige Manifest bleibt unverändert.

## Prüfung und Grenzen

`tests/test_save_safety.py` enthält 19 Verhaltenstests mit synthetischen PDFs,
kontrollierten OCR-Antworten sowie Schreib-, Veröffentlichungs-, Archivierungs-
und Bereinigungsfehlern. Die ursprünglichen sieben Gegenproben scheiterten am
unveränderten GitHub-Stand `a825ee1`. Die korrigierte Quellcode-Suite erreicht
163 bestandene Tests und eine dokumentierte Überspringung: Der lokale
Aufgabenabgleich benötigt die bewusst nicht versionierte `AUFGABEN.txt`.

Diese Tests belegen den geprüften Seiten-/Speichervertrag, keine allgemeine
OCR-Erkennungsqualität. Externe Pfadrennen, umfassender Stage-Austauschschutz,
globale Mehrdatei-Transaktionen, echte Geräte, Store-Zertifizierung und neue
EXE-Pakete sind nicht abgenommen. Benutzerdateien und persönliche Konfigurationen
wurden nicht als Testdaten verwendet.
