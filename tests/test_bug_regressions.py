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
BS-8: Nach Stapeln/Mergen finden Doppelklick, Kontextmenü und Manifest die nach 'Einzeldateien' verschobenen OCR-Ergebnisse statt der Quelldatei.
BS-9: Archiv-Pfadauflösung mit Glob-Metazeichen, Re-Merge-Idempotenz in merge_ocr_outputs und CLI-/Pfad-Normalisierung mit Anführungszeichen & Whitespace.
BS-10: export_job_manifest und build_job_export_payload berücksichtigen konfigurierten Exportordner, merge_selected aktualisiert Zielpfade relativ zum gewählten Ausgabeordner und add_paths_from_arguments registriert Ordner-Batches.
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


def test_bs9_resolve_ocr_output_path_escapes_glob_brackets(tmp_path):
    """BS-9: resolve_ocr_output_path maskiert Glob-Metazeichen wie '[' und ']' in Dateinamen
    damit archivierte/disambiguierte OCR-Dateien zuverlässig aufgelöst werden."""
    import PDFtoPDFocr_2 as app
    from PIL import Image

    sub = tmp_path / app.MERGE_SUBFOLDER_NAME
    sub.mkdir()

    source = tmp_path / "Scan [2026].pdf"
    source.write_bytes(b"%PDF-bracket\n")

    archived = sub / "Scan [2026]_ocred_12345678.pdf"
    Image.new("RGB", (5, 5), "white").save(archived, "PDF")

    resolved = app.resolve_ocr_output_path(source)
    assert resolved is not None, "resolve_ocr_output_path failed to find disambiguated file with brackets"
    assert resolved.resolve() == archived.resolve()


def test_bs9_merge_ocr_outputs_idempotent_for_already_archived_files(tmp_path):
    """BS-9: merge_ocr_outputs benennt bereits in 'Einzeldateien' archivierte Dateien nicht mehrfach
    mit zufälligen UUIDs um, wenn ein erneuter Merge aufgerufen wird."""
    import pikepdf
    import PDFtoPDFocr_2 as app

    sub = tmp_path / app.MERGE_SUBFOLDER_NAME
    sub.mkdir()

    p1 = sub / "doc1_ocred.pdf"
    p2 = sub / "doc2_ocred.pdf"
    for p in (p1, p2):
        pdf = pikepdf.Pdf.new()
        pdf.add_blank_page()
        pdf.save(p)
        pdf.close()

    app.merge_ocr_outputs([str(p1), str(p2)], "merged.pdf", tmp_path)
    assert p1.exists(), "doc1_ocred.pdf should remain unchanged in subfolder without UUID rename"
    assert p2.exists(), "doc2_ocred.pdf should remain unchanged in subfolder without UUID rename"

    # Zweiter Aufruf darf keine UUID-Ketten generieren
    app.merge_ocr_outputs([str(p1), str(p2)], "merged.pdf", tmp_path)
    assert p1.exists()
    assert p2.exists()
    assert len(list(sub.glob("*.pdf"))) == 2


def test_bs9_add_paths_from_arguments_handles_quoted_and_spaced_paths(tmp_path):
    """BS-9: add_paths_from_arguments verarbeitet Pfade mit Anführungszeichen und Whitespace."""
    from PySide6.QtWidgets import QApplication
    import PDFtoPDFocr_2 as app

    _ = QApplication.instance() or QApplication([])
    gui = app.OCRConverterGUI()
    try:
        f1 = tmp_path / "arg1.pdf"
        f2 = tmp_path / "arg2.pdf"
        f1.write_bytes(b"%PDF-1\n")
        f2.write_bytes(b"%PDF-2\n")

        # Quoted and spaced arguments
        count = gui.add_paths_from_arguments([f'"{f1}"', f"   {f2}   "])
        assert count == 2
        assert gui.list_widget.count() == 2
    finally:
        gui.close()


