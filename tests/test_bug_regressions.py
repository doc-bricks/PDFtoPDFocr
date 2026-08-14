# -*- coding: utf-8 -*-
"""Regressionstests Bugsweep 2026-06-23 (Desktop, /bugsweep-Loop Run 5/15).

BS-1: pikepdf-Quell-PDFs wurden im Loop VOR out_pdf.save() geschlossen
      (pikepdf kopiert lazy -> korrupte/fehlende OCR-Seiten).
BS-2: OCR-Fehler im Worker via print() statt logging -> crasht den Worker-Thread
      im windowed-PyInstaller (sys.stdout None).
BS-3: merge_ocr_outputs Quell-PDFs wurden im Loop VOR merged.save() geschlossen
      (pikepdf kopiert lazy -> Stream-Korruption beim Mergen).
"""
import io
import py_compile
from pathlib import Path
import pikepdf
from PIL import Image

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


def test_bs3_merge_ocr_outputs_sources_kept_open_until_save():
    """In merge_ocr_outputs muessen geoffnete Quell-PDFs bis nach merged.save() offen bleiben."""
    import PDFtoPDFocr_2 as app
    import inspect

    src = inspect.getsource(app.merge_ocr_outputs)
    assert "opened_sources" in src
    assert "opened_sources.append(src_pdf)" in src
    i_save = src.find("merged.save(merged_path)")
    i_close = src.find("for src_pdf in opened_sources")
    assert 0 <= i_save < i_close, (
        "Quell-PDFs in merge_ocr_outputs werden vor merged.save() geschlossen -> Lazy-Copy-Korruption"
    )


def test_bs3_merge_ocr_outputs_functional_execution(tmp_path):
    """Funktionaler Test von merge_ocr_outputs mit mehreren Quell-PDFs."""
    import PDFtoPDFocr_2 as app

    export_folder = tmp_path / "exports"
    p1 = tmp_path / "page1_ocred.pdf"
    p2 = tmp_path / "page2_ocred.pdf"
    Image.new("RGB", (20, 20), "white").save(p1, "PDF")
    Image.new("RGB", (20, 20), "blue").save(p2, "PDF")

    merged = app.merge_ocr_outputs([str(p1), str(p2)], "combined.pdf", export_folder)
    assert merged.exists()
    with pikepdf.Pdf.open(merged) as pdf:
        assert len(pdf.pages) == 2


def test_bs_syntax_valid():
    py_compile.compile(str(_SRC_PATH), doraise=True)
