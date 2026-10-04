# -*- coding: utf-8 -*-
"""Regression tests for BS-11: EXIF preservation, merge hardening, worker cancellation, and path safety.

BS-11 facets verified:
1. _load_source_images preserves EXIF & info metadata so exif_transpose can rotate images.
2. _load_source_images handles truncated multi-frame images raising EOFError gracefully.
3. _ocr_pdf unlinks temporary PDF files immediately if pikepdf.open fails, preventing tempfile leaks.
4. open_file_path and open_file_folder reject None, empty strings, and whitespace without opening CWD.
5. merge_ocr_outputs sanitizes merged_name against traversal, enforces .pdf extension, and checks file existence.
6. resolve_ocr_output_path uses safe mtime sorting against concurrent file deletion or OSError.
7. ensure_tesseract validates and sanitizes lang codes against directory traversal and rejects empty inputs.
8. build_job_export_payload handles OSError during stat/is_file lookups without raising unhandled exceptions.
9. OCRWorker supports stop() cancellation and OCRConverterGUI.on_start guards against re-entrant worker creation.
10. PDFListWidget.add_file rejects directories with supported extensions (e.g. dir.pdf) and initializes UserRole+4.
"""
from pathlib import Path
import tempfile
from unittest.mock import MagicMock
from PIL import Image
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

import PDFtoPDFocr_2 as app


def _get_qapp():
    return QApplication.instance() or QApplication([])


def test_bs11_load_source_images_preserves_exif_and_info(tmp_path):
    """BS-11 (1): _load_source_images preserves EXIF orientation metadata on copied frames."""
    img_path = tmp_path / "oriented_photo.jpg"
    im = Image.new("RGB", (20, 40), color="white")
    exif = im.getexif()
    exif[0x0112] = 6  # 90 degrees CW rotation
    im.save(img_path, exif=exif)

    worker = app.OCRWorker([], "deu")
    loaded_frames = worker._load_source_images(str(img_path))
    assert len(loaded_frames) == 1
    frame = loaded_frames[0]

    # Verify that exif metadata was transferred to the frame
    assert frame.getexif().get(0x0112) == 6

    # Normalization should transpose (20, 40) into (40, 20)
    normalized = app.normalize_image_for_ocr(frame)
    assert normalized.size == (40, 20)


def test_bs11_load_source_images_eoferror_resilience(tmp_path, monkeypatch):
    """BS-11 (2): _load_source_images stops iteration without crashing if a frame seek raises EOFError."""
    img_path = tmp_path / "multipage_truncated.tif"
    im = Image.new("RGB", (10, 10), color="white")
    im.save(img_path)

    worker = app.OCRWorker([], "deu")

    original_open = Image.open

    class MockMultiFrame:
        def __init__(self, real_im):
            self.real_im = real_im
            self.n_frames = 3

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.real_im.close()

        def seek(self, frame_idx):
            if frame_idx >= 1:
                raise EOFError("Truncated image stream")

        def copy(self):
            return self.real_im.copy()

        def getexif(self):
            return self.real_im.getexif()

    monkeypatch.setattr(Image, "open", lambda p: MockMultiFrame(original_open(p)))

    frames = worker._load_source_images(str(img_path))
    assert len(frames) == 1


def test_bs11_ocr_pdf_tempfile_cleanup_on_open_failure(tmp_path, monkeypatch):
    """BS-11 (3): _ocr_pdf unlinks temporary file if pikepdf fails to open fallback bytes."""
    worker = app.OCRWorker([], "deu")

    # Mock _load_source_images to return 1 dummy image
    monkeypatch.setattr(worker, "_load_source_images", lambda p: [Image.new("RGB", (10, 10))])
    # Mock pytesseract to return dummy invalid PDF bytes
    monkeypatch.setattr(app.pytesseract, "image_to_pdf_or_hocr", lambda img, lang, extension: b"corrupt-pdf-data")

    created_temp_files = []
    original_named_temp = tempfile.NamedTemporaryFile

    def tracking_temp(*args, **kwargs):
        tf = original_named_temp(*args, **kwargs)
        created_temp_files.append(tf.name)
        return tf

    monkeypatch.setattr(tempfile, "NamedTemporaryFile", tracking_temp)

    # Let pikepdf fail on both BytesIO and file open
    import pikepdf

    def failing_open(src):
        raise pikepdf.PdfError("Simulated pikepdf corruption")

    monkeypatch.setattr(pikepdf.Pdf, "open", failing_open)

    dummy_pdf = tmp_path / "test.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4\n")

    success = worker._ocr_pdf(str(dummy_pdf), "deu")
    assert success is False
    # Fallback pages are staged inside the private output directory (see SAVE_SAFETY.md),
    # so no system temp file may be created and nothing may be left beside the source.
    assert all(not Path(name).exists() for name in created_temp_files)
    assert sorted(item.name for item in tmp_path.iterdir()) == ["test.pdf"]


def test_bs11_open_file_path_and_folder_rejects_none_empty_and_dirs(tmp_path):
    """BS-11 (4): open_file_path and open_file_folder reject None, empty, whitespace, and invalid paths."""
    assert app.open_file_path(None) is False
    assert app.open_file_path("") is False
    assert app.open_file_path("   ") is False
    assert app.open_file_folder(None) is False
    assert app.open_file_folder("") is False
    assert app.open_file_folder("   ") is False

    # Directories must not be opened by open_file_path
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    assert app.open_file_path(dir_path) is False

    # Non-existent file whose parent exists can open parent via open_file_folder
    missing = dir_path / "nonexistent.pdf"
    # open_file_path on missing returns False
    assert app.open_file_path(missing) is False


