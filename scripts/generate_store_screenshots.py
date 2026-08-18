#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erzeugt reproduzierbare Windows-Store-Screenshots mit neutralen Demo-Daten.

Deckt den in `releases/windowsstore/SCREENSHOT_PLAN.md` beschriebenen Satz ab:
01-main-window, 02-language-selection, 03-batch-progress, 04-job-export.
Keine echten Dateipfade/-inhalte -- nur neutrale Beispielnamen (Datenschutz-
Hinweis des Plans).
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "PDFtoPDFocr_2.py"
OUTPUT_DIR = PROJECT_ROOT / "releases" / "windowsstore" / "screenshots"
WINDOW_SIZE = (960, 640)

# Neutrale Beispielnamen (kein echter Dokumentinhalt/Pfad) -- siehe SCREENSHOT_PLAN.md.
DEMO_FILES = [
    "scan-beispiel-01.pdf",
    "scan-beispiel-02.pdf",
    "scan-beispiel-03.pdf",
    "scan-beispiel-04.pdf",
]


def _force_native_platform() -> None:
    """Entfernt eine geerbte offscreen-Plattform VOR der QApplication-Erzeugung.

    Unter QT_QPA_PLATFORM=offscreen rendert Qt auf Windows keine echten
    Glyphen -- jede Glyphe wird als .notdef-Kaestchen (Tofu) gerastert; ein
    Screenshot per grab() sieht dann gueltig aus, ist aber unbrauchbar (Fund
    aus der Store-Welle 1, behoben u.a. in SoftwareCenter/ProfiPrompt/
    CleanMarkdown/LitZen/ProSync/PromptBoard/Klangpult).
    """
    if os.environ.get("QT_QPA_PLATFORM") == "offscreen":
        del os.environ["QT_QPA_PLATFORM"]


def _render_probe_char(app: QApplication, ch: str) -> bytes:
    from PySide6.QtGui import QPainter
    pm = QPixmap(48, 48)
    pm.fill(Qt.GlobalColor.white)
    p = QPainter(pm)
    p.setFont(app.font())
    p.drawText(pm.rect(), Qt.AlignCenter, ch)
    p.end()
    return bytes(pm.toImage().constBits())


def _assert_font_rendering(app: QApplication) -> None:
    """Bricht ab statt still ein Tofu-Screenshot-Set zu erzeugen."""
    platform = QApplication.platformName()
    if platform == "offscreen":
        raise RuntimeError(
            "Qt laeuft unter 'offscreen' -- Screenshots waeren Tofu (Kaestchen "
            "statt Text). QT_QPA_PLATFORM=offscreen nicht setzen."
        )
    probes = ["A", "B", "g", "8", "M"]
    renders = [_render_probe_char(app, ch) for ch in probes]
    blank = _render_probe_char(app, " ")
    distinct = len(set(renders))
    non_blank = sum(1 for r in renders if r != blank)
    if not (distinct >= 3 and non_blank >= len(probes) - 1):
        raise RuntimeError(
            f"Font-Rendering-Selbsttest fehlgeschlagen (Plattform '{platform}'): "
            "gerenderte Glyphen sind nicht unterscheidbar (Tofu-Verdacht). "
            "Abbruch, um kein defektes Screenshot-Set zu erzeugen."
        )


def load_module():
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    spec = importlib.util.spec_from_file_location("pdftopdfocr_store_module", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def ensure_app() -> QApplication:
    _force_native_platform()
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    _assert_font_rendering(app)
    return app


def _set_item_state(item, state: str, text_prefix: str = "") -> None:
    from PySide6.QtCore import Qt as _Qt
    if state == "done":
        item.setText(f"✓ {item.text().lstrip('✓⚠ ')}")
        item.setForeground(QColor("green"))
        item.setData(_Qt.UserRole + 1, "done")
    elif state == "error":
        item.setText(f"⚠ {item.text().lstrip('✓⚠ ')}")
        item.setForeground(QColor("orange"))
        item.setData(_Qt.UserRole + 1, "error")


def capture(widget, target: Path) -> Path:
    widget.repaint()
    QApplication.processEvents()
    pixmap = widget.grab()
    target.parent.mkdir(parents=True, exist_ok=True)
    if not pixmap.save(str(target), "PNG"):
        raise RuntimeError(f"Screenshot konnte nicht gespeichert werden: {target}")
    return target


def generate_screenshots() -> list[Path]:
    app = ensure_app()
    module = load_module()

    written: list[Path] = []
    gui = module.OCRConverterGUI()
    try:
        gui.resize(*WINDOW_SIZE)
        gui.show()
        QApplication.processEvents()

        # 01-main-window.png -- leere Dateiliste, Ausgangszustand.
        written.append(capture(gui, OUTPUT_DIR / "01-main-window.png"))

        # 02-language-selection.png -- Dateien hinzugefuegt, OCR-Sprache sichtbar.
        for name in DEMO_FILES:
            gui.list_widget.add_file(name)
        gui.lang_combo.setCurrentText("deu")
        QApplication.processEvents()
        written.append(capture(gui, OUTPUT_DIR / "02-language-selection.png"))

        # 03-batch-progress.png -- gemischter Fortschritt (fertig/Fehler/ausstehend).
        for i in range(gui.list_widget.count()):
            item = gui.list_widget.item(i)
            if i == 0:
                _set_item_state(item, "done")
            elif i == 1:
                _set_item_state(item, "done")
            elif i == 2:
                _set_item_state(item, "error")
            # i == 3 bleibt "pending" (Ausgangszustand von add_file)
        # Bewusst KEIN "fertig"/"abgeschlossen"-Text, solange eine Datei noch
        # aussteht -- Policy 10.1.1.3 Inaccurate Representation (Lehrfall
        # SoftwareCenter-Rejection 2026-08-11) verbietet irrefuehrende Screenshots.
        gui.status_label.setText("Verarbeite Datei 3 von 4 ...")
        gui.status_label.setStyleSheet("")
        QApplication.processEvents()
        written.append(capture(gui, OUTPUT_DIR / "03-batch-progress.png"))

        # 04-job-export.png -- Job-Export-Workflow (pdftopdfocr-job-v1), ohne Dialog
        # (Datei-Save-Dialog waere nicht automatisierbar/nicht store-tauglich als
        # Screenshot) -- zeigt stattdessen den Bestaetigungs-Status nach Export.
        gui.status_label.setText(
            module.tr("status_export_saved", filename=f"{module.EXPORT_SCHEMA}.json")
            if hasattr(module, "tr")
            else f"Exportiert: {module.EXPORT_SCHEMA}.json"
        )
        gui.status_label.setStyleSheet("color: #0b6e4f; font-weight: bold;")
        QApplication.processEvents()
        written.append(capture(gui, OUTPUT_DIR / "04-job-export.png"))
    finally:
        gui.close()

    return written


def main() -> int:
    for path in generate_screenshots():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
