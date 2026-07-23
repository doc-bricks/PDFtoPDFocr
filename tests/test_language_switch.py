# -*- coding: utf-8 -*-
"""Regressionstests: Welle-1 U1 — sichtbarer DE/EN-UI-Sprachschalter (PDFtoPDFocr).

Prueft die tr()-Umschaltung und die Persistenz der UI-Sprache (headless).
Die OCR-Sprach-Combo (deu/eng/fra/spa) ist bewusst NICHT betroffen.
"""
import PDFtoPDFocr_2 as app


def test_tr_switches_ui_language():
    app.set_language("de")
    assert app.tr("window_title") == "PDF OCR Werkzeug"
    assert app.tr("btn_add_file") == "Datei hinzufügen"
    assert app.tr("label_ui_lang") == "Anzeigesprache:"
    app.set_language("en")
    assert app.tr("window_title") == "PDF OCR Tool"
    assert app.tr("btn_add_file") == "Add File"
    assert app.tr("label_ui_lang") == "Display language:"
    app.set_language("de")


def test_get_language_reflects_set_language():
    app.set_language("en")
    assert app.get_language() == "en"
    app.set_language("de")
    assert app.get_language() == "de"


def test_ui_language_config_roundtrip(tmp_path, monkeypatch):
    cfg = tmp_path / "PDFtoPDFocr"
    monkeypatch.setattr(app, "_ui_config_dir", lambda: cfg)
    # Default, wenn nichts gespeichert
    assert app.load_ui_language() == "de"
    # Speichern + persistiert auf Platte
    assert app.save_ui_language("en") is True
    assert (cfg / "config.json").exists()
    assert app.load_ui_language() == "en"
    # Ungueltige Sprache wird abgelehnt, alter Wert bleibt
    assert app.save_ui_language("fr") is False
    assert app.load_ui_language() == "en"


def test_save_ui_language_preserves_other_keys(tmp_path, monkeypatch):
    cfg = tmp_path / "cfgx"
    cfg.mkdir()
    (cfg / "config.json").write_text('{"other": 42}', encoding="utf-8")
    monkeypatch.setattr(app, "_ui_config_dir", lambda: cfg)
    assert app.save_ui_language("en") is True
    import json
    data = json.loads((cfg / "config.json").read_text(encoding="utf-8"))
    assert data["ui_language"] == "en"
    assert data["other"] == 42  # bestehende Keys bleiben erhalten


def test_unknown_saved_ui_language_falls_back(tmp_path, monkeypatch):
    cfg = tmp_path / "cfg2"
    cfg.mkdir()
    (cfg / "config.json").write_text('{"ui_language": "xx"}', encoding="utf-8")
    monkeypatch.setattr(app, "_ui_config_dir", lambda: cfg)
    assert app.load_ui_language() == "de"


def test_corrupt_config_is_tolerated(tmp_path, monkeypatch):
    cfg = tmp_path / "cfg3"
    cfg.mkdir()
    (cfg / "config.json").write_text("{ this is not valid json", encoding="utf-8")
    monkeypatch.setattr(app, "_ui_config_dir", lambda: cfg)
    assert app.load_ui_language() == "de"