def test_bs9_add_file_sanitizes_surrounding_whitespace(tmp_path):
    """BS-9: add_file entfernt führende/nachlaufende Leerzeichen vor os.path.abspath."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    import PDFtoPDFocr_2 as app

    _ = QApplication.instance() or QApplication([])
    widget = app.PDFListWidget()

    f = tmp_path / "spaced.pdf"
    f.write_bytes(b"%PDF-spaced\n")

    widget.add_file(f"   {f}   ")
    assert widget.count() == 1
    stored = widget.item(0).data(Qt.UserRole)
    assert Path(stored).resolve() == f.resolve()
    assert Path(stored).exists()


def test_bs10_build_job_export_payload_and_manifest_respect_custom_export_folder(tmp_path):
    """BS-10: build_job_export_payload und export_job_manifest finden OCR-Ergebnisse im konfigurierten Exportordner."""
    import json
    from PIL import Image
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    import PDFtoPDFocr_2 as app

    _ = QApplication.instance() or QApplication([])

    src_dir = tmp_path / "inputs"
    src_dir.mkdir()
    source_file = src_dir / "document.pdf"
    source_file.write_bytes(b"%PDF-source\n")

    exp_dir = tmp_path / "custom_exports"
    archived_dir = exp_dir / app.MERGE_SUBFOLDER_NAME
    archived_dir.mkdir(parents=True)
    archived_ocr = archived_dir / "document_ocred.pdf"
    Image.new("RGB", (5, 5), "white").save(archived_ocr, "PDF")

    # 1. Payload-Funktion direkt mit export_folder testen
    payload = app.build_job_export_payload(
        [{"path": str(source_file), "status": "done"}],
        "deu",
        export_folder=exp_dir,
    )
    assert len(payload["outputs"]) == 1
    output_entry = payload["outputs"][0]
    assert output_entry["output_exists"] is True
    assert output_entry["output_local_path"] == archived_ocr.as_posix()

    # 2. GUI export_job_manifest mit konfiguriertem export_folder testen
    gui = app.OCRConverterGUI()
    try:
        gui.export_folder = str(exp_dir)
        gui.list_widget.add_file(str(source_file))
        item = gui.list_widget.item(0)
        item.setData(Qt.UserRole + 1, "done")
        item.setData(Qt.UserRole + 2, "OCR erfolgreich")

        target_json = tmp_path / "manifest.json"
        written = gui.export_job_manifest(target_path=target_json, show_feedback=False)
        assert written == target_json
        manifest_data = json.loads(target_json.read_text(encoding="utf-8"))
        gui_output = manifest_data["outputs"][0]
        assert gui_output["output_exists"] is True
        assert gui_output["output_local_path"] == archived_ocr.as_posix()
    finally:
        gui.close()


def test_bs10_merge_selected_updates_output_path_with_custom_target_folder(tmp_path):
    """BS-10: merge_selected aktualisiert UserRole+4 auch dann auf den Archivpfad, wenn
    der Benutzer einen anderen Zielordner als gui.export_folder wählt.
    """
    from PIL import Image
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    import PDFtoPDFocr_2 as app

    _ = QApplication.instance() or QApplication([])
    gui = app.OCRConverterGUI()
    try:
        gui.export_folder = str(tmp_path / "configured_export_dir")
        (tmp_path / "configured_export_dir").mkdir()

        # Quelldateien und OCR-Ergebnisse im Eingabeordner
        in_dir = tmp_path / "incoming"
        in_dir.mkdir()
        for name in ("part1.pdf", "part2.pdf"):
            src = in_dir / name
            src.write_bytes(b"%PDF-doc\n")
            out = in_dir / f"{src.stem}_ocred.pdf"
            Image.new("RGB", (5, 5), "white").save(out, "PDF")
            gui.list_widget.add_file(str(src))
            item = gui.list_widget.item(gui.list_widget.count() - 1)
            item.setData(Qt.UserRole + 1, "done")
            item.setSelected(True)

        # Merge in einen abweichenden benutzerdefinierten Ordner
        custom_target_dir = tmp_path / "user_chosen_folder"
        custom_target_dir.mkdir()
        target_merged = custom_target_dir / "collective.pdf"

        result = gui.merge_selected(target_path=target_merged)
        assert result == target_merged
        assert target_merged.exists()

        # Beide Items müssen auf die in custom_target_dir/Einzeldateien verschobenen Dateien verweisen
        expected_subfolder = custom_target_dir / app.MERGE_SUBFOLDER_NAME
        for i in range(2):
            stored = gui.list_widget.item(i).data(Qt.UserRole + 4)
            assert stored is not None
            stored_path = Path(stored)
            assert stored_path.exists(), f"Stored path {stored_path} does not exist"
            assert stored_path.parent.resolve() == expected_subfolder.resolve()
    finally:
        gui.close()


def test_bs10_add_paths_from_arguments_tags_folder_batch(tmp_path):
    """BS-10: add_paths_from_arguments weist beim Hinzufügen von Ordnern batch_ids zu
    und registriert den Batch-Ordner für automatischen U5-Merge.
    """
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication
    import PDFtoPDFocr_2 as app

    _ = QApplication.instance() or QApplication([])
    gui = app.OCRConverterGUI()
    try:
        batch_dir = tmp_path / "folder_batch"
        batch_dir.mkdir()
        (batch_dir / "doc1.pdf").write_bytes(b"%PDF-1\n")
        (batch_dir / "doc2.pdf").write_bytes(b"%PDF-2\n")

        added = gui.add_paths_from_arguments([str(batch_dir)])
        assert added == 2
        assert gui.list_widget.count() == 2

        batch_id1 = gui.list_widget.item(0).data(Qt.UserRole + 3)
        batch_id2 = gui.list_widget.item(1).data(Qt.UserRole + 3)
        assert batch_id1 is not None and batch_id1 != ""
        assert batch_id1 == batch_id2
        assert gui._batch_folders.get(batch_id1) == str(batch_dir)
    finally:
        gui.close()

