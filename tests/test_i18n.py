# -*- coding: utf-8 -*-
"""Comprehensive internationalization (i18n) contract & regression tests for PDFtoPDFocr.

========================================================================================
Standardisiert gemäß Policy P-006 / Tier-2-Mehrsprachigkeit:
Unterstützte Sprachen: DE (Deutsch), EN (English), ES (Español),
                      ZH (简体中文), JA (日本語), RU (Русский).
========================================================================================
"""
from __future__ import annotations

import json
from pathlib import Path
from PySide6.QtWidgets import QApplication

import PDFtoPDFocr_2 as app
import manage_translations
from translator import LANGUAGE_NAMES, SUPPORTED_LANGUAGES, TranslationManager, detect_system_language

ROOT = Path(__file__).resolve().parents[1]


def _qapp() -> QApplication:
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication([])
    return instance


def test_all_six_languages_complete_in_translations_json() -> None:
    """Verifies that translations.json contains all 6 languages with 0 missing or empty keys."""
    trans_path = ROOT / "translations.json"
    assert trans_path.exists(), "translations.json must exist in project root"

    data = json.loads(trans_path.read_text(encoding="utf-8"))
    assert len(data) >= 60, f"Expected at least 60 translation keys, got {len(data)}"

    for key, lang_map in data.items():
        assert isinstance(lang_map, dict), f"Key '{key}' must be a dictionary"
        for lang in SUPPORTED_LANGUAGES:
            assert lang in lang_map, f"Key '{key}' is missing language '{lang}'"
            val = lang_map[lang]
            assert isinstance(val, str) and len(val.strip()) > 0, (
                f"Key '{key}' for language '{lang}' must be a non-empty string"
            )


def test_placeholder_consistency_across_all_languages() -> None:
    """Verifies that formatting placeholders ({filename}, {error}, etc.) match in all languages."""
    import re

    placeholder_regex = re.compile(r"\{([a-zA-Z0-9_]+)\}")
    trans_path = ROOT / "translations.json"
    data = json.loads(trans_path.read_text(encoding="utf-8"))

    for key, lang_map in data.items():
        de_placeholders = set(placeholder_regex.findall(lang_map["de"]))
        for lang in SUPPORTED_LANGUAGES:
            lang_placeholders = set(placeholder_regex.findall(lang_map[lang]))
            assert lang_placeholders == de_placeholders, (
                f"Placeholder mismatch in key '{key}' for lang '{lang}': "
                f"{lang_placeholders} vs {de_placeholders}"
            )


def test_manage_translations_auditor_passes_clean() -> None:
    """Runs the manage_translations auditor and asserts 100% full coverage and zero errors."""
    is_ok, errors, stats = manage_translations.audit_translations(ROOT)
    assert is_ok is True, f"Translation audit failed with errors: {errors}"
    assert len(errors) == 0

    total_keys = stats["de"]
    assert total_keys >= 60
    for lang in SUPPORTED_LANGUAGES:
        assert stats[lang] == total_keys, (
            f"Language '{lang}' has only {stats[lang]}/{total_keys} translations"
        )


def test_translator_module_and_manager_functionality() -> None:
    """Tests TranslationManager from translator.py with switching, formatting, and fallbacks."""
    mgr = TranslationManager(default_lang="de", base_path=ROOT)
    assert mgr.get_language() == "de"
    assert mgr.tr("window_title") == "PDF OCR Werkzeug"

    mgr.set_language("en")
    assert mgr.get_language() == "en"
    assert mgr.tr("window_title") == "PDF OCR Tool"

    mgr.set_language("es")
    assert mgr.get_language() == "es"
    assert mgr.tr("window_title") == "Herramienta OCR para PDF"

    mgr.set_language("zh")
    assert mgr.get_language() == "zh"
    assert mgr.tr("window_title") == "PDF OCR 工具"

    mgr.set_language("ja")
    assert mgr.get_language() == "ja"
    assert mgr.tr("window_title") == "PDF OCR ツール"

    mgr.set_language("ru")
    assert mgr.get_language() == "ru"
    assert mgr.tr("window_title") == "Инструмент PDF OCR"

    # Placeholder formatting test
    formatted = mgr.tr("status_processing", filename="doc.pdf")
    assert "doc.pdf" in formatted


def test_four_stage_fallback_chain() -> None:
    """Tests the 4-stage fallback: current_lang -> en -> de -> key."""
    mgr = TranslationManager(default_lang="de", base_path=ROOT)
    # Inject temporary dummy translations
    mgr.translations["test_fallback_en"] = {"en": "English Fallback", "de": "German Text"}
    mgr.translations["test_fallback_de"] = {"de": "German Fallback"}

    mgr.set_language("ru")
    # Falls back to EN
    assert mgr.tr("test_fallback_en") == "English Fallback"
    # Falls back to DE
    assert mgr.tr("test_fallback_de") == "German Fallback"
    # Non-existent key returns key itself
    assert mgr.tr("completely_unknown_key_12345") == "completely_unknown_key_12345"


def test_dynamic_language_switch_in_app_for_all_six_locales() -> None:
    """Tests that app.tr() accurately translates core UI strings across all 6 locales."""
    expected_titles = {
        "de": "PDF OCR Werkzeug",
        "en": "PDF OCR Tool",
        "es": "Herramienta OCR para PDF",
        "zh": "PDF OCR 工具",
        "ja": "PDF OCR ツール",
        "ru": "Инструмент PDF OCR",
    }

    expected_add_buttons = {
        "de": "Datei hinzufügen",
        "en": "Add File",
        "es": "Añadir archivo",
        "zh": "添加文件",
        "ja": "ファイルを追加",
        "ru": "Добавить файл",
    }

    for lang_code, expected_title in expected_titles.items():
        app.set_language(lang_code)
        assert app.get_language() == lang_code
        assert app.tr("window_title") == expected_title
        assert app.tr("btn_add_file") == expected_add_buttons[lang_code]

    # Reset back to German default
    app.set_language("de")


def test_ui_combobox_contains_all_six_languages() -> None:
    """Tests that OCRConverterGUI populates all 6 languages in the UI dropdown."""
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        combo = gui.ui_lang_combo
        assert combo.count() == 6

        found_codes = [combo.itemData(i) for i in range(combo.count())]
        assert tuple(found_codes) == SUPPORTED_LANGUAGES

        found_names = [combo.itemText(i) for i in range(combo.count())]
        for code in SUPPORTED_LANGUAGES:
            assert LANGUAGE_NAMES[code] in found_names
    finally:
        gui.close()


def test_unicode_and_utf8_character_integrity() -> None:
    """Tests that non-ASCII characters in all 6 languages decode properly without mojibake."""
    app.set_language("de")
    assert "ä" in app.tr("tooltip_delete") or "ü" in app.tr("btn_add_file")

    app.set_language("es")
    assert "ñ" in app.tr("btn_add_file") or "ñ" in app.tr("a11y_add_file_description")

    app.set_language("zh")
    assert any("\u4e00" <= ch <= "\u9fff" for ch in app.tr("window_title"))

    app.set_language("ja")
    assert any("\u3040" <= ch <= "\u30ff" or "\u4e00" <= ch <= "\u9fff" for ch in app.tr("btn_add_file"))

    app.set_language("ru")
    assert any("\u0400" <= ch <= "\u04ff" for ch in app.tr("window_title"))

    app.set_language("de")


def test_detect_system_language() -> None:
    """Tests detect_system_language returns a string code."""
    detected = detect_system_language()
    assert isinstance(detected, str)
    assert len(detected) == 2
