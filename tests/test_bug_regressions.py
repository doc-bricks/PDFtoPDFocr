# -*- coding: utf-8 -*-
"""Regressionstests Bugsweep 2026-06-23 (Desktop, /bugsweep-Loop Run 5/15).

BS-1: pikepdf-Quell-PDFs wurden im Loop VOR out_pdf.save() geschlossen
      (pikepdf kopiert lazy -> korrupte/fehlende OCR-Seiten).
BS-2: OCR-Fehler im Worker via print() statt logging -> crasht den Worker-Thread
      im windowed-PyInstaller (sys.stdout None).
BS-3: merge_ocr_outputs Quell-PDFs wurden im Loop VOR merged.save() geschlossen
      (pikepdf kopiert lazy -> Stream-Korruption beim Mergen).
"""
from pathlib import Path
import py_compile

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


def test_bs3_merge_ocr_outputs_sources_closed_after_save():
    """Beim Mergen duerfen Quell-PDFs erst NACH merged.save() geschlossen werden."""
    i_save = _SRC.find("merged.save(merged_path)")
    i_close_loop = _SRC.find("for src_pdf in opened_sources:")
    assert 0 <= i_save < i_close_loop, (
        "Quell-PDFs in merge_ocr_outputs werden vor merged.save() geschlossen"
    )


def test_py_compile_syntax_clean():
    """PDFtoPDFocr_2.py laesst sich fehlerfrei kompilieren."""
    py_compile.compile(str(_SRC_PATH), doraise=True)


def test_tesseract_portable_exclude_list_covers_known_tools():
    """U7: Die Ausschlussliste enthaelt alle Tesseract-Trainingstools."""
    import build_release
    for tool in ("lstmtraining.exe", "cntraining.exe", "tesseract-uninstall.exe"):
        assert tool in build_release.TESSERACT_PORTABLE_EXCLUDE_NAMES
