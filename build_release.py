#!/usr/bin/env python3
"""Build script for PDFtoPDFocr release.

Creates a clean virtual environment with only the required dependencies,
then runs PyInstaller with the optimized spec file.

Usage:
    python build_release.py          # Full build
    python build_release.py --clean  # Remove old build artifacts first
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
VENV_DIR = SCRIPT_DIR / ".build_venv"
SPEC_FILE = SCRIPT_DIR / "PDFtoPDFocr.spec"
DIST_DIR = SCRIPT_DIR / "dist"
BUILD_DIR = SCRIPT_DIR / "build"

# Only the packages actually needed at runtime
REQUIRED_PACKAGES = [
    "PySide6==6.8.3",
    "pytesseract>=0.3.10",
    "Pillow>=10.0",
    "pdf2image>=1.16",
    "pikepdf>=8.0",
    "requests>=2.28",
    "pyinstaller>=6.0",
]


def run(cmd, **kwargs):
    """Runs a command and exits on failure."""
    print(f"  > {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        print(f"FEHLER: Kommando fehlgeschlagen (Exit {result.returncode})")
        sys.exit(1)


def main():
    clean = "--clean" in sys.argv

    if clean:
        print("[1/4] Bereinige alte Artefakte...")
        for d in [DIST_DIR, BUILD_DIR, VENV_DIR]:
            if d.exists():
                shutil.rmtree(d, ignore_errors=True)
                print(f"  Geloescht: {d}")

    # Schritt 1: Sauberes venv erstellen
    print("[1/4] Erstelle sauberes Build-venv...")
    if not VENV_DIR.exists():
        run([sys.executable, "-m", "venv", str(VENV_DIR)])

    # Python im venv
    if os.name == "nt":
        python = str(VENV_DIR / "Scripts" / "python.exe")
    else:
        python = str(VENV_DIR / "bin" / "python")

    # Schritt 2: Dependencies installieren
    print("[2/4] Installiere Dependencies...")
    run([python, "-m", "pip", "install", "--upgrade", "pip"])
    for pkg in REQUIRED_PACKAGES:
        run([python, "-m", "pip", "install", pkg])

    # Schritt 3: PyInstaller ausfuehren
    print("[3/4] Starte PyInstaller Build...")
    pyinstaller = str(VENV_DIR / ("Scripts" if os.name == "nt" else "bin") / "pyinstaller")
    run([pyinstaller, str(SPEC_FILE), "--noconfirm"], cwd=str(SCRIPT_DIR))

    # Schritt 4: Ergebnis pruefen
    print("[4/4] Pruefe Build-Ergebnis...")
    exe_path = DIST_DIR / "PDFtoPDFocr" / ("PDFtoPDFocr.exe" if os.name == "nt" else "PDFtoPDFocr")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        total_mb = sum(f.stat().st_size for f in (DIST_DIR / "PDFtoPDFocr").rglob("*") if f.is_file()) / (1024 * 1024)
        print(f"\n  Build erfolgreich!")
        print(f"  EXE: {exe_path} ({size_mb:.1f} MB)")
        print(f"  Gesamt: {total_mb:.1f} MB")
    else:
        print(f"\n  WARNUNG: EXE nicht gefunden: {exe_path}")


if __name__ == "__main__":
    main()