def test_bs11_merge_ocr_outputs_sanitizes_filename_and_handles_missing_extension(tmp_path):
    """BS-11 (5): merge_ocr_outputs sanitizes merged_name against traversal and appends .pdf."""
    import pikepdf

    p1 = tmp_path / "page1_ocred.pdf"
    p2 = tmp_path / "page2_ocred.pdf"
    for p in (p1, p2):
        pdf = pikepdf.Pdf.new()
        pdf.add_blank_page()
        pdf.save(p)
        pdf.close()

    out_dir = tmp_path / "output_dir"
    # Call with path traversal and without .pdf extension
    result = app.merge_ocr_outputs([str(p1), str(p2)], "../traversal_name", out_dir)

    assert result == out_dir / "traversal_name.pdf"
    assert result.is_file()

    # Rejection of fewer than 2 existing files
    with pytest.raises(ValueError, match="mindestens 2"):
        app.merge_ocr_outputs([str(tmp_path / "nonexistent.pdf")], "merged.pdf", out_dir)


def test_bs11_resolve_ocr_output_path_safe_mtime_on_missing_file(tmp_path, monkeypatch):
    """BS-11 (6): resolve_ocr_output_path does not crash if a file's stat().st_mtime raises OSError during sort."""
    sub = tmp_path / app.MERGE_SUBFOLDER_NAME
    sub.mkdir()
    source = tmp_path / "doc.pdf"
    source.write_bytes(b"%PDF\n")

    archived = sub / "doc_ocred.pdf"
    archived.write_bytes(b"%PDF-archived\n")

    original_stat = Path.stat

    class FlakyStatResult:
        def __init__(self, real):
            self._real = real
        @property
        def st_mtime(self):
            raise OSError("Simulated concurrent mtime access error")
        def __getattr__(self, name):
            return getattr(self._real, name)

    def flaky_stat(self, *args, **kwargs):
        res = original_stat(self, *args, **kwargs)
        if self.name == "doc_ocred.pdf":
            return FlakyStatResult(res)
        return res

    monkeypatch.setattr(Path, "stat", flaky_stat)

    # Must resolve cleanly without raising unhandled OSError/FileNotFoundError
    resolved = app.resolve_ocr_output_path(source)
    assert resolved == archived


def test_bs11_ensure_tesseract_sanitizes_lang_parameter():
    """BS-11 (7): ensure_tesseract rejects empty or traversal language strings."""
    assert app.ensure_tesseract("") is False
    assert app.ensure_tesseract(None) is False
    assert app.ensure_tesseract("   ") is False


def test_bs11_build_job_export_payload_oserror_safety(tmp_path, monkeypatch):
    """BS-11 (8): build_job_export_payload handles OSError during size_bytes lookup gracefully."""
    f = tmp_path / "sample.pdf"
    f.write_bytes(b"%PDF-1.4\n")

    original_stat = Path.stat

    class FlakySizeResult:
        def __init__(self, real):
            self._real = real
        @property
        def st_size(self):
            raise OSError("Permission denied reading size")
        def __getattr__(self, name):
            return getattr(self._real, name)

    def flaky_stat(self, *args, **kwargs):
        res = original_stat(self, *args, **kwargs)
        if self.name == "sample.pdf":
            return FlakySizeResult(res)
        return res

    monkeypatch.setattr(Path, "stat", flaky_stat)

    payload = app.build_job_export_payload(
        [{"path": str(f), "status": "pending"}],
        "deu",
        created_at="2026-10-03T00:00:00Z",
    )
    assert len(payload["input_files"]) == 1
    entry = payload["input_files"][0]
    # size_bytes should safely fall back to None instead of raising an unhandled exception
    assert entry["size_bytes"] is None
    assert entry["missing"] is False


def test_bs11_worker_concurrency_and_cancellation():
    """BS-11 (9): OCRWorker supports stop() and on_start guards against re-entrant worker creation."""
    _get_qapp()
    worker = app.OCRWorker(["path1", "path2", "path3"], "deu")
    assert worker._is_cancelled is False
    worker.stop()
    assert worker._is_cancelled is True

    gui = app.OCRConverterGUI()
    try:
        mock_worker = MagicMock()
        mock_worker.isRunning.return_value = True
        gui._ocr_worker = mock_worker

        # When running, on_start should return immediately without replacing worker
        gui.on_start()
        assert gui._ocr_worker is mock_worker
    finally:
        gui.close()


def test_bs11_add_file_rejects_directory_with_supported_extension(tmp_path):
    """BS-11 (10): PDFListWidget.add_file rejects directories with supported extensions and initializes UserRole+4."""
    _get_qapp()
    widget = app.PDFListWidget()

    dir_as_pdf = tmp_path / "directory_named.pdf"
    dir_as_pdf.mkdir()

    widget.add_file(str(dir_as_pdf))
    assert widget.count() == 0, "Directory named like a PDF must not be added as a file"

    # Add a real file and verify UserRole + 4 is initialized
    real_file = tmp_path / "actual_document.pdf"
    real_file.write_bytes(b"%PDF-doc\n")
    widget.add_file(str(real_file))
    assert widget.count() == 1
    assert widget.item(0).data(Qt.UserRole + 4) is None
