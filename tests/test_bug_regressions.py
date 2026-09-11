# -*- coding: utf-8 -*-
"""Regressionstests Bugsweep.

BS-1: pikepdf-Quell-PDFs wurden im Loop VOR out_pdf.save() geschlossen
      (pikepdf kopiert lazy -> korrupte/fehlende OCR-Seiten).
BS-2: OCR-Fehler im Worker via print() statt logging -> crasht den Worker-Thread
      im windowed-PyInstaller (sys.stdout None).
BS-3: merge_ocr_outputs Quell-PDFs wurden im Loop VOR merged.save() geschlossen
      (pikepdf kopiert lazy -> Stream-Korruption beim Mergen).
BS-4: Transparente RGBA-/LA-/P-Bilder werden auf weißem Hintergrund composited.
BS-5: 0-Byte .traineddata-Dateien werden erkannt und neu heruntergeladen.
BS-6: normalize_image_for_ocr behandelt alle Alpha- & Transparenz-Modi (PA sowie tRNS).
BS-7: add_file normalisiert Pfade und verhindert Duplikate bei Case-/Relativpfad-Varianten.
BS-8: Nach Stapeln/Mergen finden Doppelklick, Kontextmenü und Manifest die nach 'Einzel-Seiten' verschobenen OCR-Ergebnisse statt der Quelldatei.
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


def test_bs6_normalize_image_for_ocr_pa_and_indexed_transparency():
    """BS-6: PA-Modus (Palette+Alpha) und Indexed-Transparency (L/RGB mit tRNS)
    müssen auf weißem Hintergrund composited werden, statt schwarz eingefärbt zu werden.
    """
    from PIL import Image
    import PDFtoPDFocr_2 as app

    # 1. PA-Modus (Palette mit Alphakanal)
    pa = Image.new("PA", (10, 10), (0, 0))  # transparenter Hintergrund
    pa.putpixel((5, 5), (0, 255))           # opaker Pixel
    norm_pa = app.normalize_image_for_ocr(pa)
    assert norm_pa.mode == "RGB"
    assert norm_pa.getpixel((0, 0)) == (255, 255, 255), (
        f"PA transparenter Hintergrund muss weiß sein, war aber {norm_pa.getpixel((0, 0))}"
    )

    # 2. L-Modus mit tRNS Transparenz-Metadaten
    l_img = Image.new("L", (10, 10), 0)
    l_img.info["transparency"] = 0
    norm_l = app.normalize_image_for_ocr(l_img)
    assert norm_l.mode == "RGB"
    assert norm_l.getpixel((0, 0)) == (255, 255, 255), (
        f"L mit Transparenz muss weiß sein, war aber {norm_l.getpixel((0, 0))}"
    )


def test_bs7_add_file_duplicate_detection_normalizes_paths():
    """BS-7: add_file normalisiert Pfade (Slashes, redundante Trenner) gegen Duplikate."""
    from PySide6.QtWidgets import QApplication
    import PDFtoPDFocr_2 as app

    _ = QApplication.instance() or QApplication([])
    widget = app.PDFListWidget()

    widget.add_file("C:/scans/document.pdf")
    assert widget.count() == 1

    # Gleiche Datei mit Backslashes darf kein Duplikat anlegen
    widget.add_file(r"C:\scans\document.pdf")
    assert widget.count() == 1

    # Gleiche Datei mit redundanten Punkten/Slashes darf kein Duplikat anlegen
    widget.add_file("C:/scans/./document.pdf")
    assert widget.count() == 1


def test_bs7_add_file_case_and_relative_duplicates(tmp_path):
    """BS-7: add_file erkennt Duplikate bei relativen vs. absoluten Pfaden und Windows-Case."""
    import os
    import sys
    from PySide6.QtWidgets import QApplication
    import PDFtoPDFocr_2 as app

    _ = QApplication.instance() or QApplication([])
    widget = app.PDFListWidget()

    # Relativer Pfad vs. absoluter Pfad
    test_pdf = tmp_path / "relative_sample.pdf"
    test_pdf.write_bytes(b"%PDF-1.4\n")

    cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        widget.add_file("relative_sample.pdf")
        assert widget.count() == 1

        widget.add_file(str(test_pdf))
        assert widget.count() == 1

        # Case-Insensitivität auf Windows
        if sys.platform.startswith("win"):
            upper_path = str(test_pdf).upper()
            widget.add_file(upper_path)
            assert widget.count() == 1
    finally:
        os.chdir(cwd)


def test_bs8_double_click_and_context_menu_open_archived_ocr_result_after_merge(tmp_path, monkeypatch):
    """BS-8: Nach Stapeln/Mergen (Einzeldateien in 'Einzel-Seiten' archiviert)
    müssen Doppelklick und Kontextmenü das archivierte OCR-Ergebnis öffnen,
    nicht fälschlicherweise die un-ocred Quelldatei.
    """
    from PIL import Image
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    import PDFtoPDFocr_2 as app

    _ = QApplication.instance() or QApplication([])
    gui = app.OCRConverterGUI()

    opened_urls = []
    from PySide6.QtGui import QDesktopServices
    monkeypatch.setattr(QDesktopServices, "openUrl", lambda url: opened_urls.append(url.toLocalFile()) or True)

    try:
        f1 = tmp_path / "scan1.pdf"
        f2 = tmp_path / "scan2.pdf"
        f1.write_bytes(b"%PDF-source-1\n")
        f2.write_bytes(b"%PDF-source-2\n")

        gui.list_widget.add_file(str(f1))
        gui.list_widget.add_file(str(f2))

        # Erzeuge OCR-Ausgabedateien
        o1 = tmp_path / "scan1_ocred.pdf"
        o2 = tmp_path / "scan2_ocred.pdf"
        Image.new("RGB", (5, 5), "white").save(o1, "PDF")
        Image.new("RGB", (5, 5), "white").save(o2, "PDF")

        item1 = gui.list_widget.item(0)
        item2 = gui.list_widget.item(1)
        item1.setData(Qt.UserRole + 1, "done")
        item2.setData(Qt.UserRole + 1, "done")
        item1.setSelected(True)
        item2.setSelected(True)

        # Merge ausführen -> Einzelseiten wandern nach 'Einzel-Seiten'
        merged_path = gui.merge_selected(target_path=tmp_path / "merged.pdf")
        assert merged_path.exists()
        assert not o1.exists()
        archived_o1 = tmp_path / app.MERGE_SUBFOLDER_NAME / "scan1_ocred.pdf"
        assert archived_o1.exists()

        # 1. Doppelklick auf Item 1 muss das archivierte OCR-Ergebnis öffnen
        gui._on_item_double_clicked(item1)
        assert len(opened_urls) == 1
        assert Path(opened_urls[-1]).resolve() == archived_o1.resolve(), (
            f"Doppelklick öffnete {opened_urls[-1]}, erwartet wurde {archived_o1}"
        )

        # 2. Kontextmenü 'Datei öffnen' muss ebenfalls das archivierte OCR-Ergebnis öffnen
        menu = gui._create_list_context_menu([item1])
        open_action = [a for a in menu.actions() if a.text() == app.tr("action_open_file")][0]
        open_action.trigger()
        assert len(opened_urls) == 2
        assert Path(opened_urls[-1]).resolve() == archived_o1.resolve(), (
            f"Kontextmenü 'Datei öffnen' öffnete {opened_urls[-1]}, erwartet wurde {archived_o1}"
        )

        # 3. Kontextmenü 'Ordner öffnen' muss den Archivordner öffnen
        folder_action = [a for a in menu.actions() if a.text() == app.tr("action_open_folder")][0]
        folder_action.trigger()
        assert len(opened_urls) == 3
        assert Path(opened_urls[-1]).resolve() == archived_o1.parent.resolve(), (
            f"Kontextmenü 'Ordner öffnen' öffnete {opened_urls[-1]}, erwartet wurde {archived_o1.parent}"
        )
    finally:
        gui.close()


def test_bs8_resolve_ocr_output_path_finds_subfolder_and_export_folder(tmp_path):
    """BS-8: resolve_ocr_output_path findet OCR-Dateien im Quellordner, im 'Einzel-Seiten'-Archiv
    sowie im konfigurierten Exportordner.
    """
    from PIL import Image
    import PDFtoPDFocr_2 as app

    source = tmp_path / "docs" / "report.pdf"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"%PDF-doc\n")

    # 1. Vor dem Merge: direkt neben der Quelldatei
    direct_ocr = source.parent / "report_ocred.pdf"
    Image.new("RGB", (5, 5), "white").save(direct_ocr, "PDF")
    resolved = app.resolve_ocr_output_path(source)
    assert resolved is not None
    assert resolved.resolve() == direct_ocr.resolve()

    # 2. Nach lokalem Merge: in Einzel-Seiten verschoben
    subfolder = source.parent / app.MERGE_SUBFOLDER_NAME
    subfolder.mkdir()
    archived_ocr = subfolder / "report_ocred.pdf"
    direct_ocr.rename(archived_ocr)

    resolved = app.resolve_ocr_output_path(source)
    assert resolved is not None
    assert resolved.resolve() == archived_ocr.resolve()

    # 3. Wenn in konfigurierten Exportordner verschoben
    export_dir = tmp_path / "custom_exports"
    export_subfolder = export_dir / app.MERGE_SUBFOLDER_NAME
    export_subfolder.mkdir(parents=True)
    exp_archived = export_subfolder / "report_ocred.pdf"
    archived_ocr.rename(exp_archived)

    resolved = app.resolve_ocr_output_path(source, export_folder=export_dir)
    assert resolved is not None
    assert resolved.resolve() == exp_archived.resolve()


def test_bs8_add_folder_handles_oserror_gracefully(tmp_path):
    """BS-8: PDFListWidget.add_folder fängt OSError (z.B. nicht existenter oder unlesbarer Ordner)
    sauber ab, statt mit unhandled exception abzustürzen.
    """
    from PySide6.QtWidgets import QApplication
    import PDFtoPDFocr_2 as app

    _ = QApplication.instance() or QApplication([])
    widget = app.PDFListWidget()

    non_existent = tmp_path / "does_not_exist_folder"
    # Darf nicht abstürzen
    widget.add_folder(str(non_existent), batch_id="test-batch")
    assert widget.count() == 0
