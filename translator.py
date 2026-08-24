# -*- coding: utf-8 -*-
"""TranslationSystem - Multi-Language Support für PDFtoPDFocr.

============================================================
Version: 2.0.0 (Standardisiert gemäß P-006 / Tier-2-Mehrsprachigkeit)
Unterstützte Sprachen: DE, EN, ES, ZH (Vereinfacht), JA, RU
============================================================
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

SUPPORTED_LANGUAGES: Tuple[str, ...] = ("de", "en", "es", "zh", "ja", "ru")
DEFAULT_LANGUAGE: str = "de"

LANGUAGE_NAMES: Dict[str, str] = {
    "de": "Deutsch",
    "en": "English",
    "es": "Español",
    "zh": "简体中文",
    "ja": "日本語",
    "ru": "Русский",
}


def detect_system_language() -> str:
    """Erkennt die Systemsprache (Windows UI Language oder Locale) mit Fallback 'de'.

    Unterstützt Standard-Sprachen: 'de', 'en', 'es', 'zh', 'ja', 'ru'.

    Returns:
        Sprachcode ('de', 'en', 'es', 'zh', 'ja', 'ru')
    """
    try:
        if sys.platform.startswith("win"):
            import ctypes

            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0xFF
            lang_map = {
                0x07: "de",  # German
                0x09: "en",  # English
                0x0A: "es",  # Spanish
                0x04: "zh",  # Chinese
                0x11: "ja",  # Japanese
                0x19: "ru",  # Russian
            }
            if lang_id in lang_map:
                return lang_map[lang_id]
            return "en"
    except Exception:
        pass
    try:
        import locale

        loc = (locale.getdefaultlocale()[0] or "").lower()
        for code in ("de", "es", "zh", "ja", "ru", "en"):
            if loc.startswith(code):
                return code
    except Exception:
        pass
    return "de"


class TranslationManager:
    """Multi-Language Translation Manager v2.0 (DE, EN, ES, ZH, JA, RU)."""

    def __init__(self, default_lang: str = "de", base_path: Optional[Path] = None):
        self.current_lang = default_lang if default_lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        self.base_path = Path(base_path) if base_path else Path(__file__).resolve().parent
        self.translations: Dict[str, Dict[str, str]] = self._load_translations()

    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Lädt translations.json aus dem Base- oder Bundle-Verzeichnis."""
        try:
            base = getattr(sys, "_MEIPASS", str(self.base_path))
            path = os.path.join(base, "translations.json")
            if not os.path.exists(path):
                path = os.path.join(str(self.base_path), "translations.json")
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def set_language(self, lang: str) -> None:
        """Setzt die aktive UI-Sprache."""
        if lang in SUPPORTED_LANGUAGES:
            self.current_lang = lang

    def get_language(self) -> str:
        """Gibt die aktuell aktive UI-Sprache zurück."""
        return self.current_lang

    def tr(self, key: str, **kwargs: Any) -> str:
        """Gibt den übersetzten String für key in der aktuellen Sprache zurück.

        Fallback-Kette: current_lang -> en -> de -> key.
        Unterstützt Platzhalter via str.format(**kwargs).
        """
        entry = self.translations.get(key, {})
        if isinstance(entry, dict):
            text = (
                entry.get(self.current_lang)
                or entry.get("en")
                or entry.get("de")
                or key
            )
        else:
            text = str(entry) if entry else key

        if kwargs:
            try:
                text = text.format(**kwargs)
            except (KeyError, ValueError, IndexError):
                pass
        return text


# Globaler Default-Manager für direkte Modulaufrufe
_GLOBAL_MANAGER = TranslationManager()


def tr(key: str, **kwargs: Any) -> str:
    return _GLOBAL_MANAGER.tr(key, **kwargs)


def set_language(lang: str) -> None:
    _GLOBAL_MANAGER.set_language(lang)


def get_language() -> str:
    return _GLOBAL_MANAGER.get_language()
