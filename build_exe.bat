@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "PYTHONIOENCODING=utf-8"
set "PROJECT_NAME=PDFtoPDFocr"
set "PROJECT_ROOT=%CD%"
set "SPEC_FILE=%PROJECT_ROOT%\PDFtoPDFocr.spec"
set "BUILD_ROOT=C:\_Local_DEV\BUILDS\%PROJECT_NAME%\1.1.3"
set "DIST_DIR=%PROJECT_ROOT%\dist"

echo [INFO] Starte Build fuer %PROJECT_NAME%...

python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python wurde nicht gefunden.
    exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] PyInstaller fehlt. Bitte im Venv installieren.
    exit /b 1
)

if not exist "%BUILD_ROOT%" mkdir "%BUILD_ROOT%"
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

python -m PyInstaller --noconfirm --clean ^
    --workpath "%BUILD_ROOT%\build" ^
    --distpath "%BUILD_ROOT%\dist" ^
    --specpath "%BUILD_ROOT%" ^
    "%SPEC_FILE%"

if errorlevel 1 (
    echo [FEHLER] PyInstaller-Build fehlgeschlagen.
    exit /b 1
)

if exist "%BUILD_ROOT%\dist\%PROJECT_NAME%" (
    echo [INFO] Synchronisiere Dist-Artefakte...
    xcopy /E /I /Y "%BUILD_ROOT%\dist\%PROJECT_NAME%" "%DIST_DIR%\%PROJECT_NAME%" >nul
)

echo [OK] Build erfolgreich: %DIST_DIR%\%PROJECT_NAME%
endlocal
