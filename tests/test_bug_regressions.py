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


def test_bs4_normalize_image_for_ocr_rgba_compositing_white_background():
    """BS-4: Transparente RGBA-Bilder werden auf weißem Hintergrund composited statt schwarz gefärbt."""
    from PIL import Image
    import PDFtoPDFocr_2 as app

    # Erzeuge Bild mit transparentem Hintergrund (0,0,0,0) und schwarzem Zeichenpixel (0,0,0,255)
    rgba = Image.new("RGBA", (20, 20), (0, 0, 0, 0))
    rgba.putpixel((10, 10), (0, 0, 0, 255))

    normalized = app.normalize_image_for_ocr(rgba)

    assert normalized.mode == "RGB"
    # Hintergrund muss weiß (255, 255, 255) sein, nicht schwarz (0, 0, 0)
    assert normalized.getpixel((0, 0)) == (255, 255, 255)
    # Text-Pixel muss schwarz (0, 0, 0) bleiben
    assert normalized.getpixel((10, 10)) == (0, 0, 0)


def test_bs4_normalize_image_for_ocr_la_and_p_modes():
    """BS-4: LA- und palettierte Bilder mit Transparenz werden sauber nach RGB normalisiert."""
    from PIL import Image
    import PDFtoPDFocr_2 as app

    # LA (Luminance + Alpha)
    la = Image.new("LA", (10, 10), (0, 0))  # transparent
    la.putpixel((5, 5), (0, 255))           # schwarzer Pixel
    norm_la = app.normalize_image_for_ocr(la)
    assert norm_la.mode == "RGB"
    assert norm_la.getpixel((0, 0)) == (255, 255, 255)
    assert norm_la.getpixel((5, 5)) == (0, 0, 0)

    # P-Mode mit Transparenz
    p = Image.new("P", (10, 10))
    p.info["transparency"] = 0
    norm_p = app.normalize_image_for_ocr(p)
    assert norm_p.mode == "RGB"


def test_bs5_ensure_tesseract_handles_zero_byte_traineddata(tmp_path, monkeypatch):
    """BS-5: 0-Byte .traineddata-Dateien werden erkannt und neu heruntergeladen."""
    import PDFtoPDFocr_2 as app

    tessdata_dir = tmp_path / "tessdata"
    tessdata_dir.mkdir(parents=True, exist_ok=True)
    corrupted_target = tessdata_dir / "testlang.traineddata"
    corrupted_target.write_bytes(b"")  # 0-Byte-Datei

    monkeypatch.setattr(app, "get_tessdata_dir", lambda: str(tessdata_dir))
    monkeypatch.setattr(app, "configure_tesseract", lambda: "mock_tesseract")
    monkeypatch.setattr(app.QMessageBox, "information", lambda *a, **kw: None)

    class MockResponse:
        status_code = 200
        def iter_content(self, chunk_size=65536):
            yield b"VALID_TRAINEDDATA_CONTENT"

    monkeypatch.setattr("PDFtoPDFocr_2.requests.get", lambda url, stream, timeout: MockResponse())

    res = app.ensure_tesseract("testlang")
    assert res is True
    assert corrupted_target.exists()
    assert corrupted_target.stat().st_size > 0
    assert corrupted_target.read_bytes() == b"VALID_TRAINEDDATA_CONTENT"

