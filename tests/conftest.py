# -*- coding: utf-8 -*-
"""Gemeinsame Test-Fixtures fuer PDFtoPDFocr."""
import pytest

import PDFtoPDFocr_2 as app


def pytest_configure(config):
    """Setzt basetemp CWD-unabhaengig relativ zum Repo-Root (T-20261114-932985855)."""
    if config.option.basetemp is None:
        config.option.basetemp = str(config.rootpath / ".pytest_temp")


@pytest.fixture(autouse=True)
def _isolate_app_config(tmp_path, monkeypatch):
    """Isoliert die App-Konfiguration (UI-Sprache U6, Exportordner U4) je Test.

    Ohne dies wuerden GUI-instanziierende Tests die echte
    %APPDATA%/PDFtoPDFocr/config.json lesen/schreiben -- umgebungsabhaengig
    und potenziell nebenwirkungsbehaftet. Einzelne Tests koennen
    `_ui_config_dir` weiterhin selbst ueberschreiben (z.B. um einen
    vordefinierten Inhalt zu testen); das hier ist nur der Default.
    """
    monkeypatch.setattr(app, "_ui_config_dir", lambda: tmp_path / "PDFtoPDFocr")
