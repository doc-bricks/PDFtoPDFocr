"""Automated metadata, manifest, documentation, and security parity tests for PDFtoPDFocr."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_metadata() -> None:
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "PDFtoPDFocr"' in content
    assert 'version = "1.1.4"' in content
    assert 'requires-python = ">=3.10"' in content
    assert "https://github.com/doc-bricks/PDFtoPDFocr" in content
    assert 'license = { text = "MIT" }' in content
    assert 'license-files = ["LICENSE", "THIRD_PARTY_LICENSES.md"]' in content
    assert '"Third-Party Licenses"' in content
    assert '"Marketing Log"' in content
    assert '"LLM Ready"' in content


def test_pyproject_urls_contract() -> None:
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"Third-Party Licenses" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/THIRD_PARTY_LICENSES.md"' in content
    assert '"Marketing Log" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/MARKETING-LOG.txt"' in content
    assert '"LLM Ready" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/llms.txt"' in content


def test_readme_badges_and_links_parity() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    # English README badges & links
    assert "badge/license-MIT-green.svg" in readme_en
    assert "badge/version-1.1.4-blue.svg" in readme_en
    assert "badge/python-3.10%2B-blue.svg" in readme_en
    assert "badge/UI%20Engine-PySide6%20%7C%20Qt-41cd52.svg" in readme_en
    assert "badge/i18n-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-blue.svg" in readme_en
    assert "badge/pytest-121%20passed%20%7C%20100%25-brightgreen.svg" in readme_en
    assert "badge/Third--Party-Audited-green.svg" in readme_en
    assert "badge/Marketing--Log-Active-blue.svg" in readme_en
    assert "badge/LLM--Ready-llms.txt-blueviolet.svg" in readme_en
    assert "badge/Ecosystem-doc--bricks-orange.svg" in readme_en
    assert "badge/Umbrella-open--bricks-blue.svg" in readme_en
    assert "badge/last%20checked-2026--09--20-informational.svg" in readme_en

    # German README badges & links
    assert "badge/lizenz-MIT-green.svg" in readme_de
    assert "badge/version-1.1.4-blue.svg" in readme_de
    assert "badge/python-3.10%2B-blue.svg" in readme_de
    assert "badge/UI%20Engine-PySide6%20%7C%20Qt-41cd52.svg" in readme_de
    assert "badge/i18n-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-blue.svg" in readme_de
    assert "badge/pytest-121%20bestanden%20%7C%20100%25-brightgreen.svg" in readme_de
    assert "badge/Drittanbieter--Lizenzen-auditiert-green.svg" in readme_de
    assert "badge/Marketing--Log-aktiv-blue.svg" in readme_de
    assert "badge/LLM--Ready-llms.txt-blueviolet.svg" in readme_de
    assert "doc--bricks-orange.svg" in readme_de
    assert "open--bricks-blue.svg" in readme_de
    assert "badge/zuletzt%20gepr%C3%BCft-2026--09--20-informational.svg" in readme_de

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
    assert "Last-checked: 2026-09-20" in llms
    assert "https://github.com/doc-bricks/PDFtoPDFocr" in llms
    assert "MIT" in llms
    assert "121 verified tests" in llms or "121 passed" in llms
    assert "1.1.4" in llms
    assert "test_metadata.py" in llms
    assert "test_i18n.py" in llms
    assert "test_ui_accessibility.py" in llms
    assert "THIRD_PARTY_LICENSES.md" in llms
    assert "MARKETING-LOG.txt" in llms


def test_security_policy_bilingual_and_invariants() -> None:
    sec = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "## Deutsch" in sec
    assert "## English" in sec
    assert "security@open-bricks.org" in sec
    assert "security@ellmos.ai" in sec
    assert "48 Stunden" in sec or "48 hours" in sec
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
    assert "Pfad B Marketing" in changelog or "MARKETING-LOG.txt" in changelog
    assert "Internationalisierung" in changelog or "i18n" in changelog.lower()


def test_readme_navigation_and_anchor_parity() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    en_anchors = [
        "#system-architecture--component-workflow",
        "#local-data-flow--privacy-isolation",
        "#quick-start--key-operations",
        "#core-features",
        "#target-personas--discoverability",
        "#accessibility--keyboard-shortcuts",
        "#requirements--platform-matrix",
        "#installation--portable-setup",
        "#usage--execution-guidelines",
        "#tests--quality-verification",
        "#sibling-tools--ecosystem",
        "#third-party-licenses--transparency",
        "#privacy--security-model",
        "#exe--distribution-packaging",
        "#machine-readable-llm-context",
        "#contributing--license",
    ]

    de_anchors = [
        "#systemarchitektur--komponenten-workflow",
        "#lokaler-datenfluss--datenschutz-isolation",
        "#schnelleinstieg--kernabläufe",
        "#funktionen--features",
        "#zielgruppen--auffindbarkeit",
        "#barrierefreiheit--tastenkürzel",
        "#voraussetzungen--plattformmatrix",
        "#installation--portables-setup",
        "#nutzung--ausführungsrichtlinien",
        "#tests--qualitätsprüfung",
        "#geschwister-tools--ökosystem",
        "#drittanbieter-lizenzen--transparenz",
        "#datenschutz--sicherheitsmodell",
        "#exe--distributions-packaging",
        "#maschinenlesbarer-llm-kontext",
        "#mitwirken--lizenz",
    ]

    assert len(en_anchors) == 16
    assert len(de_anchors) == 16

    for anchor in en_anchors:
        assert anchor in readme_en, f"Missing anchor in README.md: {anchor}"
    for anchor in de_anchors:
        assert anchor in readme_de, f"Missing anchor in README_de.md: {anchor}"


def test_marketing_log_file_integrity() -> None:
    log_path = ROOT / "MARKETING-LOG.txt"
    assert log_path.exists(), "MARKETING-LOG.txt does not exist"
    text = log_path.read_text(encoding="utf-8")

    assert "PFAD_B_DISCOVERABILITY_AND_DESIGN" in text
    assert "doc-bricks/PDFtoPDFocr" in text
    assert "Persona 1: Legal" in text
    assert "Persona 2: Archivists" in text
    assert "Persona 3: Privacy-Conscious" in text
    assert "Persona 4: Automated Pipeline" in text
    assert "5-WAY COMPETITIVE MATRIX" in text
    assert "Adobe Acrobat Pro" in text
    assert "ABBYY FineReader" in text
    assert "OCRmyPDF" in text
    assert "INV-LOCAL-01" in text
    assert "INV-SLA-10" in text


def test_third_party_licenses_md_integrity() -> None:
    lic_path = ROOT / "THIRD_PARTY_LICENSES.md"
    assert lic_path.exists(), "THIRD_PARTY_LICENSES.md does not exist"
    text = lic_path.read_text(encoding="utf-8")

    # Direct dependencies
    assert "PySide6" in text
    assert "pytesseract" in text
    assert "Pillow" in text
    assert "pdf2image" in text
    assert "pikepdf" in text
    assert "requests" in text

    # Bundled and engine tools
    assert "Tesseract OCR Engine" in text
    assert "Leptonica" in text
    assert "Poppler Utilities" in text

    # Invariants
    for i in range(1, 11):
        assert "INV-" in text

    assert "INV-LOCAL-01" in text
    assert "INV-UNPRIV-02" in text
    assert "INV-NONDEST-03" in text
    assert "INV-ISOLATION-04" in text
    assert "INV-BOUNDED-05" in text
    assert "INV-PORTABLE-06" in text
    assert "INV-MANIFEST-07" in text
    assert "INV-A11Y-08" in text
    assert "INV-FAILCLOSED-09" in text
    assert "INV-SLA-10" in text
    assert "security@open-bricks.org" in text


def test_ci_workflows_timeout_and_concurrency() -> None:
    workflows_dir = ROOT / ".github" / "workflows"
    assert workflows_dir.exists(), "Workflows directory missing"

    tests_yml = (workflows_dir / "tests.yml").read_text(encoding="utf-8")
    assert "timeout-minutes: 15" in tests_yml
    assert "permissions:\n  contents: read" in tests_yml or "contents: read" in tests_yml
    assert "concurrency:" in tests_yml
    assert "cancel-in-progress: true" in tests_yml

    smoke_yml = (workflows_dir / "source-platform-smoke.yml").read_text(encoding="utf-8")
    assert "timeout-minutes: 15" in smoke_yml
    assert "contents: read" in smoke_yml
    assert "concurrency:" in smoke_yml
    assert "cancel-in-progress: true" in smoke_yml


def test_stale_workflow_present_and_configured() -> None:
    stale_yml_path = ROOT / ".github" / "workflows" / "stale.yml"
    assert stale_yml_path.exists(), ".github/workflows/stale.yml must exist"
    content = stale_yml_path.read_text(encoding="utf-8")

    assert "actions/stale@v9" in content
    assert "timeout-minutes: 10" in content
    assert "issues: write" in content
    assert "pull-requests: write" in content
    assert "days-before-stale: 30" in content
    assert "days-before-close: 7" in content


def test_gitignore_multihost_conflict_and_lock_defense() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    # Multi-host conflict protection
    assert "* (kopie)*" in gitignore
    assert "*conflicted copy*" in gitignore
    assert "*-WORKSTATION*" in gitignore
    assert "*-ASUS*" in gitignore

    # Canonical lock protection
    assert "LOCK" in gitignore
    assert "LOCK.*" in gitignore
    assert "LOCK*.txt" in gitignore
    assert "uv.lock" in gitignore
    assert "!package-lock.json" in gitignore


def test_version_parity_across_manifests() -> None:
    import PDFtoPDFocr_2 as app

    # Code version
    assert getattr(app, "APP_VERSION", None) == "1.1.4"

    # pyproject.toml
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "1.1.4"' in pyproject
    assert 'license-files = ["LICENSE", "THIRD_PARTY_LICENSES.md"]' in pyproject

    # store_package.json
    store_pkg = json.loads((ROOT / "store_package.json").read_text(encoding="utf-8"))
    assert store_pkg["version"] == "1.1.4.0"

    # SECURITY.md
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "1.1.4" in security

    # llms.txt
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "1.1.4" in llms

    # READMEs
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")
    assert "badge/version-1.1.4-blue.svg" in readme_en
    assert "badge/version-1.1.4-blue.svg" in readme_de
