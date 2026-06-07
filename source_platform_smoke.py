#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Source-platform smoke test for PDFtoPDFocr (Linux + macOS).

Verifies imports, core logic, and headless GUI startup without requiring
Tesseract or Poppler system binaries.
Run via:  python source_platform_smoke.py
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> int:
    print("=== PDFtoPDFocr source-platform smoke ===\n")

    try:
        # ── Check 1: stdlib imports ───────────────────────────────────────────
        print("Check 1: stdlib imports")
        import io, logging, shutil  # noqa: F401,E401
        print("PASS: stdlib imports\n")

        # ── Check 2: PySide6 + OCR Python libs ───────────────────────────────
        print("Check 2: PySide6 + OCR Python libs import")
        from PySide6.QtWidgets import QApplication  # noqa: F401
        from PySide6.QtCore import QThread, Signal  # noqa: F401
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401
        from pdf2image import convert_from_path  # noqa: F401
        import pikepdf  # noqa: F401
        import requests  # noqa: F401
        print("PASS: PySide6 + OCR libs\n")

        # ── Check 3: app module loads + i18n ─────────────────────────────────
        print("Check 3: app module loads + i18n functions")
        sys.path.insert(0, str(PROJECT_ROOT))
        import PDFtoPDFocr_2 as app_mod
        app_mod.set_language("en")
        title_en = app_mod.tr("window_title")
        app_mod.set_language("de")
        title_de = app_mod.tr("window_title")
        assert isinstance(title_en, str) and title_en, \
            f"Expected non-empty EN title, got {title_en!r}"
        assert isinstance(title_de, str) and title_de, \
            f"Expected non-empty DE title, got {title_de!r}"
        assert app_mod.EXPORT_SCHEMA == "pdftopdfocr-job-v1", \
            f"Unexpected EXPORT_SCHEMA: {app_mod.EXPORT_SCHEMA!r}"
        assert app_mod.APP_VERSION, "APP_VERSION is empty"
        print(
            f"PASS: i18n OK (en={title_en!r}, de={title_de!r}), "
            f"EXPORT_SCHEMA={app_mod.EXPORT_SCHEMA!r}, "
            f"APP_VERSION={app_mod.APP_VERSION!r}\n"
        )

        # ── Check 4: build_job_export_payload ────────────────────────────────
        print("Check 4: build_job_export_payload")
        fake_entries = [{"path": "/tmp/dummy.pdf", "status": "done", "message": ""}]
        payload = app_mod.build_job_export_payload(
            fake_entries, ocr_language="eng", created_at="2026-01-01T00:00:00Z"
        )
        assert payload["schema"] == "pdftopdfocr-job-v1", \
            f"Bad schema: {payload['schema']!r}"
        assert payload["ocr_language"] == "eng", \
            f"Bad lang: {payload['ocr_language']!r}"
        assert isinstance(payload["input_files"], list), "input_files not a list"
        assert isinstance(payload["outputs"], list), "outputs not a list"
        assert payload["settings"]["dpi"] == 300, \
            f"Unexpected DPI: {payload['settings']['dpi']}"
        print(
            f"PASS: payload schema={payload['schema']!r} "
            f"dpi={payload['settings']['dpi']}\n"
        )

        # ── Check 5: write_job_export UTF-8 without BOM ──────────────────────
        print("Check 5: write_job_export UTF-8 roundtrip")
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir) / "test_export.json"
            app_mod.write_job_export(out_path, payload)
            raw = out_path.read_bytes()
            assert not raw.startswith(b"\xef\xbb\xbf"), "Unexpected UTF-8 BOM in output"
            loaded = json.loads(raw.decode("utf-8"))
            assert loaded["schema"] == "pdftopdfocr-job-v1", \
                f"Roundtrip schema mismatch: {loaded['schema']!r}"
        print("PASS: JSON written without BOM, schema round-trips correctly\n")

        # ── Check 6: headless OCRConverterGUI ────────────────────────────────
        print("Check 6: headless OCRConverterGUI startup")
        app = QApplication.instance() or QApplication(sys.argv)
        win = app_mod.OCRConverterGUI()
        win.show()
        win.close()
        del win
        app.processEvents()
        print("PASS: OCRConverterGUI opened and closed headlessly\n")

        print("=== ALL CHECKS PASSED ===")
        return EXIT_SUCCESS

    except AssertionError as exc:
        print(f"\nCHECK FAILED: {exc}")
        return EXIT_FAILURE
    except Exception as exc:
        print(f"\nUNEXPECTED ERROR: {exc}")
        import traceback
        traceback.print_exc()
        return EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
