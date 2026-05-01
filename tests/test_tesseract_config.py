import os

import PDFtoPDFocr_2 as app


def _point_app_at(tmp_path, monkeypatch):
    module_file = tmp_path / "PDFtoPDFocr_2.py"
    module_file.write_text("# test module path\n", encoding="utf-8")
    monkeypatch.setattr(app, "__file__", str(module_file))
    monkeypatch.delattr(app.sys, "_MEIPASS", raising=False)


def test_configure_tesseract_prefers_portable_runtime(tmp_path, monkeypatch):
    _point_app_at(tmp_path, monkeypatch)
    portable_dir = tmp_path / "tesseract_portable"
    portable_dir.mkdir()
    exe_name = "tesseract.exe" if os.name == "nt" else "tesseract"
    portable_exe = portable_dir / exe_name
    portable_exe.write_text("", encoding="utf-8")
    monkeypatch.setattr(app.shutil, "which", lambda name: None)

    cmd = app.configure_tesseract()

    assert cmd == str(portable_exe)
    assert app.pytesseract.pytesseract.tesseract_cmd == str(portable_exe)


def test_get_tessdata_dir_prefers_portable_tessdata(tmp_path, monkeypatch):
    _point_app_at(tmp_path, monkeypatch)
    monkeypatch.delenv("TESSDATA_PREFIX", raising=False)
    portable_tessdata = tmp_path / "tesseract_portable" / "tessdata"
    portable_tessdata.mkdir(parents=True)

    assert app.get_tessdata_dir() == str(portable_tessdata)


def test_ensure_tesseract_accepts_bundled_language_pack(tmp_path, monkeypatch):
    _point_app_at(tmp_path, monkeypatch)
    monkeypatch.delenv("TESSDATA_PREFIX", raising=False)
    portable_dir = tmp_path / "tesseract_portable"
    tessdata_dir = portable_dir / "tessdata"
    tessdata_dir.mkdir(parents=True)
    exe_name = "tesseract.exe" if os.name == "nt" else "tesseract"
    (portable_dir / exe_name).write_text("", encoding="utf-8")
    (tessdata_dir / "eng.traineddata").write_text("dummy", encoding="utf-8")
    monkeypatch.setattr(app.shutil, "which", lambda name: None)

    assert app.ensure_tesseract("eng") is True
    assert os.environ["TESSDATA_PREFIX"] == str(tessdata_dir)
