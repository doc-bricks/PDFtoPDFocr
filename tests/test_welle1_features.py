"""Regressionstests fuer das Welle-1-Feature-Paket (U1-U5, 2026-07-24).

U1: Bild-Import (JPG/PNG/TIFF) -> durchsuchbares PDF.
U2/U3: Stapeln/Mergen per Kontextmenu, Ablage (Einzelseiten-Unterordner + Sammel-PDF).
U4: Konfigurierbarer Exportordner, Fallback = Quellordner.
U5: Ganze Ordner reinziehbar = automatischer Merge-Modus.
"""

import io

import pikepdf
from PIL import Image
from PySide6.QtCore import Qt

import PDFtoPDFocr_2 as app


def _qapp():
    from PySide6.QtWidgets import QApplication

    instance = QApplication.instance()
    if instance is None:
        instance = QApplication([])
    return instance


def _fake_ocr_pdf_bytes(size=(5, 5)) -> bytes:
    """Erzeugt echte, minimal gueltige Ein-Seiten-PDF-Bytes via Pillow (kein Tesseract noetig)."""
    buf = io.BytesIO()
    Image.new("RGB", size, "white").save(buf, "PDF")
    return buf.getvalue()


# ===== U1: Bild-Import =====


def test_supported_exts_include_common_image_formats():
    for ext in (".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff"):
        assert ext in app.SUPPORTED_EXTS


def test_ocr_pdf_handles_image_input_without_pdf_rasterization(tmp_path, monkeypatch):
    """U1: JPG-Input muss OCR-PDF erzeugen, ohne convert_from_path (PDF-Rasterung via Poppler)."""
    _qapp()
    worker = app.OCRWorker(pending_paths=[], lang="eng")

    def _must_not_be_called(*a, **kw):
        raise AssertionError("convert_from_path darf fuer Bild-Input nicht aufgerufen werden")

    monkeypatch.setattr("PDFtoPDFocr_2.convert_from_path", _must_not_be_called)
    monkeypatch.setattr(
        "PDFtoPDFocr_2.pytesseract.image_to_pdf_or_hocr",
        lambda *a, **kw: _fake_ocr_pdf_bytes(),
    )

    src = tmp_path / "scan.jpg"
    Image.new("RGB", (20, 20), "white").save(src, "JPEG")

    result = worker._ocr_pdf(str(src), "eng")

    assert result is True
    dst = tmp_path / "scan_ocred.pdf"
    assert dst.exists()
    with pikepdf.Pdf.open(dst) as pdf:
        assert len(pdf.pages) == 1


def test_ocr_pdf_handles_multipage_tiff_one_page_per_frame(tmp_path, monkeypatch):
    """U1: Mehrseitige TIFF-Datei erzeugt eine OCR-PDF mit einer Seite pro Frame."""
    _qapp()
    worker = app.OCRWorker(pending_paths=[], lang="eng")

    def _must_not_be_called(*a, **kw):
        raise AssertionError("convert_from_path darf fuer TIFF-Input nicht aufgerufen werden")

    monkeypatch.setattr("PDFtoPDFocr_2.convert_from_path", _must_not_be_called)
    monkeypatch.setattr(
        "PDFtoPDFocr_2.pytesseract.image_to_pdf_or_hocr",
        lambda *a, **kw: _fake_ocr_pdf_bytes(),
    )

    src = tmp_path / "scan.tiff"
    frame1 = Image.new("RGB", (10, 10), "white")
    frame2 = Image.new("RGB", (10, 10), "black")
    frame1.save(src, save_all=True, append_images=[frame2])

    result = worker._ocr_pdf(str(src), "eng")

    assert result is True
    dst = tmp_path / "scan_ocred.pdf"
    with pikepdf.Pdf.open(dst) as pdf:
        assert len(pdf.pages) == 2


def test_add_file_accepts_image_extensions(tmp_path):
    _qapp()
    widget = app.PDFListWidget()
    img_path = tmp_path / "photo.png"
    Image.new("RGB", (5, 5), "white").save(img_path, "PNG")

    widget.add_file(str(img_path))

    assert widget.count() == 1
    assert widget.item(0).data(Qt.UserRole) == str(img_path)


# ===== U4: Exportordner-Fallback =====


def test_resolve_export_folder_uses_configured_folder_when_valid(tmp_path):
    configured = tmp_path / "exports"
    configured.mkdir()
    source = tmp_path / "src" / "scan.pdf"

    assert app.resolve_export_folder(str(source), str(configured)) == configured


