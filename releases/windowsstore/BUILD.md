# PDFtoPDFocr - Windows Store Build-Anleitung

## Voraussetzungen

1. Python 3.10+ mit PySide6
2. PyInstaller für den Desktop-Build
3. Windows SDK mit `makeappx.exe` und `appcert.exe` (WACK)
4. Lokaler Schreibpfad außerhalb eines synchronisierten Ordners für große MSIX-Artefakte, z. B. `C:\build\pdftopdfocr-store`

## Build-Schritte

1. PyInstaller Build ausführen:
   ```cmd
   build_exe.bat
   ```
2. MSIX-Paket erstellen:
   ```powershell
   makeappx.exe pack /d dist\PDFtoPDFocr /p releases\PDFtoPDFocr.msix
   ```
3. WACK-Prüfung ausführen:
   ```cmd
   appcert.exe test -appxpackagepath releases\PDFtoPDFocr.msix -reportoutputpath releases\windowsstore\test_reports\wack_report.xml
   ```
