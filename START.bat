@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

if exist "dist\PDFtoPDFocr\PDFtoPDFocr.exe" (
    echo [INFO] Starte PDFtoPDFocr aus dist\PDFtoPDFocr\PDFtoPDFocr.exe...
    start "" "dist\PDFtoPDFocr\PDFtoPDFocr.exe"
    exit /b 0
)

if exist "dist\PDFtoPDFocr.exe" (
    echo [INFO] Starte PDFtoPDFocr aus dist\PDFtoPDFocr.exe...
    start "" "dist\PDFtoPDFocr.exe"
    exit /b 0
)

if exist "PDFtoPDFocr.exe" (
    echo [INFO] Starte PDFtoPDFocr aus PDFtoPDFocr.exe...
    start "" "PDFtoPDFocr.exe"
    exit /b 0
)

where py >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [INFO] Starte Python-Fallback via py -3 PDFtoPDFocr_2.py...
    py -3 "PDFtoPDFocr_2.py"
) else (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [FEHLER] Python wurde nicht gefunden.
        pause
        exit /b 1
    )
    echo [INFO] Starte Python-Fallback via python PDFtoPDFocr_2.py...
    python "PDFtoPDFocr_2.py"
)

if errorlevel 1 pause


