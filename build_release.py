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

# U7 Paket-Hygiene: Tesseract-Trainingstools und der Deinstaller gehoeren nicht
# ins Store-Paket (Groesse/WACK) -- nur die Laufzeit-Binaries werden gebuendelt.
TESSERACT_PORTABLE_EXCLUDE_NAMES = {
    "lstmtraining.exe", "lstmtraining.1.html",
    "cntraining.exe", "cntraining.1.html",
    "mftraining.exe", "mftraining.1.html",
    "text2image.exe", "text2image.1.html",
    "shapeclustering.exe", "shapeclustering.1.html",
    "combine_lang_model.exe", "combine_lang_model.1.html",
    "combine_tessdata.exe", "combine_tessdata.1.html",
    "dawg2wordlist.exe", "dawg2wordlist.1.html",
    "wordlist2dawg.exe", "wordlist2dawg.1.html",
    "merge_unicharsets.exe", "merge_unicharsets.1.html",
    "set_unicharset_properties.exe", "set_unicharset_properties.1.html",
    "unicharset_extractor.exe", "unicharset_extractor.1.html",
    "ambiguous_words.exe", "ambiguous_words.1.html",
    "classifier_tester.exe", "classifier_tester.1.html",
    "lstmeval.exe", "lstmeval.1.html",
    "tesseract-uninstall.exe",
    "winpath.exe",
}


def collect_tesseract_portable_files(root) -> list:
    """Lists (source_file, dest_dir) pairs for bundling tesseract_portable/,
    excluding training tools and the uninstaller (U7 Paket-Hygiene).

    Used both by PDFtoPDFocr.spec (PyInstaller `datas`) and by tests, so the
    exclusion list has exactly one source of truth.

    Args:
        root: Path to the tesseract_portable directory.

    Returns:
        List of (absolute source file path, PyInstaller dest folder) tuples,
        sorted for reproducible builds.
    """
    root = Path(root)
    dest_root_name = root.name
    entries = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name in TESSERACT_PORTABLE_EXCLUDE_NAMES:
            continue
        rel_dir = path.parent.relative_to(root)
        dest = dest_root_name if str(rel_dir) == "." else str(Path(dest_root_name) / rel_dir)
        entries.append((str(path), dest))
    return entries

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
                print(f"  Gelöscht: {d}")

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

    # Schritt 3: PyInstaller ausführen
    print("[3/4] Starte PyInstaller Build...")
    pyinstaller = str(VENV_DIR / ("Scripts" if os.name == "nt" else "bin") / "pyinstaller")
    run([pyinstaller, str(SPEC_FILE), "--noconfirm"], cwd=str(SCRIPT_DIR))

    # Schritt 4: Ergebnis prüfen
    print("[4/4] Prüfe Build-Ergebnis...")
    exe_path = DIST_DIR / "PDFtoPDFocr" / ("PDFtoPDFocr.exe" if os.name == "nt" else "PDFtoPDFocr")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        total_mb = sum(f.stat().st_size for f in (DIST_DIR / "PDFtoPDFocr").rglob("*") if f.is_file()) / (1024 * 1024)
        print("\n  Build erfolgreich!")
        print(f"  EXE: {exe_path} ({size_mb:.1f} MB)")
        print(f"  Gesamt: {total_mb:.1f} MB")
    else:
        print(f"\n  WARNUNG: EXE nicht gefunden: {exe_path}")


if __name__ == "__main__":
    main()
