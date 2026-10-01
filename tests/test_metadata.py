"""Automated metadata, manifest, documentation, and security parity tests for PDFtoPDFocr."""

from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_metadata() -> None:
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "PDFtoPDFocr"' in content
    assert 'version = "1.1.4"' in content
    assert 'requires-python = ">=3.10"' in content
    assert "https://github.com/doc-bricks/PDFtoPDFocr" in content
    assert 'license = { text = "MIT" }' in content
    assert 'license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"]' in content
    assert '"Contributing"' in content
    assert '"Plain-Text License"' in content
    assert '"Third-Party Licenses"' in content
    assert '"Third-Party Licenses (Text)"' in content
    assert '"Level 1 SBOM"' in content
    assert '"Marketing Log"' in content
    assert '"LLM Ready"' in content
    assert '"Notice"' in content


def test_pyproject_urls_contract() -> None:
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"Contributing" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/CONTRIBUTING.md"' in content
    assert '"Plain-Text License" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/LICENSE"' in content
    assert '"Third-Party Licenses" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/THIRD_PARTY_LICENSES.md"' in content
    assert '"Third-Party Licenses (Text)" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/THIRD_PARTY_LICENSES.txt"' in content
    assert '"Level 1 SBOM" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/THIRD_PARTY_LICENSES.txt"' in content
    assert '"Marketing Log" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/MARKETING-LOG.txt"' in content
    assert '"LLM Ready" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/llms.txt"' in content
    assert '"Notice" = "https://github.com/doc-bricks/PDFtoPDFocr/blob/master/NOTICE"' in content


def test_readme_badges_and_links_parity() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    # English README badges & links
    assert "badge/license-MIT-green.svg" in readme_en
    assert "badge/version-1.1.4-blue.svg" in readme_en
    assert "badge/python-3.10%2B-blue.svg" in readme_en
    assert "badge/UI%20Engine-PySide6%20%7C%20Qt-41cd52.svg" in readme_en
    assert "badge/i18n-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-blue.svg" in readme_en
    assert re.search(r"badge/pytest-\d+%20passed", readme_en)
    assert "badge/Third--Party-Audited-green.svg" in readme_en
    assert "badge/Level%201%20SBOM-Plain%20Text-success.svg" in readme_en
    assert "badge/Attribution-NOTICE-informational.svg" in readme_en
    assert "badge/Marketing--Log-Active-blue.svg" in readme_en
    assert "badge/LLM--Ready-llms.txt-blueviolet.svg" in readme_en
    assert "badge/Ecosystem-doc--bricks-orange.svg" in readme_en
    assert "badge/Umbrella-open--bricks-blue.svg" in readme_en
    assert ("badge/last%20checked-2026--10--01-informational.svg" in readme_en) or ("badge/last%20checked-2026--09--30-informational.svg" in readme_en)

    # German README badges & links
    assert "badge/lizenz-MIT-green.svg" in readme_de
    assert "badge/version-1.1.4-blue.svg" in readme_de
    assert "badge/python-3.10%2B-blue.svg" in readme_de
    assert "badge/UI%20Engine-PySide6%20%7C%20Qt-41cd52.svg" in readme_de
    assert "badge/i18n-DE%20%7C%20EN%20%7C%20ES%20%7C%20ZH%20%7C%20JA%20%7C%20RU-blue.svg" in readme_de
    assert re.search(r"badge/pytest-\d+%20bestanden", readme_de)
    assert "badge/Drittanbieter--Lizenzen-auditiert-green.svg" in readme_de
    assert "badge/Level%201%20SBOM-Klartext-success.svg" in readme_de
    assert "badge/Attribution-NOTICE-informational.svg" in readme_de
    assert "badge/Marketing--Log-aktiv-blue.svg" in readme_de
    assert "badge/LLM--Ready-llms.txt-blueviolet.svg" in readme_de
    assert "doc--bricks-orange.svg" in readme_de
    assert "open--bricks-blue.svg" in readme_de
    assert ("badge/zuletzt%20gepr%C3%BCft-2026--10--01-informational.svg" in readme_de) or ("badge/zuletzt%20gepr%C3%BCft-2026--09--30-informational.svg" in readme_de)

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
    assert ("Last-checked: 2026-10-01" in llms) or ("Last-checked: 2026-09-30" in llms)
    assert "https://github.com/doc-bricks/PDFtoPDFocr" in llms
    assert "MIT" in llms
    assert "NOTICE" in llms
    assert "verified tests" in llms or "passed" in llms
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
        "#visual-showcase",
        "#system-architecture--component-workflow",
        "#local-data-flow--privacy-isolation",
        "#quick-start--key-operations",
        "#core-features",
        "#target-personas--discoverability",
        "#comparative-matrix--alternatives",
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
        "#statutory-notice--license",
    ]

    de_anchors = [
        "#visuelle-showcase-galerie",
        "#systemarchitektur--komponenten-workflow",
        "#lokaler-datenfluss--datenschutz-isolation",
        "#schnelleinstieg--kernabläufe",
        "#funktionen--features",
        "#zielgruppen--auffindbarkeit",
        "#vergleichsmatrix--alternativen",
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
        "#gesetzlicher-hinweis--lizenz",
    ]

    assert len(en_anchors) == 18
    assert len(de_anchors) == 18

    for anchor in en_anchors:
        assert anchor in readme_en, f"Missing anchor in README.md: {anchor}"
    for anchor in de_anchors:
        assert anchor in readme_de, f"Missing anchor in README_de.md: {anchor}"

    # Reciprocal HTML anchor tags in both
    for anchor in en_anchors:
        anchor_id = anchor.lstrip("#")
        assert f'<a id="{anchor_id}">' in readme_en, f"Missing HTML anchor <a id=\"{anchor_id}\"> in README.md"
        assert f'<a id="{anchor_id}">' in readme_de, f"Missing reciprocal HTML anchor <a id=\"{anchor_id}\"> in README_de.md"

    for anchor in de_anchors:
        anchor_id = anchor.lstrip("#")
        assert f'<a id="{anchor_id}">' in readme_de, f"Missing HTML anchor <a id=\"{anchor_id}\"> in README_de.md"
        assert f'<a id="{anchor_id}">' in readme_en, f"Missing reciprocal HTML anchor <a id=\"{anchor_id}\"> in README.md"


