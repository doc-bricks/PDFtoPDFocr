# -*- coding: utf-8 -*-
"""manage_translations.py - Multi-Language Translation Manager & Auditor.

=============================================================================
Standardisiert gemäß P-006 / Tier-2-Mehrsprachigkeit (DE, EN, ES, ZH, JA, RU).
Verifiziert und pflegt translations.json für PDFtoPDFocr.

Verwendung:
    python manage_translations.py [--check] [--dir PROJEKTVERZEICHNIS]
=============================================================================
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

SUPPORTED_LANGUAGES: Tuple[str, ...] = ("de", "en", "es", "zh", "ja", "ru")
TRANSLATION_FILE = "translations.json"

TR_CALL_PATTERN = re.compile(r'\btr\(\s*["\']([^"\']+)["\']')
PLACEHOLDER_PATTERN = re.compile(r"\{([a-zA-Z0-9_]+)\}")


def load_translations(base_dir: Path) -> Dict[str, Dict[str, str]]:
    """Lädt translations.json."""
    trans_path = base_dir / TRANSLATION_FILE
    if not trans_path.exists():
        return {}
    with open(trans_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_tr_keys_in_code(base_dir: Path) -> Set[str]:
    """Findet alle Schlüssel, die im Quellcode via tr('key') referenziert werden."""
    keys: Set[str] = set()
    skip_dirs = {"build", "dist", "venv", ".venv", "__pycache__", ".git", ".pytest_cache"}

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".py") and not file.startswith("test_") and file != "manage_translations.py":
                file_path = Path(root) / file
                try:
                    content = file_path.read_text(encoding="utf-8")
                    for match in TR_CALL_PATTERN.finditer(content):
                        keys.add(match.group(1))
                except Exception:
                    pass
    return keys


def audit_translations(base_dir: Path) -> Tuple[bool, List[str], Dict[str, int]]:
    """Prüft Vollständigkeit und Platzhalterkonsistenz der Übersetzungen."""
    translations = load_translations(base_dir)
    errors: List[str] = []
    stats: Dict[str, int] = {lang: 0 for lang in SUPPORTED_LANGUAGES}

    if not translations:
        errors.append(f"Übersetzungsdatei {TRANSLATION_FILE} nicht gefunden oder leer.")
        return False, errors, stats

    code_keys = find_tr_keys_in_code(base_dir)
    for code_key in code_keys:
        if code_key not in translations:
            errors.append(f"Schlüssel '{code_key}' im Quelltext gefunden, fehlt jedoch in {TRANSLATION_FILE}!")

    for key, lang_map in translations.items():
        if not isinstance(lang_map, dict):
            errors.append(f"Schlüssel '{key}' hat ungültiges Format (kein Dictionary).")
            continue

        de_text = lang_map.get("de", "")
        de_placeholders = set(PLACEHOLDER_PATTERN.findall(de_text))

        for lang in SUPPORTED_LANGUAGES:
            text = lang_map.get(lang)
            if not text or not isinstance(text, str) or not text.strip():
                errors.append(f"Schlüssel '{key}' fehlt für Sprache '{lang}' oder ist leer.")
            else:
                stats[lang] += 1
                lang_placeholders = set(PLACEHOLDER_PATTERN.findall(text))
                if lang_placeholders != de_placeholders:
                    errors.append(
                        f"Schlüssel '{key}' ({lang}) hat abweichende Platzhalter: "
                        f"{lang_placeholders} vs. {de_placeholders} (DE)"
                    )

    is_ok = len(errors) == 0
    return is_ok, errors, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-Language Translation Auditor für PDFtoPDFocr")
    parser.add_argument("--dir", type=str, default=".", help="Projektverzeichnis (Default: .)")
    parser.add_argument("--check", action="store_true", help="Gibt Non-Zero Exit Code bei Fehlern zurück (CI-Gate)")
    args = parser.parse_args()

    base_dir = Path(args.dir).resolve()
    is_ok, errors, stats = audit_translations(base_dir)

    print(f"=== Translation Audit: PDFtoPDFocr ({base_dir}) ===")
    print(f"Unterstützte Sprachen (P-006): {', '.join(SUPPORTED_LANGUAGES)}")
    print(f"Gefundene Schlüssel: {stats.get('de', 0)}\n")

    print("Uebersetzungsabdeckung:")
    for lang in SUPPORTED_LANGUAGES:
        count = stats.get(lang, 0)
        status = "[OK] 100% vollstaendig" if count == stats.get("de", 0) and count > 0 else f"[!] {count} Eintraege"
        print(f"  - [{lang.upper()}] {status} ({count} Strings)")

    if errors:
        print(f"\n[!] Gefundene Fehler ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")
        return 1 if args.check else 0
    else:
        print("\n[OK] Alle Uebersetzungen sind vollstaendig, wohlgeformt und valide!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
