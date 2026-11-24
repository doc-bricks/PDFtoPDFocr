# -*- coding: utf-8 -*-
"""Contract and regression tests for PDFtoPDFocr CLI, P-022 artifacts, and bug fixes."""
from __future__ import annotations

import io
import json
from pathlib import Path
import sys

import pikepdf

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import PDFtoPDFocr_2 as app

ROOT = Path(__file__).resolve().parents[1]


def _make_blank_pdf(path: Path, pages: int = 1) -> Path:
    pdf = pikepdf.Pdf.new()
    for _ in range(pages):
        pdf.add_blank_page(page_size=(120, 120))
    buf = io.BytesIO()
    pdf.save(buf)
    pdf.close()
    path.write_bytes(buf.getvalue())
    return path


def test_pytest_config_has_no_relative_basetemp_and_uses_rootpath_conftest() -> None:
    """T-20261114-932985855: No relative --basetemp in addopts; conftest resolves against rootpath."""
    pyproject_data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    addopts = pyproject_data.get("tool", {}).get("pytest", {}).get("ini_options", {}).get("addopts", "")
    assert "--basetemp" not in addopts

    pytest_ini = ROOT / "pytest.ini"
    if pytest_ini.exists():
        ini_text = pytest_ini.read_text(encoding="utf-8")
        assert "--basetemp" not in ini_text

    conftest_text = (ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert "def pytest_configure(config):" in conftest_text
    assert 'config.rootpath / ".pytest_temp"' in conftest_text


def test_load_translations_prefers_locales_directory(tmp_path: Path, monkeypatch) -> None:
    """TW-PDF-08 parity: PDFtoPDFocr_2._load_translations prefers locales/translations.json."""
    module_file = tmp_path / "PDFtoPDFocr_2.py"
    module_file.write_text("# dummy\n", encoding="utf-8")
    (tmp_path / "locales").mkdir()
    (tmp_path / "locales" / "translations.json").write_text(
        json.dumps({"window_title": {"de": "Aus Locales", "en": "From Locales"}}),
        encoding="utf-8",
    )
    (tmp_path / "translations.json").write_text(
        json.dumps({"window_title": {"de": "Aus Root", "en": "From Root"}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(app, "__file__", str(module_file))
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)

    loaded = app._load_translations()
    assert loaded["window_title"]["de"] == "Aus Locales"


def test_merge_ocr_outputs_ignores_nonexistent_trailing_path_when_target_exists(tmp_path: Path) -> None:
    """merge_ocr_outputs must not raise FileNotFoundError in samefile when an extra input path is missing."""
    p1 = _make_blank_pdf(tmp_path / "a_ocred.pdf")
    p2 = _make_blank_pdf(tmp_path / "b_ocred.pdf")
    target = _make_blank_pdf(tmp_path / "merged.pdf")
    missing = tmp_path / "missing_ocred.pdf"

    merged = app.merge_ocr_outputs([str(p1), str(p2), str(missing)], target.name, tmp_path)
    assert merged == target
    with pikepdf.Pdf.open(merged) as pdf:
        assert len(pdf.pages) == 2


def test_ocr_worker_cancelled_does_not_emit_finished_all(tmp_path: Path, monkeypatch) -> None:
    """Cancelled OCRWorker stops remaining files and skips finished_all emission."""
    p1 = _make_blank_pdf(tmp_path / "one.pdf")
    p2 = _make_blank_pdf(tmp_path / "two.pdf")
    worker = app.OCRWorker([str(p1), str(p2)], "eng")

    processed: list[str] = []
    finished_called = []
    worker.finished_all.connect(lambda: finished_called.append(True))

    def fake_ocr(src: str, lang: str) -> bool:
        processed.append(src)
        worker.stop()
        return True

    monkeypatch.setattr(worker, "_ocr_pdf", fake_ocr)
    worker.run()

    assert processed == [str(p1)]
    assert finished_called == []


def test_ensure_tesseract_headless_does_not_call_qmessagebox(monkeypatch) -> None:
    """Headless ensure_tesseract never attempts to show GUI QMessageBox dialogs."""
    monkeypatch.setattr(app, "configure_tesseract", lambda: None)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("QMessageBox must not be called in headless mode")

    monkeypatch.setattr(app.QMessageBox, "critical", fail_if_called)
    monkeypatch.setattr(app.QMessageBox, "information", fail_if_called)

    assert app.ensure_tesseract("eng", headless=True) is False


def test_cli_version_and_help_and_gui_passthrough(capsys) -> None:
    """CLI --version/--help run headlessly; plain file paths defer to GUI mode."""
    assert app.is_cli_invocation(["sample.pdf"]) is False
    assert app.is_cli_invocation(["--help"]) is True
    assert app.is_cli_invocation(["--version"]) is True
    assert app.is_cli_invocation(["languages", "--json"]) is True

    rc_ver = app.run_cli(["--version", "--json"])
    assert rc_ver == 0
    ver_payload = json.loads(capsys.readouterr().out)
    assert ver_payload["app"] == "PDFtoPDFocr"
    assert ver_payload["version"] == "1.1.4"

    rc_help = app.run_cli(["--help"])
    assert rc_help == 0
    help_out = capsys.readouterr().out
    assert "export-job" in help_out
    assert "merge" in help_out
    assert "ocr" in help_out


def test_cli_languages_and_check_json(capsys, tmp_path: Path, monkeypatch) -> None:
    """Headless languages and check subcommands emit structured JSON without GUI."""
    rc = app.run_cli(["languages", "--json"])
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ui_languages"] == ["de", "en", "es", "zh", "ja", "ru"]
    assert "deu" in data["ocr_languages"]

    monkeypatch.setattr(app, "configure_tesseract", lambda: None)
    monkeypatch.setattr(app, "get_tessdata_dir", lambda: str(tmp_path))
    rc_check = app.run_cli(["check", "--ocr-lang", "eng", "--json"])
    assert rc_check == 1
    check_data = json.loads(capsys.readouterr().out)
    assert check_data["tesseract_found"] is False
    assert check_data["traineddata_found"] is False


def test_cli_export_job_and_merge_json(capsys, tmp_path: Path) -> None:
    """Headless export-job and merge execute shared core logic and return exit codes."""
    p1 = _make_blank_pdf(tmp_path / "doc1.pdf")
    p2 = _make_blank_pdf(tmp_path / "doc2.pdf")
    manifest_out = tmp_path / "job.json"

    rc_exp = app.run_cli([
        "export-job",
        str(p1),
        str(p2),
        "--out",
        str(manifest_out),
        "--ocr-lang",
        "eng",
        "--json",
    ])
    assert rc_exp == 0
    exp_res = json.loads(capsys.readouterr().out)
    assert exp_res["schema"] == "pdftopdfocr-job-v1"
    assert Path(exp_res["output_path"]).is_file()

    merged_out = tmp_path / "out" / "bundle.pdf"
    rc_merge = app.run_cli([
        "merge",
        str(p1),
        str(p2),
        "--out",
        str(merged_out),
        "--json",
    ])
    assert rc_merge == 0
    merge_res = json.loads(capsys.readouterr().out)
    assert Path(merge_res["merged_path"]).is_file()
    assert merge_res["pages"] == 2

    rc_bad_merge = app.run_cli(["merge", str(tmp_path / "missing.pdf"), "--out", str(merged_out), "--json"])
    assert rc_bad_merge == 2
    bad_res = json.loads(capsys.readouterr().out)
    assert bad_res["ok"] is False


def test_cli_ocr_headless_json(capsys, tmp_path: Path, monkeypatch) -> None:
    """Headless ocr subcommand processes files via OCRWorker._ocr_pdf and reports JSON."""
    src = _make_blank_pdf(tmp_path / "scan.pdf")
    monkeypatch.setattr(app, "ensure_tesseract", lambda lang, headless=False: True)
    monkeypatch.setattr(
        app.OCRWorker,
        "_ocr_pdf",
        lambda self, src_path, lang: bool(_make_blank_pdf(Path(src_path).with_name("scan_ocred.pdf"))),
    )

    rc = app.run_cli(["ocr", str(src), "--lang", "eng", "--json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["succeeded"] == 1
    assert payload["failed"] == 0
    assert Path(payload["results"][0]["output_path"]).is_file()

    rc_missing = app.run_cli(["ocr", str(tmp_path / "nope.pdf"), "--json"])
    assert rc_missing == 2
    _ = capsys.readouterr()


def test_p022_skill_llm_txt_and_readme_links() -> None:
    """Policy P-022: SKILL.md, llm.txt, llms.txt, and README links exist and stay current."""
    skill_path = ROOT / "SKILL.md"
    llm_path = ROOT / "llm.txt"
    llms_path = ROOT / "llms.txt"
    assert skill_path.is_file(), "SKILL.md missing (Policy P-022)"
    assert llm_path.is_file(), "llm.txt missing (Policy P-022)"

    skill_text = skill_path.read_text(encoding="utf-8")
    assert "1.1.4" in skill_text
    assert "export-job" in skill_text
    assert "merge" in skill_text
    assert "ocr" in skill_text
    assert "OneDrive" not in skill_text
    assert "C:\\Users\\" not in skill_text

    llm_text = llm_path.read_text(encoding="utf-8")
    assert "llms.txt" in llm_text
    assert "SKILL.md" in llm_text

    llms_text = llms_path.read_text(encoding="utf-8")
    assert "SKILL.md" in llms_text
    assert "llm.txt" in llms_text
    assert "Last-checked:" in llms_text

    for readme_name in ("README.md", "README_de.md"):
        readme_text = (ROOT / readme_name).read_text(encoding="utf-8")
        assert "SKILL.md" in readme_text
        assert "llm.txt" in readme_text
