# -*- coding: utf-8 -*-
"""Regressionstests: U7 Paket-Hygiene -- tesseract_portable Ausschlussliste."""
import os

import build_release


def _make_fake_tesseract_portable(tmp_path):
    root = tmp_path / "tesseract_portable"
    (root / "tessdata").mkdir(parents=True)
    # Laufzeit-Dateien, die ins Paket MUESSEN
    (root / "tesseract.exe").write_text("", encoding="utf-8")
    (root / "libtesseract-5.dll").write_text("", encoding="utf-8")
    (root / "libleptonica-6.dll").write_text("", encoding="utf-8")
    (root / "tessdata" / "deu.traineddata").write_text("", encoding="utf-8")
    # Trainingstools + Deinstaller, die NICHT ins Paket duerfen (U7)
    (root / "lstmtraining.exe").write_text("", encoding="utf-8")
    (root / "cntraining.exe").write_text("", encoding="utf-8")
    (root / "text2image.exe").write_text("", encoding="utf-8")
    (root / "tesseract-uninstall.exe").write_text("", encoding="utf-8")
    return root


def test_collect_tesseract_portable_files_excludes_training_tools(tmp_path):
    root = _make_fake_tesseract_portable(tmp_path)

    entries = build_release.collect_tesseract_portable_files(root)
    names = {os.path.basename(src) for src, _dest in entries}

    for excluded in (
        "lstmtraining.exe",
        "cntraining.exe",
        "text2image.exe",
        "tesseract-uninstall.exe",
    ):
        assert excluded not in names, f"{excluded} haette ausgeschlossen werden muessen"


def test_collect_tesseract_portable_files_keeps_runtime_binaries(tmp_path):
    root = _make_fake_tesseract_portable(tmp_path)

    entries = build_release.collect_tesseract_portable_files(root)
    names = {os.path.basename(src) for src, _dest in entries}

    for required in ("tesseract.exe", "libtesseract-5.dll", "libleptonica-6.dll", "deu.traineddata"):
        assert required in names, f"{required} haette im Paket bleiben muessen"


def test_collect_tesseract_portable_files_preserves_subfolder_dest(tmp_path):
    root = _make_fake_tesseract_portable(tmp_path)

    entries = build_release.collect_tesseract_portable_files(root)
    entry_map = {os.path.basename(src): dest for src, dest in entries}

    assert entry_map["tesseract.exe"] == "tesseract_portable"
    assert entry_map["deu.traineddata"] == os.path.join("tesseract_portable", "tessdata")