def test_marketing_log_file_integrity() -> None:
    log_path = ROOT / "MARKETING-LOG.txt"
    assert log_path.exists(), "MARKETING-LOG.txt does not exist"
    text = log_path.read_text(encoding="utf-8")

    assert "PFAD_B_DISCOVERABILITY_AND_DESIGN" in text
    assert "doc-bricks/PDFtoPDFocr" in text
    assert "PERSONA-01" in text
    assert "PERSONA-02" in text
    assert "PERSONA-03" in text
    assert "PERSONA-04" in text
    assert "10-DIMENSION COMPARATIVE MATRIX" in text or "5-WAY COMPETITIVE MATRIX" in text
    assert "Adobe Acrobat Pro" in text
    assert "ABBYY FineReader" in text
    assert "OCRmyPDF" in text
    assert "INV-LOCAL-01" in text
    assert "INV-SLA-10" in text


def test_third_party_licenses_md_integrity() -> None:
    lic_path = ROOT / "THIRD_PARTY_LICENSES.md"
    assert lic_path.exists(), "THIRD_PARTY_LICENSES.md does not exist"
    text = lic_path.read_text(encoding="utf-8")

    # Level 1 SBOM
    assert "Level 1 Software Bill of Materials" in text or "Level 1 SBOM" in text

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

    # Invariant Cross-Reference Matrix & Non-Elevation
    assert "Invariant Cross-Reference & Verification Matrix" in text
    assert "Unprivileged RunAsInvoker Non-Elevation Certification" in text
    assert "Subprocess Boundary & Copyleft Isolation Guarantee" in text
    assert "security@open-bricks.org" in text


def test_mermaid_diagrams_dual_parity() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for content in (readme_en, readme_de):
        assert "```mermaid" in content
        assert "flowchart TD" in content or "graph TD" in content
        assert "sequenceDiagram" in content
        assert "autonumber" in content


