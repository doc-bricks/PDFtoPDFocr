import codecs
import json
from unittest.mock import MagicMock

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

import PDFtoPDFocr_2 as app


def _qapp():
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication([])
    return instance


def test_build_job_export_payload_handles_missing_and_relative_paths(tmp_path):
    existing = tmp_path / "scan.pdf"
    existing.write_bytes(b"%PDF-1.4\n")

    payload = app.build_job_export_payload(
        [
            {"path": str(existing), "status": "done", "message": "OCR erfolgreich abgeschlossen."},
            {"path": "relative/missing.pdf", "status": "pending", "message": ""},
        ],
        "deu",
        created_at="2026-05-28T00:00:00Z",
    )

    assert payload["schema"] == "pdftopdfocr-job-v1"
    assert payload["created_at"] == "2026-05-28T00:00:00Z"
    assert payload["settings"]["dpi"] == 300

    existing_entry, missing_entry = payload["input_files"]
    assert existing_entry["local_path"] == existing.as_posix()
    assert existing_entry["size_bytes"] == existing.stat().st_size
    assert existing_entry["missing"] is False
    assert missing_entry["local_path"] == "relative/missing.pdf"
    assert missing_entry["size_bytes"] is None
    assert missing_entry["missing"] is True

    success_output, pending_output = payload["outputs"]
    assert success_output["status"] == "success"
    assert success_output["output_name"] == "scan_ocred.pdf"
    assert pending_output["status"] == "pending"
    assert pending_output["output_name"] == "missing_ocred.pdf"


def test_write_job_export_uses_utf8_without_bom(tmp_path):
    target = tmp_path / "job.json"
    payload = app.build_job_export_payload([], "eng", created_at="2026-05-28T00:00:00Z")

    written = app.write_job_export(target, payload)

    raw = written.read_bytes()
    assert written == target
    assert not raw.startswith(codecs.BOM_UTF8)
    assert json.loads(raw.decode("utf-8"))["schema"] == "pdftopdfocr-job-v1"


def test_build_job_export_payload_disambiguates_duplicate_file_names(tmp_path):
    first = tmp_path / "one" / "scan.pdf"
    second = tmp_path / "two" / "scan.pdf"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    first.write_bytes(b"%PDF-first\n")
    second.write_bytes(b"%PDF-second\n")

    payload = app.build_job_export_payload(
        [
            {"path": str(first), "status": "done", "message": "Erster Lauf"},
            {"path": str(second), "status": "error", "message": "Zweiter Lauf"},
        ],
        "deu",
        created_at="2026-06-04T00:00:00Z",
    )

    first_output, second_output = payload["outputs"]
    assert first_output["input_name"] == "scan.pdf"
    assert second_output["input_name"] == "scan.pdf"
    assert first_output["input_local_path"] == first.as_posix()
    assert second_output["input_local_path"] == second.as_posix()
    assert first_output["output_local_path"] != second_output["output_local_path"]


def test_export_job_manifest_supports_empty_project_state(tmp_path):
    _qapp()
    gui = app.OCRConverterGUI()

    target = tmp_path / "empty.json"
    written = gui.export_job_manifest(target_path=target, show_feedback=False)
    data = json.loads(target.read_text(encoding="utf-8"))

    assert written == target
    assert data["input_files"] == []
    assert data["outputs"] == []
    gui.close()


def test_export_job_manifest_collects_current_gui_status(tmp_path):
    _qapp()
    source = tmp_path / "scan.pdf"
    source.write_bytes(b"%PDF-1.4\n")
    output = tmp_path / "scan_ocred.pdf"
    output.write_bytes(b"%PDF-result\n")

    gui = app.OCRConverterGUI()
    gui.list_widget.add_file(str(source))
    item = gui.list_widget.item(0)
    item.setData(Qt.UserRole + 1, "done")
    item.setData(Qt.UserRole + 2, "OCR erfolgreich abgeschlossen.")

    target = tmp_path / "current-job.json"
    gui.export_job_manifest(target_path=target, show_feedback=False)
    data = json.loads(target.read_text(encoding="utf-8"))

    assert data["ocr_language"] == gui.lang_combo.currentText()
    assert data["outputs"][0]["status"] == "success"
    assert data["outputs"][0]["output_exists"] is True
    assert data["outputs"][0]["message"] == "OCR erfolgreich abgeschlossen."
    gui.close()


def test_file_list_delete_key_removes_selection_and_exposes_accessible_context(tmp_path):
    _qapp()
    first = tmp_path / "first.pdf"
    second = tmp_path / "second.pdf"
    first.write_bytes(b"%PDF-first\n")
    second.write_bytes(b"%PDF-second\n")

    gui = app.OCRConverterGUI()
    gui.show()
    gui.list_widget.add_file(str(first))
    gui.list_widget.add_file(str(second))

    assert gui.list_widget.accessibleName() == "PDF-Dateiliste"
    assert "Entf-Taste" in gui.list_widget.accessibleDescription()
    assert "Entf" in gui.btn_delete.toolTip()

    item = gui.list_widget.item(0)
    item.setSelected(True)
    gui.list_widget.setCurrentItem(item)
    gui.list_widget.setFocus()
    QTest.keyClick(gui.list_widget, Qt.Key_Delete)
    QApplication.processEvents()

    assert gui.list_widget.count() == 1
    assert gui.list_widget.item(0).data(Qt.UserRole) == str(second)
    gui.close()


def test_close_event_waits_for_running_worker():
    _qapp()
    gui = app.OCRConverterGUI()

    mock_worker = MagicMock()
    mock_worker.isRunning.return_value = True
    gui._ocr_worker = mock_worker

    mock_event = MagicMock()
    gui.closeEvent(mock_event)

    mock_worker.wait.assert_called_once()
    mock_event.accept.assert_called_once()

    gui._ocr_worker = None
    gui.close()