def test_resolve_export_folder_falls_back_to_source_folder(tmp_path):
    source = tmp_path / "src" / "scan.pdf"

    assert app.resolve_export_folder(str(source), None) == source.parent
    assert app.resolve_export_folder(str(source), str(tmp_path / "missing")) == source.parent


# ===== U2/U3: merge_ocr_outputs (Kernfunktion) =====


def test_merge_ocr_outputs_creates_collective_pdf_and_archives_pages(tmp_path):
    export_folder = tmp_path / "out"
    a = tmp_path / "a_ocred.pdf"
    b = tmp_path / "b_ocred.pdf"
    Image.new("RGB", (5, 5), "white").save(a, "PDF")
    Image.new("RGB", (5, 5), "white").save(b, "PDF")

    merged_path = app.merge_ocr_outputs([str(a), str(b)], "merged.pdf", export_folder)

    assert merged_path == export_folder / "merged.pdf"
    with pikepdf.Pdf.open(merged_path) as pdf:
        assert len(pdf.pages) == 2

    subfolder = export_folder / app.MERGE_SUBFOLDER_NAME
    assert (subfolder / "a_ocred.pdf").exists()
    assert (subfolder / "b_ocred.pdf").exists()
    assert not a.exists()
    assert not b.exists()


def test_merge_ocr_outputs_requires_at_least_two_files(tmp_path):
    a = tmp_path / "a_ocred.pdf"
    Image.new("RGB", (5, 5), "white").save(a, "PDF")

    try:
        app.merge_ocr_outputs([str(a)], "merged.pdf", tmp_path / "out")
        assert False, "erwartete ValueError bei nur einer Datei"
    except ValueError:
        pass
    assert a.exists(), "bei fehlgeschlagenem Merge duerfen keine Dateien verschoben werden"


def test_merge_ocr_outputs_disambiguates_name_collisions_in_subfolder(tmp_path):
    """Zwei Quelldateien mit gleichem Basisnamen aus unterschiedlichen Ordnern."""
    export_folder = tmp_path / "out"
    dir1 = tmp_path / "one"
    dir2 = tmp_path / "two"
    dir1.mkdir()
    dir2.mkdir()
    a = dir1 / "scan_ocred.pdf"
    b = dir2 / "scan_ocred.pdf"
    Image.new("RGB", (5, 5), "white").save(a, "PDF")
    Image.new("RGB", (5, 5), "white").save(b, "PDF")

    app.merge_ocr_outputs([str(a), str(b)], "merged.pdf", export_folder)

    subfolder = export_folder / app.MERGE_SUBFOLDER_NAME
    archived = list(subfolder.glob("*.pdf"))
    assert len(archived) == 2, "beide archivierten Dateien muessen erhalten bleiben (kein Ueberschreiben)"


# ===== U2: merge_selected (GUI-Ebene, per target_path testbar wie export_job_manifest) =====


def test_merge_selected_creates_collective_pdf_for_selected_done_items(tmp_path):
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        for name in ("a.pdf", "b.pdf"):
            src = tmp_path / name
            src.write_bytes(b"%PDF-1.4\n")
            out = tmp_path / f"{src.stem}_ocred.pdf"
            Image.new("RGB", (5, 5), "white").save(out, "PDF")
            gui.list_widget.add_file(str(src))
            item = gui.list_widget.item(gui.list_widget.count() - 1)
            item.setData(Qt.UserRole + 1, "done")
            item.setSelected(True)

        target = tmp_path / "merged.pdf"
        result = gui.merge_selected(target_path=target)

        assert result == target
        with pikepdf.Pdf.open(target) as pdf:
            assert len(pdf.pages) == 2
        subfolder = tmp_path / app.MERGE_SUBFOLDER_NAME
        assert (subfolder / "a_ocred.pdf").exists()
        assert (subfolder / "b_ocred.pdf").exists()
    finally:
        gui.close()


def test_merge_selected_returns_none_when_fewer_than_two_done_items(tmp_path, monkeypatch):
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        monkeypatch.setattr(app.QMessageBox, "information", lambda *a, **kw: None)
        src = tmp_path / "a.pdf"
        src.write_bytes(b"%PDF-1.4\n")
        gui.list_widget.add_file(str(src))
        item = gui.list_widget.item(0)
        item.setData(Qt.UserRole + 1, "pending")
        item.setSelected(True)

        result = gui.merge_selected(target_path=tmp_path / "merged.pdf")

        assert result is None
    finally:
        gui.close()


# ===== U5: Ordner-Drop = automatischer Merge =====