def test_target_personas_and_seo_queries() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for content in (readme_en, readme_de):
        assert "[PERSONA-01]" in content
        assert "[PERSONA-02]" in content
        assert "[PERSONA-03]" in content
        assert "[PERSONA-04]" in content


def test_comparative_matrix_and_invariants() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    for content in (readme_en, readme_de):
        for _ in range(1, 11):
            assert "INV-" in content
        assert "INV-LOCAL-01" in content
        assert "INV-SLA-10" in content
        assert "Adobe Acrobat Pro" in content
        assert "ABBYY FineReader" in content
        assert "OCRmyPDF" in content


def test_bgb_521_statutory_notice() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "§ 521 BGB" in readme_en
    assert "Bürgerliches Gesetzbuch" in readme_en
    assert "§ 521 BGB" in readme_de
    assert "Gefälligkeitsrecht" in readme_de or "Schenkungsrecht" in readme_de


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
    assert "*-WORKSTATION-LG*" in gitignore
    assert "*-ASUS*" in gitignore
    assert "*-IDEAPAD*" in gitignore

    # Canonical lock protection
    assert "LOCK" in gitignore
    assert "LOCK.*" in gitignore
    assert "LOCK*.txt" in gitignore
    assert "LOCK.dev.*" in gitignore
    assert "LOCK.antigravity.*" in gitignore
    assert ".automation-lock" in gitignore
    assert "uv.lock" in gitignore
    assert "!package-lock.json" in gitignore

    # Test temp & cache protection
    assert ".pytest_temp/" in gitignore
    assert ".pytest_tmp*" in gitignore
    assert "Desktop.ini" in gitignore
    assert "ehthumbs.db" in gitignore
    assert "*.swo" in gitignore
    assert "TASKPLAN_*.md" in gitignore


def test_version_parity_across_manifests() -> None:
    import PDFtoPDFocr_2 as app

    # Code version
    assert getattr(app, "APP_VERSION", None) == "1.1.4"

    # pyproject.toml
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "1.1.4"' in pyproject
    assert 'license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"]' in pyproject

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


def test_notice_attribution_contract() -> None:
    notice_path = ROOT / "NOTICE"
    assert notice_path.exists(), "NOTICE file must exist in repository root"
    content = notice_path.read_text(encoding="utf-8")
    assert "PDFtoPDFocr" in content
    assert "Lukas Geiger" in content
    assert "doc-bricks" in content
    assert "open-bricks" in content
    assert "MIT License" in content
    assert "THIRD_PARTY_LICENSES.md" in content
    assert "THIRD_PARTY_LICENSES.txt" in content


def test_ci_lifecycle_workflows_and_labels_parity() -> None:
    workflows_dir = ROOT / ".github" / "workflows"
    auto_assign = (workflows_dir / "auto-assign.yml").read_text(encoding="utf-8")
    assert "Auto Assign" in auto_assign
    assert "timeout-minutes: 5" in auto_assign
    assert "cancel-in-progress: true" in auto_assign
    assert "actions/github-script@v7" in auto_assign

    label_sync = (workflows_dir / "label-sync.yml").read_text(encoding="utf-8")
    assert "Label Sync" in label_sync
    assert "timeout-minutes: 5" in label_sync
    assert "cancel-in-progress: true" in label_sync
    assert "EndBug/label-sync@v2" in label_sync
    assert ".github/labels.yml" in label_sync

    labels_yml = ROOT / ".github" / "labels.yml"
    assert labels_yml.exists()
    labels_content = labels_yml.read_text(encoding="utf-8")
    for expected_label in ("bug", "documentation", "duplicate", "enhancement", "security"):
        assert f'name: "{expected_label}"' in labels_content

    welcome_yml = (workflows_dir / "welcome.yml").read_text(encoding="utf-8")
    assert "actions/first-interaction@v3" in welcome_yml
    assert "cancel-in-progress: true" in welcome_yml
    assert "timeout-minutes: 5" in welcome_yml


