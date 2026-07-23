# -*- coding: utf-8 -*-
"""Regressionstests Bugsweep 2026-06-23 (Desktop, /bugsweep-Loop Run 5/15).

BS-1: pikepdf-Quell-PDFs wurden im Loop VOR out_pdf.save() geschlossen
      (pikepdf kopiert lazy -> korrupte/fehlende OCR-Seiten).
BS-2: OCR-Fehler im Worker via print() statt logging -> crasht den Worker-Thread
      im windowed-PyInstaller (sys.stdout None).
"""
import py_compile
from pathlib import Path

_SRC_PATH = Path(__file__).parent.parent / "PDFtoPDFocr_2.py"
_SRC = _SRC_PATH.read_text(encoding="utf-8")


def test_bs1_pikepdf_sources_collected():
    """Die pikepdf-Quellen werden in page_sources gesammelt (statt im Loop geschlossen)."""
    assert "page_sources" in _SRC
    assert "page_sources.append" in _SRC


def test_bs1_sources_closed_after_save():
    """Quell-PDFs duerfen erst NACH out_pdf.save() geschlossen werden."""
    i_save = _SRC.find("out_pdf.save(dst_path)")
    i_close_loop = _SRC.find("for _src_pdf, _tmp in page_sources")
    assert 0 <= i_save < i_close_loop, (
        "Quell-PDFs werden vor out_pdf.save() geschlossen -> Lazy-Copy-Korruption"
    )


def test_bs2_ocr_error_uses_logging_not_print():
    """OCR-Fehler im Worker via logging, nicht print (windowed stdout=None)."""
    assert 'print(f"OCR-Fehler' not in _SRC
    assert 'logging.error("OCR-Fehler bei %s: %s"' in _SRC


def test_bs_syntax_valid():
    py_compile.compile(str(_SRC_PATH), doraise=True)