def test_ocr_worker_progress_uses_tr_for_localization():
    _qapp()
    app.set_language("en")

    emitted = []
    worker = app.OCRWorker(pending_paths=["scan.pdf"], lang="eng")
    worker.progress.connect(emitted.append)
    worker._ocr_pdf = lambda path, lang: True

    worker.run()

    app.set_language("de")

    assert len(emitted) == 1
    assert emitted[0].startswith("Processing:"), (
        f"Expected localized 'Processing:' but got: {emitted[0]!r}"
    )


def test_ocr_pdf_fallback_closes_src_pdf_before_unlink(tmp_path, monkeypatch):
    """Bug #3: src_pdf.close() muss vor os.unlink() im Fallback-Temp-Pfad kommen."""
    from PIL import Image as PILImage
    import pikepdf

    _qapp()
    worker = app.OCRWorker(pending_paths=[], lang="eng")

    fake_image = PILImage.new("RGB", (10, 10))
    monkeypatch.setattr("PDFtoPDFocr_2.convert_from_path", lambda *a, **kw: [fake_image])
    monkeypatch.setattr(
        "PDFtoPDFocr_2.pytesseract.image_to_pdf_or_hocr",
        lambda *a, **kw: b"%PDF-fake",
    )

    events = []
    mock_src_pdf = MagicMock()
    mock_src_pdf.pages = []
    mock_src_pdf.close = lambda: events.append("close")

    open_calls = [0]

    def patched_open(source, *a, **kw):
        open_calls[0] += 1
        if open_calls[0] == 1:
            raise Exception("forced BytesIO failure")
        return mock_src_pdf

    monkeypatch.setattr(pikepdf.Pdf, "open", patched_open)

    _original_unlink = app.os.unlink

    def patched_unlink(p):
        events.append("unlink")
        _original_unlink(p)

    monkeypatch.setattr(app.os, "unlink", patched_unlink)

    src = tmp_path / "test.pdf"
    src.write_bytes(b"%PDF-1.4\n")
    worker._ocr_pdf(str(src), "eng")

    assert "close" in events, "src_pdf.close() wurde im Fallback-Pfad nie aufgerufen"
    assert "unlink" in events, "os.unlink() wurde nie aufgerufen — Temp-Datei wurde nicht gelöscht"
    assert events.index("close") < events.index("unlink"), (
        f"src_pdf.close() muss vor os.unlink() kommen; Reihenfolge war: {events}"
    )


def test_ocr_pdf_returns_false_when_all_pages_yield_empty_bytes(tmp_path, monkeypatch):
    """Bug #4: Wenn pytesseract für alle Seiten leere Bytes liefert,
    darf _ocr_pdf KEINE leere PDF speichern und muss False zurückgeben."""
    from PIL import Image as PILImage

    _qapp()
    worker = app.OCRWorker(pending_paths=[], lang="eng")

    fake_image = PILImage.new("RGB", (10, 10))
    monkeypatch.setattr("PDFtoPDFocr_2.convert_from_path", lambda *a, **kw: [fake_image])
    # Simuliere leere Bytes für alle Seiten
    monkeypatch.setattr(
        "PDFtoPDFocr_2.pytesseract.image_to_pdf_or_hocr",
        lambda *a, **kw: b"",
    )

    src = tmp_path / "empty_ocr.pdf"
    src.write_bytes(b"%PDF-1.4\n")

    result = worker._ocr_pdf(str(src), "eng")

    assert result is False, "Erwartet False, wenn OCR keine Seiten erzeugt"
    dst = tmp_path / "empty_ocr_ocred.pdf"
    assert not dst.exists(), "Es darf keine leere Ausgabe-PDF angelegt werden"


def test_ensure_tesseract_download_leaves_no_partial_file_on_network_error(
    tmp_path, monkeypatch
):
    """Bug #5: Bei einem Netzwerkabbruch während des Downloads darf keine
    abgeschnittene .traineddata-Datei auf der Platte verbleiben."""

    # Tesseract-Binary simulieren
    exe_name = "tesseract.exe" if app.os.name == "nt" else "tesseract"
    portable_dir = tmp_path / "tesseract_portable"
    tessdata_dir = portable_dir / "tessdata"
    tessdata_dir.mkdir(parents=True)
    fake_exe = portable_dir / exe_name
    fake_exe.write_text("", encoding="utf-8")

    module_file = tmp_path / "PDFtoPDFocr_2.py"
    module_file.write_text("# stub\n", encoding="utf-8")
    monkeypatch.setattr(app, "__file__", str(module_file))
    monkeypatch.delattr(app.sys, "_MEIPASS", raising=False)
    monkeypatch.setattr(app.shutil, "which", lambda name: None)
    monkeypatch.delenv("TESSDATA_PREFIX", raising=False)

    # Simuliere eine Response, deren .raw.read() einen Fehler wirft
    class BrokenRaw:
        def read(self, amt=-1):
            raise OSError("simulated network drop")

    class FakeResponse:
        status_code = 200
        raw = BrokenRaw()

    monkeypatch.setattr(app.requests, "get", lambda *a, **kw: FakeResponse())

    # QMessageBox.critical unterdrücken
    monkeypatch.setattr(app.QMessageBox, "critical", lambda *a, **kw: None)
    monkeypatch.setattr(app.QMessageBox, "information", lambda *a, **kw: None)

    result = app.ensure_tesseract("fra")

    target = tessdata_dir / "fra.traineddata"
    assert result is False, "ensure_tesseract muss False zurückgeben bei Netzwerkfehler"
    assert not target.exists(), (
        "Keine abgeschnittene .traineddata-Datei darf nach Netzwerkfehler auf der Platte liegen"
    )