def test_contributing_guide_quality_gates_and_version_freeze() -> None:
    contrib = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "Quality Gates" in contrib
    assert "pytest" in contrib
    assert "ruff check" in contrib
    assert "compileall" in contrib
    assert "git diff --check" in contrib
    assert "T-20260920-167562623" in contrib
    assert "1.1.4" in contrib
    assert "Plan D" in contrib


def test_third_party_licenses_txt_level1_sbom_invariants() -> None:
    txt_path = ROOT / "THIRD_PARTY_LICENSES.txt"
    assert txt_path.exists()
    content = txt_path.read_text(encoding="utf-8")
    assert ("Stand: 2026-10-01" in content) or ("Stand: 2026-09-30" in content)
    assert "NOTICE" in content
    assert "THIRD_PARTY_LICENSES.md" in content
    for inv in [
        "INV-LOCAL-01",
        "INV-UNPRIV-02",
        "INV-NONDEST-03",
        "INV-ISOLATION-04",
        "INV-BOUNDED-05",
        "INV-PORTABLE-06",
        "INV-MANIFEST-07",
        "INV-A11Y-08",
        "INV-FAILCLOSED-09",
        "INV-SLA-10",
    ]:
        assert f"{inv}:" in content
        assert "(VERIFIED)" in content


def test_changelog_unreleased_pfad_a_hygiene() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]" in changelog
    assert "Pfad A: Repository-Hygiene, CI-Lifecycle-Workflows" in changelog
    assert "NOTICE" in changelog
    assert "T-20260920-167562623" in changelog
    assert "2026-09-30" in changelog


def test_ascii_four_view_topology_projection() -> None:
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README_de.md").read_text(encoding="utf-8")

    # English 4-view topology
    assert "Four-View Architectural Topology Projection" in readme_en
    assert "[VIEW 1: INGESTION, DRAG-AND-DROP QUEUE & ACCESSIBILITY]" in readme_en
    assert "[VIEW 2: ASYNC ORCHESTRATION, WORKER THREAD & DISPATCHER ENGINE]" in readme_en
    assert "[VIEW 3: CORE OCR PIPELINE, POPPLER RASTERIZER & TESSERACT ENGINE]" in readme_en
    assert "[VIEW 4: AIR-GAP DEFENSE PERIMETER, ZERO-EGRESS & GOVERNANCE BOUNDARY]" in readme_en

    # German 4-view topology
    assert "Vier-Sichten Architektur-Topologie Projektion" in readme_de
    assert "[SICHT 1: AUFNAHME, DRAG-AND-DROP-WARTESCHLANGE & BARRIEREFREIHEIT]" in readme_de
    assert "[SICHT 2: ASYNCHRONE ORCHESTRIERUNG, WORKER-THREAD & DISPATCHER-ENGINE]" in readme_de
    assert "[SICHT 3: KERN-OCR-PIPELINE, POPPLER-RASTERISIERER & TESSERACT-ENGINE]" in readme_de
    assert "[SICHT 4: AIR-GAP-SICHERHEITSPERIMETER, ZERO-EGRESS & DATEISYSTEMGRENZE]" in readme_de

    # Reciprocal anchors in both
    for content in (readme_en, readme_de):
        assert 'id="four-view-architectural-topology-projection"' in content
        assert 'id="vier-sichten-architektur-topologie-projektion"' in content


def test_pep621_seo_keywords_expansion() -> None:
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for keyword in ("zero-egress", "offline-first", "batch-ocr", "accessibility", "local-first", "pdf", "ocr"):
        assert f'"{keyword}"' in content


def test_marketing_log_pfad_b_recency() -> None:
    log_path = ROOT / "MARKETING-LOG.txt"
    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "2026-10-01" in content
    assert "[PFAD_B_DISCOVERABILITY_AND_DESIGN]" in content
    assert "FOUR-VIEW ARCHITECTURAL TOPOLOGY" in content
    assert "doc-bricks/PDFtoPDFocr" in content


def test_changelog_pfad_b_recency() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]" in changelog
    assert "Pfad B: Discoverability, Visuelle Vier-Sichten-Architektur, Level 1 SBOM Re-Audit & Vertragstests (2026-10-01)" in changelog
    assert "T-20260920-167562623" in changelog
    assert "2026-10-01" in changelog
