"""
Tests for Windows Store materials and preflight readiness in PDFtoPDFocr.
"""

import json
from pathlib import Path
from scripts.check_store_readiness import (
    check_documentation_files,
    check_store_icon_assets,
    check_store_package_json,
    run_store_readiness_check,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_store_package_json_validity():
    errors = check_store_package_json(PROJECT_ROOT)
    assert errors == [], f"store_package.json failed validation: {errors}"


def test_store_package_json_content():
    p = PROJECT_ROOT / "store_package.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["app_name"] == "PDFtoPDFocr"
    assert data["publisher"] == "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
    assert data["identity_name"] == "Geiger.PDFtoPDFocr"
    assert "internetClient" in data["capabilities"]
    assert "runFullTrust" in data["capabilities"]


def test_documentation_files_exist():
    errors = check_documentation_files(PROJECT_ROOT)
    assert errors == [], f"Documentation check failed: {errors}"


def test_store_icon_assets_exist():
    errors = check_store_icon_assets(PROJECT_ROOT)
    assert errors == [], f"Store icons check failed: {errors}"


def test_full_store_readiness_preflight():
    success, errors = run_store_readiness_check(PROJECT_ROOT)
    assert success is True, f"Full store readiness preflight failed: {errors}"
    assert errors == []
