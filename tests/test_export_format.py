import codecs
import json

from PySide6.QtCore import Qt
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
