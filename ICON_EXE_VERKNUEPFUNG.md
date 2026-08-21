# Anleitung: Icon- und EXE-Verknüpfung (Windows / PyInstaller)

Diese Dokumentation beschreibt die verbindlichen Verfahren und Best Practices zur Verknüpfung von Anwendungs-Icons (`.ico`) mit ausführbaren Windows-Dateien (`.exe`), dem PyInstaller-Build-Prozess, der Windows-Shell und Startskripten (`START.bat`).

---

## 1. Icon-Asset-Anforderungen

Für eine saubere Darstellung im Windows Explorer, auf dem Desktop, in der Taskleiste und im Alt-Tab-Dialog muss das Master-Icon als Windows-Icon-Container (`.ico`) mit mehreren Auflösungsebenen vorliegen:

| Auflösung | Farbtiefe | Verwendungszweck |
| :--- | :--- | :--- |
| **256 × 256** | 32-Bit RGBA | Große Kacheln, High-DPI Displays, Windows Explorer Extra-Große Symbole |
| **128 × 128** | 32-Bit RGBA | Mittlere/Große Kacheln, Windows Suche |
| **64 × 64** | 32-Bit RGBA | Windows Explorer Große Symbole |
| **48 × 48** | 32-Bit RGBA | Desktop-Standardansicht, Windows Explorer Kachelansicht |
| **32 × 32** | 32-Bit RGBA | Startmenü, Taskleiste (Standard-DPI), Explorer Listenansicht |
| **24 × 24** | 32-Bit RGBA | Taskleiste (Kompaktmodus), Toolbars |
| **16 × 16** | 32-Bit RGBA | Titelleiste (Fenster), Infobereich (System Tray), Explorer Detailansicht |

> **Wichtig:** Reine Single-Resolution-ICOs (z. B. nur 32x32 oder nur 256x256) führen zu unscharfem Downsampling oder Skalierungsartefakten im Explorer.

---

## 2. Einbindung in PyInstaller (`.spec` & CLI)

PyInstaller bettet das Icon während des Linkens als Windows PE-Ressource (`RT_GROUP_ICON`, Ressourcen-ID `1` bzw. `IDI_ICON1`) direkt in den Header der Binärdatei ein.

### 2.1 In der Spec-Datei (`PDFtoPDFocr.spec`)

Im `EXE(...)`-Block der `.spec`-Datei wird das Icon über den Parameter `icon` deklariert:

```python
# 1. Icon-Pfad auflösen
if os.path.exists('PDFtoPDFocr.ico'):
    icon_path = 'PDFtoPDFocr.ico'
elif os.path.exists('assets/icon.ico'):
    icon_path = 'assets/icon.ico'
else:
    icon_path = None

# 2. EXE-Konfiguration mit Icon-Verknüpfung
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDFtoPDFocr',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=icon_path,  # <--- Bindet das Icon in die EXE-Ressourcen ein
)
```

### 2.2 Bundling für die Laufzeit (`datas`)

Damit die GUI-Engine (PySide6 / Qt) das Icon auch zur Laufzeit aus dem Anwendungsordner bzw. `sys._MEIPASS` laden kann, wird das Icon in die `datas`-Liste des `Analysis`-Blocks aufgenommen:

```python
datas = [
    ('translations.json', '.'),
    ('assets', 'assets'),
    ('PDFtoPDFocr.ico', '.'),
    ('ICO.ico', '.'),
]
```

---

## 3. Laufzeit-Zuweisung in PySide6 / Python

Das in der EXE eingebettete PE-Ressourcen-Icon wird vom Windows Explorer für die Dateidarstellung genutzt. Sobald die Anwendung gestartet wird, muss das Fenster-Icon im UI-Thread an das Qt-Fenster und die Applikations-Instanz übergeben werden:

```python
from pathlib import Path
import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow

def get_project_root() -> Path:
    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent

def get_app_icon() -> QIcon:
    root = get_project_root()
    for candidate in [root / "PDFtoPDFocr.ico", root / "assets" / "icon.ico", root / "assets" / "icon.png"]:
        if candidate.exists():
            return QIcon(str(candidate))
    return QIcon()

# In main()
app = QApplication(sys.argv)
app.setWindowIcon(get_app_icon())  # Setzt globales App-Icon (Taskleiste & Dialoge)

window = QMainWindow()
window.setWindowIcon(get_app_icon())  # Setzt Fenster-Icon (Titelleiste)
```

---

## 4. Standardisiertes Startskript (`START.bat`)

Um Benutzern den Start unabhängig von einer installierten Python-Umgebung oder einer gebauten EXE zu ermöglichen, priorisiert `START.bat` vorkompilierte Binaries und fällt bei Bedarf transparent auf Python zurück:

```bat
@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 1. Bevorzugt kompilierte Onedir-EXE im dist-Ordner
if exist "dist\PDFtoPDFocr\PDFtoPDFocr.exe" (
    echo [INFO] Starte PDFtoPDFocr (dist\PDFtoPDFocr\PDFtoPDFocr.exe)...
    start "" "dist\PDFtoPDFocr\PDFtoPDFocr.exe"
    exit /b 0
)

REM 2. Standalone-EXE im dist-Ordner
if exist "dist\PDFtoPDFocr.exe" (
    echo [INFO] Starte PDFtoPDFocr (dist\PDFtoPDFocr.exe)...
    start "" "dist\PDFtoPDFocr.exe"
    exit /b 0
)

REM 3. Root-EXE
if exist "PDFtoPDFocr.exe" (
    echo [INFO] Starte PDFtoPDFocr (PDFtoPDFocr.exe)...
    start "" "PDFtoPDFocr.exe"
    exit /b 0
)

REM 4. Python-Interpreter Fallback (py -3 oder python)
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
```

---

## 5. Desktop- & Startmenü-Verknüpfungen (.lnk) mit Icon

Zur Erzeugung von Windows-Desktopverknüpfungen mit expliziter Icon-Zuweisung kann folgendes PowerShell-Kommando verwendet werden:

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$([Environment]::GetFolderPath('Desktop'))\PDFtoPDFocr.lnk")
$Shortcut.TargetPath = "C:\_Local_DEV\repos\PDFtoPDFocr\dist\PDFtoPDFocr\PDFtoPDFocr.exe"
$Shortcut.WorkingDirectory = "C:\_Local_DEV\repos\PDFtoPDFocr\dist\PDFtoPDFocr"
$Shortcut.IconLocation = "C:\_Local_DEV\repos\PDFtoPDFocr\PDFtoPDFocr.ico, 0"
$Shortcut.Description = "PDFtoPDFocr - OCR-Verarbeitung für PDFs"
$Shortcut.Save()
```

---

## 6. Fehlerbehebung / Windows Icon-Cache Reset

Falls Windows nach einem Neu-Build weiterhin ein altes oder generisches Standard-Icon anzeigt, ist der Explorer-Icon-Cache veraltet.

Befehl zum schnellen Cache-Reload:
```cmd
ie4uinit.exe -show
```

Oder vollständiger Icon-Cache-Reset per PowerShell:
```powershell
taskkill /f /im explorer.exe
Remove-Item "$env:LOCALAPPDATA\IconCache.db" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:LOCALAPPDATA\Microsoft\Windows\Explorer\iconcache*.db" -Force -ErrorAction SilentlyContinue
start explorer.exe
```
