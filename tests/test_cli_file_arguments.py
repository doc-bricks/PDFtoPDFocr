# -*- coding: utf-8 -*-
"""Tests fuer die Verarbeitung von Dateiargumenten beim Start.

Hintergrund: Das Store-Paket deklarierte keine Dateizuordnung, und die
Anwendung wertete uebergebene Pfade nicht aus. Beides zusammen fuehrte dazu,
dass ein Doppelklick auf eine PDF die App nicht oeffnete. Der Manifest-Eintrag
allein genuegt nicht - Windows uebergibt den Pfad als Argument.
"""
from __future__ import annotations

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PDFtoPDFocr_2 = pytest.importorskip("PDFtoPDFocr_2")


@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication
    inst = QApplication.instance() or QApplication([])
    yield inst


@pytest.fixture
def gui(app):
    g = PDFtoPDFocr_2.OCRConverterGUI()
    yield g
    g.close()


def _make_pdf(path):
    """Minimale, aber strukturell gueltige PDF-Datei."""
    path.write_bytes(b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n")
    return str(path)


def test_method_exists(gui):
    assert hasattr(gui, "add_paths_from_arguments")


def test_single_file_is_added(gui, tmp_path):
    pdf = _make_pdf(tmp_path / "test.pdf")
    assert gui.add_paths_from_arguments([pdf]) == 1
    assert gui.list_widget.count() == 1


def test_unsupported_extension_is_ignored(gui, tmp_path):
    other = tmp_path / "notizen.docx"
    other.write_bytes(b"x")
    assert gui.add_paths_from_arguments([str(other)]) == 0
    assert gui.list_widget.count() == 0


def test_duplicates_are_not_added_twice(gui, tmp_path):
    pdf = _make_pdf(tmp_path / "a.pdf")
    gui.add_paths_from_arguments([pdf])
    assert gui.add_paths_from_arguments([pdf]) == 0
    assert gui.list_widget.count() == 1


def test_directory_is_expanded(gui, tmp_path):
    d = tmp_path / "ordner"
    d.mkdir()
    _make_pdf(d / "a.pdf")
    _make_pdf(d / "b.pdf")
    (d / "egal.txt").write_text("x", encoding="utf-8")
    assert gui.add_paths_from_arguments([str(d)]) == 2


def test_switches_and_missing_paths_are_skipped(gui, tmp_path):
    assert gui.add_paths_from_arguments(
        ["--irgendein-schalter", "", str(tmp_path / "gibtsnicht.pdf"), None]) == 0
    assert gui.list_widget.count() == 0


def test_empty_input_is_safe(gui):
    assert gui.add_paths_from_arguments([]) == 0
    assert gui.add_paths_from_arguments(None) == 0


def test_entrypoint_passes_arguments():
    """Der Einstiegspunkt muss die Argumente auch tatsaechlich durchreichen."""
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "PDFtoPDFocr_2.py"), encoding="utf-8").read()
    assert "add_paths_from_arguments(app.arguments()[1:])" in src
