"""Security, licensing, dependency floor, and privacy contract tests for PDFtoPDFocr."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dependency_security_minimum_floors() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    dev_requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")

    # Minimum secure floors in pyproject.toml
    assert "requests>=2.33.1" in pyproject
    assert "Pillow>=10.4.0" in pyproject
    assert "pikepdf>=8.15.1" in pyproject
    assert "pdf2image>=1.17.0" in pyproject
    assert "pytesseract>=0.3.13" in pyproject

    # Minimum secure floors in requirements.txt
    assert "requests>=2.33.1" in requirements
    assert "Pillow>=10.4.0" in requirements
    assert "pikepdf>=8.15.1" in requirements
    assert "pdf2image>=1.17.0" in requirements
    assert "pytesseract>=0.3.13" in requirements

    # Minimum secure floors in requirements-dev.txt
    assert "pytest>=9.1.1" in dev_requirements


def test_third_party_license_inventory_completeness() -> None:
    tp_file = ROOT / "THIRD_PARTY_LICENSES.txt"
    assert tp_file.exists()
    tp_text = tp_file.read_text(encoding="utf-8")

    assert "Stand: 2026-08-21" in tp_text
    required_components = [
        "PySide6",
        "Qt6",
        "pytesseract",
        "Pillow",
        "pdf2image",
        "Poppler",
        "pikepdf",
        "QPDF",
        "requests",
        "urllib3",
        "certifi",
        "charset-normalizer",
        "idna",
        "packaging",
        "Tesseract OCR",
        "Leptonica",
    ]
    for comp in required_components:
        assert comp in tp_text, f"Missing third party license declaration for: {comp}"


def test_no_hardcoded_user_paths_in_repo() -> None:
    suspicious = []
    forbidden = "C:" + "\\Users\\"
    forbidden_fwd = "C:" + "/Users/"
    for py_file in ROOT.rglob("*.py"):
        if py_file == Path(__file__):
            continue
        if any(part in py_file.parts for part in (".venv", "venv", ".build_venv", "build", "dist", "_archive")):
            continue
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        if forbidden in text or forbidden_fwd in text:
            suspicious.append(py_file.name)
    assert not suspicious, f"Hardcoded user paths found in: {suspicious}"


def test_no_plaintext_secrets_or_api_keys() -> None:
    secret_patterns = [
        re.compile(r"(?i)(?:bearer|token|secret|password|api[_-]?key)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,}['\"]"),
        re.compile(r"ghp_[a-zA-Z0-9]{36}"),
        re.compile(r"gho_[a-zA-Z0-9]{36}"),
    ]
    violations = []
    for f in LOCAL_files_iter():
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pat in secret_patterns:
            if pat.search(text):
                violations.append(f.name)
    assert not violations, f"Plaintext secrets detected in: {violations}"


def LOCAL_files_iter():
    skip_suffixes = {
        ".png", ".ico", ".jpg", ".jpeg", ".exe", ".pdf", ".traineddata",
        ".zip", ".msix", ".msixupload", ".appx", ".appxupload", ".tar",
        ".gz", ".7z", ".dll", ".so", ".dylib", ".pyd", ".pyc"
    }
    for f in ROOT.rglob("*"):
        if not f.is_file():
            continue
        if any(part in f.parts for part in (".git", ".pytest_cache", ".ruff_cache", "assets", "store_assets", "README", "build", "dist")):
            continue
        if f.suffix.lower() in skip_suffixes:
            continue
        if f.stat().st_size > 2_000_000:
            continue
        yield f


def test_gitignore_security_and_conflict_rules() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore
    assert "credentials.json" in gitignore
    assert "token.json" in gitignore
    assert "*.pem" in gitignore
    assert "*.key" in gitignore
    assert "LOCK*.txt" in gitignore
    assert "*-WORKSTATION-LG*" in gitignore
    assert "*-ASUS-GEI*" in gitignore
    assert "*.bak" in gitignore