def test_add_folder_tags_items_with_batch_id(tmp_path):
    _qapp()
    widget = app.PDFListWidget()
    folder = tmp_path / "scans"
    folder.mkdir()
    for name in ("p1.jpg", "p2.jpg"):
        Image.new("RGB", (5, 5), "white").save(folder / name, "JPEG")

    widget.add_folder(str(folder), batch_id="batch-1")

    assert widget.count() == 2
    for i in range(widget.count()):
        assert widget.item(i).data(Qt.UserRole + 3) == "batch-1"


def test_auto_merge_completed_batches_merges_once_all_files_done(tmp_path):
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        folder = tmp_path / "scans"
        folder.mkdir()
        sources = []
        for name in ("p1.jpg", "p2.jpg"):
            src = folder / name
            Image.new("RGB", (5, 5), "white").save(src, "JPEG")
            sources.append(src)
            gui.list_widget.add_file(str(src), batch_id="batch-1")
        gui._register_batch_folder("batch-1", str(folder))

        # Noch nicht alle Dateien fertig -> darf noch nicht mergen.
        gui.list_widget.item(0).setData(Qt.UserRole + 1, "done")
        Image.new("RGB", (5, 5), "white").save(folder / "p1_ocred.pdf", "PDF")
        gui._auto_merge_completed_batches()
        assert not (folder / "scans_merged.pdf").exists()

        # Zweite Datei fertigstellen -> Batch ist komplett, Auto-Merge greift.
        gui.list_widget.item(1).setData(Qt.UserRole + 1, "done")
        Image.new("RGB", (5, 5), "white").save(folder / "p2_ocred.pdf", "PDF")
        gui._auto_merge_completed_batches()

        merged = folder / "scans_merged.pdf"
        assert merged.exists()
        with pikepdf.Pdf.open(merged) as pdf:
            assert len(pdf.pages) == 2
        assert "batch-1" in gui._merged_batches
    finally:
        gui.close()


def test_auto_merge_does_not_merge_twice(tmp_path):
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        folder = tmp_path / "scans"
        folder.mkdir()
        for name in ("p1.jpg", "p2.jpg"):
            src = folder / name
            Image.new("RGB", (5, 5), "white").save(src, "JPEG")
            gui.list_widget.add_file(str(src), batch_id="batch-1")
        gui._register_batch_folder("batch-1", str(folder))
        for i in range(2):
            gui.list_widget.item(i).setData(Qt.UserRole + 1, "done")
        Image.new("RGB", (5, 5), "white").save(folder / "p1_ocred.pdf", "PDF")
        Image.new("RGB", (5, 5), "white").save(folder / "p2_ocred.pdf", "PDF")

        gui._auto_merge_completed_batches()
        merged = folder / "scans_merged.pdf"
        assert merged.exists()

        # Zweiter Aufruf darf nicht erneut ueber bereits verschobene Einzeldateien stolpern.
        gui._auto_merge_completed_batches()
    finally:
        gui.close()


# ===== U4: Persistenz (config.json, gleicher Mechanismus wie U6 Sprachwahl) =====


def test_export_folder_roundtrip(tmp_path, monkeypatch):
    cfg = tmp_path / "PDFtoPDFocr"
    monkeypatch.setattr(app, "_ui_config_dir", lambda: cfg)

    assert app.load_export_folder() is None

    target = tmp_path / "exports"
    assert app.save_export_folder(str(target)) is True
    assert app.load_export_folder() == str(target)

    assert app.save_export_folder(None) is True
    assert app.load_export_folder() is None


def test_save_export_folder_preserves_ui_language_key(tmp_path, monkeypatch):
    cfg = tmp_path / "cfgx"
    cfg.mkdir()
    (cfg / "config.json").write_text('{"ui_language": "en"}', encoding="utf-8")
    monkeypatch.setattr(app, "_ui_config_dir", lambda: cfg)

    assert app.save_export_folder(str(tmp_path)) is True

    import json

    data = json.loads((cfg / "config.json").read_text(encoding="utf-8"))
    assert data["export_folder"] == str(tmp_path)
    assert data["ui_language"] == "en"


# ===== U4: GUI-Ebene Exportordner =====


def test_export_folder_defaults_to_none_when_not_configured(tmp_path):
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        assert gui.export_folder is None
        assert app.tr("label_export_folder_default") in gui.export_folder_label.text()
    finally:
        gui.close()


def test_on_reset_export_folder_clears_configured_value(tmp_path):
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        gui.export_folder = str(tmp_path)
        app.save_export_folder(str(tmp_path))

        gui.on_reset_export_folder()

        assert gui.export_folder is None
        assert app.load_export_folder() is None
    finally:
        gui.close()
