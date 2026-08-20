"""Automated metadata, manifest, documentation, and security parity tests for PDFtoPDFocr."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_metadata() -> None:
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "PDFtoPDFocr"' in content
    assert 'version = "1.1.3"' in content
    assert 'requires-python = ">=3.10"' in content
    assert "https://github.com/doc-bricks/PDFtoPDFocr" in content
    assert 'license = { text = "MIT" }' in content


def test_readme_badges_and_links_parity() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    # English README badges & links
    assert "badge/license-MIT-green.svg" in readme_en
    assert "badge/version-1.1.3-blue.svg" in readme_en
    assert "badge/python-3.10%2B-blue.svg" in readme_en
    assert "badge/UI%20Engine-PySide6%20%7C%20Qt-41cd52.svg" in readme_en
    assert "badge/pytest-60%20passed-brightgreen.svg" in readme_en
    assert "badge/LLM--Ready-llms.txt-blueviolet.svg" in readme_en
    assert "badge/Ecosystem-doc--bricks-orange.svg" in readme_en
    assert "badge/Umbrella-open--bricks-blue.svg" in readme_en

    # German README badges & links
    assert "badge/lizenz-MIT-green.svg" in readme_de
    assert "badge/version-1.1.3-blue.svg" in readme_de
    assert "badge/python-3.10%2B-blue.svg" in readme_de
    assert "badge/UI%20Engine-PySide6%20%7C%20Qt-41cd52.svg" in readme_de
    assert "badge/pytest-60%20bestanden-brightgreen.svg" in readme_de
    assert "badge/LLM--Ready-llms.txt-blueviolet.svg" in readme_de
    assert "doc--bricks-orange.svg" in readme_de
    assert "open--bricks-blue.svg" in readme_de

    # Sibling ecosystem links in both
    for readme in (readme_en, readme_de):
        assert "https://github.com/doc-bricks/DokuReader" in readme
        assert "https://github.com/doc-bricks/MediaBrain" in readme
        assert "https://github.com/doc-bricks/UniversalDocsGrabber" in readme
        assert "https://github.com/doc-bricks/UniversalInvoiceMail" in readme
        assert "https://github.com/doc-bricks/UniversalMailCleaner" in readme
        assert "https://github.com/doc-bricks/CleanMarkdown" in readme
        assert "https://github.com/doc-bricks/LitZentrum" in readme
        assert "https://github.com/doc-bricks/MailProcessor" in readme
        assert "https://github.com/file-bricks/ProFiler" in readme
        assert "https://github.com/file-bricks/ExplorerPro" in readme
        assert "https://github.com/dev-bricks/DevCenter" in readme
        assert "https://github.com/dev-bricks/CodeBox" in readme
        assert "https://github.com/open-bricks" in readme


def test_llms_txt_currency_and_key_files() -> None:
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "Last-checked: 2026-08-21" in llms
    assert "https://github.com/doc-bricks/PDFtoPDFocr" in llms
    assert "MIT" in llms
    assert "60 verified tests" in llms or "60 passed" in llms
    assert "test_metadata.py" in llms


def test_security_policy_bilingual_and_invariants() -> None:
    sec = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "## Deutsch" in sec
    assert "## English" in sec
    assert "security@ellmos.ai" in sec
    assert "Zero-Egress" in sec
    assert "Non-Destructive" in sec or "Verlustfrei" in sec or "Original" in sec
    assert "Non-Elevation" in sec or "Administrator" in sec or "user mode" in sec.lower()


def test_store_package_parity() -> None:
    package = json.loads((ROOT / "store_package.json").read_text(encoding="utf-8"))
    assert package["identity_name"] == "Geiger.PDFtoPDFocr"
    assert package["app_name"] == "PDFtoPDFocr"
    assert package["publisher_display"] == "Geiger"
    assert "https://github.com/doc-bricks/PDFtoPDFocr" in package["support_url"]


def test_changelog_parity() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "2026-08-21" in changelog
    assert "Discoverability" in changelog or "Sichtbarkeit" in changelog
