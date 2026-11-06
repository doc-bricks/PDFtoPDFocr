# PDFtoPDFocr - WACK-Protokoll

## Ziel

Nach dem lokalen MSIX-Build soll der Windows App Certification Kit (WACK)-Lauf dokumentiert werden, damit Store-Submission und spätere Regressionen nachvollziehbar bleiben.

## Vorbereiteter Befehl

```powershell
$projectRoot = "C:\_Local_DEV\repos\PDFtoPDFocr"
$reportRoot = Join-Path $projectRoot "releases\windowsstore\test_reports"
New-Item -ItemType Directory -Force -Path $reportRoot
& appcert.exe test -appxpackagepath "$projectRoot\releases\PDFtoPDFocr.msix" -reportoutputpath "$reportRoot\wack_report.xml"
```

## Kriterien
- Pass: Alle Plattformprüfungen erfolgreich
- Keine verbotenen APIs
- Saubere Manifest-Deklaration
