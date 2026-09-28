"""App-Icon-Loader für PDFtoPDFocr.

Lädt das Anwendungs-Icon mit robuster Multi-Pfad-Auflösung (PyInstaller-Bundle,
assets/app_icon.ico, assets/PDFtoPDFocr.ico, Root-ICOs und PNG-Fallback).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Liefert das Basisverzeichnis für Ressourcen im Repo oder gefrorenen Bundle."""
    return Path(getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))))


def load_app_icon():
    """Lädt ein valides QIcon für PDFtoPDFocr über mehrere Fallback-Pfade."""
    try:
        from PySide6.QtGui import QIcon
    except ImportError:
        return None

    root = get_project_root()
    candidates = [
        root / "assets" / "app_icon.ico",
        root / "assets" / "PDFtoPDFocr.ico",
        root / "assets" / "icon.ico",
        root / "assets" / "DesktopIcon.ico",
        root / "PDFtoPDFocr.ico",
        root / "DesktopIcon.ico",
        root / "ICO.ico",
        root / "icon.ico",
        root / "assets" / "PDFtoPDFocr.png",
        root / "assets" / "icon.png",
        root / "assets" / "DesktopIcon.png",
        root / "PDFtoPDFocr.png",
        root / "DesktopIcon.png",
        root / "icon.png",
    ]

    for candidate in candidates:
        if candidate.is_file():
            icon = QIcon(str(candidate))
            if not icon.isNull():
                return icon

    return QIcon()


def get_app_icon():
    """Alias für load_app_icon."""
    return load_app_icon()
