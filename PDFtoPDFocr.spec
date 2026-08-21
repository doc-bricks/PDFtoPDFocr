# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for PDFtoPDFocr.

Optimized build to reduce size from 285MB to ~40-60MB:
- Excludes unnecessary packages (matplotlib, numpy, pandas, scipy, etc.)
- Uses onedir mode for faster startup in MSIX containers
- Bundles Tesseract portable + Poppler binaries via --add-data

Build:
    pyinstaller PDFtoPDFocr.spec

Prerequisites:
    1. Clean venv with only required packages:
       pip install PySide6 pytesseract Pillow pdf2image pikepdf requests
    2. tesseract_portable/ folder with Tesseract OCR binaries
    3. poppler/ folder with Poppler binaries (pdftoppm.exe etc.)
"""

import os
import sys

# SPECPATH wird von PyInstaller in den Spec-Namespace injiziert (Verzeichnis
# dieser .spec-Datei). Ohne diesen Eintrag findet Python build_release.py
# nicht, wenn pyinstaller aus einem anderen Arbeitsverzeichnis gestartet wird.
sys.path.insert(0, SPECPATH)
import build_release

block_cipher = None

# Tesseract und Poppler Pfade
tesseract_dir = 'tesseract_portable'
poppler_dir = 'poppler'

datas = [
    ('translations.json', '.'),
    ('assets', 'assets'),
    ('PDFtoPDFocr.ico', '.'),
    ('ICO.ico', '.'),
]

# Nur einbinden wenn vorhanden
if os.path.isdir(tesseract_dir):
    # U7 Paket-Hygiene: Trainingstools/Deinstaller ausschliessen statt den
    # kompletten Ordner 1:1 zu spiegeln (siehe build_release.py).
    datas.extend(build_release.collect_tesseract_portable_files(tesseract_dir))

if os.path.isdir(poppler_dir):
    datas.append((poppler_dir, poppler_dir))

if os.path.exists('PDFtoPDFocr.ico'):
    icon_path = 'PDFtoPDFocr.ico'
elif os.path.exists('assets/icon.ico'):
    icon_path = 'assets/icon.ico'
elif os.path.exists('ICO.ico'):
    icon_path = 'ICO.ico'
elif os.path.exists('store_assets/icon.ico'):
    icon_path = 'store_assets/icon.ico'
else:
    icon_path = None

a = Analysis(
    ['PDFtoPDFocr_2.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'sqlite3',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # GUI-Frameworks, die nicht benötigt werden
        'tkinter', 'PyQt5', 'PyQt6',
        # Wissenschaftliche & schwere Pakete
        'matplotlib', 'numpy', 'pandas', 'scipy', 'sklearn',
        'altair', 'plotly', 'pyarrow', 'soundfile', 'sympy',
        # Andere nicht benötigte Pakete
        'cv2', 'docx', 'openpyxl', 'xlrd',
        'IPython', 'jupyter', 'notebook',
        'pytest', 'unittest',
        'setuptools', 'pip', 'wheel',
        'cryptography', 'paramiko',
        'asyncio', 'aiohttp',
        # PySide6-Module, die nicht benötigt werden
        'PySide6.QtWebEngine', 'PySide6.QtWebEngineWidgets',
        'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
        'PySide6.Qt3DCore', 'PySide6.Qt3DRender',
        'PySide6.QtCharts', 'PySide6.QtDataVisualization',
        'PySide6.QtNetwork', 'PySide6.QtBluetooth',
        'PySide6.QtPositioning', 'PySide6.QtSensors',
        'PySide6.QtSerialPort', 'PySide6.QtSvg',
        'PySide6.QtTest', 'PySide6.QtXml',
        'PySide6.QtDesigner', 'PySide6.QtHelp',
        'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets',
        'PySide6.QtPdf', 'PySide6.QtPdfWidgets',
        'PySide6.QtQuick', 'PySide6.QtQml',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

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
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='PDFtoPDFocr',
)
