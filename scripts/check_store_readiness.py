"""
Store-Readiness Preflight Checker für PDFtoPDFocr.
Prüft alle Windows Store Release Readiness Artefakte auf Vollständigkeit, Konsistenz und Richtlinienkonformität (Tier-2 6-Sprachen-Standard).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from PIL import Image
except ImportError:
    Image = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BANNED_TRADEMARKS = {"windows", "microsoft", "google", "gmail", "apple", "adobe", "outlook"}
EXPECTED_PUBLISHER = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
EXPECTED_IDENTITY = "Geiger.PDFtoPDFocr"
EXPECTED_LANGUAGES = ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]


def check_store_readiness(project_root: Path = PROJECT_ROOT) -> tuple[list[str], list[str]]:
    """Führt alle Preflight-Prüfungen für die Windows Store Release Readiness durch.

    Returns:
        tuple[list[str], list[str]]: (passed_checks, findings)
    """
    passed: list[str] = []
    findings: list[str] = []

    # 1. store_package.json
    pkg_file = project_root / "store_package.json"
    if not pkg_file.exists():
        findings.append("store_package.json fehlt im Projektroot.")
    else:
        try:
            data = json.loads(pkg_file.read_text(encoding="utf-8"))
            req_fields = [
                "app_name", "identity_name", "publisher", "publisher_display",
                "version", "description", "executable", "capabilities", "category",
                "age_rating", "license", "languages", "privacy_url", "support_url"
            ]
            missing = [f for f in req_fields if f not in data or not data[f]]
            if missing:
                findings.append(f"store_package.json: Fehlende Pflichtfelder: {missing}")
            else:
                passed.append("store_package.json Pflichtfelder vollständig (inkl. license, languages)")

            if data.get("publisher") != EXPECTED_PUBLISHER:
                findings.append(f"store_package.json: 'publisher' ist '{data.get('publisher')}', erwartet '{EXPECTED_PUBLISHER}'")
            else:
                passed.append("store_package.json Publisher-DN hat CN=-Format und entspricht Partner Center")

            if data.get("identity_name") != EXPECTED_IDENTITY:
                findings.append(f"store_package.json: 'identity_name' ist '{data.get('identity_name')}', erwartet '{EXPECTED_IDENTITY}'")
            else:
                passed.append(f"store_package.json Identity Name ist {EXPECTED_IDENTITY}")

            if data.get("executable") != "PDFtoPDFocr.exe":
                findings.append(f"store_package.json: Executable ist '{data.get('executable')}', erwartet 'PDFtoPDFocr.exe'")
            else:
                passed.append("store_package.json Executable ist PDFtoPDFocr.exe")

            if not re.match(r"^\d+\.\d+\.\d+\.\d+$", data.get("version", "")):
                findings.append(f"store_package.json: Version '{data.get('version')}' ist kein 4-teiliger Version-String.")
            else:
                passed.append("store_package.json Version-Format (4-teilig) OK")

            if not data.get("privacy_url", "").startswith("https://"):
                findings.append("store_package.json: 'privacy_url' muss eine HTTPS-URL sein.")
            else:
                passed.append("store_package.json privacy_url ist gültige HTTPS-URL")

            if not data.get("support_url", "").startswith("https://"):
                findings.append("store_package.json: 'support_url' muss eine HTTPS-URL sein.")
            else:
                passed.append("store_package.json support_url ist gültige HTTPS-URL")

            # 6-Sprachen-Prüfung in store_package.json
            languages = data.get("languages", [])
            missing_langs = [lang for lang in EXPECTED_LANGUAGES if lang not in languages]
            if missing_langs:
                findings.append(f"store_package.json: Fehlende Tier-2 Sprachen: {missing_langs}")
            else:
                passed.append("store_package.json: Alle 6 Tier-2 Sprachen deklariert")

            for lang_code in ["de", "en", "es", "zh", "ja", "ru"]:
                desc_k = f"description_{lang_code}"
                if desc_k in data:
                    if len(data[desc_k]) > 100:
                        findings.append(f"store_package.json {desc_k} überschreitet 100 Zeichen ({len(data[desc_k])})")
                    else:
                        passed.append(f"store_package.json {desc_k} <= 100 Zeichen ({len(data[desc_k])})")
                else:
                    findings.append(f"store_package.json: {desc_k} fehlt.")

                kw_k = f"keywords_{lang_code}"
                if kw_k in data:
                    kws = data[kw_k]
                    if len(kws) != 7:
                        findings.append(f"store_package.json {kw_k} hat {len(kws)} Keywords (genau 7 erwartet)")
                    else:
                        passed.append(f"store_package.json {kw_k}: genau 7 Keywords")
                    for kw in kws:
                        if len(kw) > 30:
                            findings.append(f"store_package.json {kw_k} Keyword '{kw}' > 30 Zeichen")
                        if kw.lower() in BANNED_TRADEMARKS:
                            findings.append(f"store_package.json {kw_k} enthält verbotene Marke '{kw}'")
                else:
                    findings.append(f"store_package.json: {kw_k} fehlt.")

        except Exception as e:
            findings.append(f"store_package.json Lese-/Parsefehler: {e}")

    # 2. Dokumente
    doc_files = {
        "STORE_LISTING.md": ("Store Listing (DE/EN/ES/ZH/JA/RU)", 200),
        "PRIVACY_POLICY.md": ("Datenschutzerklärung", 200),
        "SUPPORT.md": ("Support-Dokumentation", 100),
        "WINDOWS_STORE_PREP.md": ("Windows Store Vorbereitungsdoku", 100),
        "THIRD_PARTY_LICENSES.txt": ("Drittanbieter-Lizenzen", 200),
    }
    for filename, (label, min_size) in doc_files.items():
        p = project_root / filename
        if not p.exists():
            findings.append(f"Dokument fehlt: {filename} ({label})")
        elif p.stat().st_size < min_size:
            findings.append(f"Dokument zu kurz: {filename} ({p.stat().st_size} Bytes < {min_size})")
        else:
            passed.append(f"Dokument vorhanden: {filename} ({label})")

    # 3. Store Icon Assets in store_assets/
    expected_icons = {
        "Square44x44Logo.png": (44, 44),
        "StoreLogo.png": (50, 50),
        "Square150x150Logo.png": (150, 150),
        "Wide310x150Logo.png": (310, 150),
        "Square310x310Logo.png": (310, 310),
    }
    asset_dir = project_root / "store_assets"
    if not asset_dir.exists():
        findings.append("store_assets/ Verzeichnis fehlt.")
    else:
        for icon_name, expected_size in expected_icons.items():
            icon_p = asset_dir / icon_name
            if not icon_p.exists():
                findings.append(f"Icon fehlt in store_assets/: {icon_name}")
            else:
                if Image is not None:
                    try:
                        with Image.open(icon_p) as im:
                            if im.size != expected_size:
                                findings.append(f"Icon {icon_name} falsche Dimension: {im.size} != {expected_size}")
                            else:
                                passed.append(f"Icon {icon_name} Größe {im.size} OK")
                    except Exception as e:
                        findings.append(f"Icon {icon_name} Bildfehler: {e}")
                else:
                    passed.append(f"Icon {icon_name} vorhanden")

    # 4. Keyword-Richtlinie 10.1.3 in STORE_LISTING.md
    listing_path = project_root / "STORE_LISTING.md"
    if listing_path.exists():
        content = listing_path.read_text(encoding="utf-8")
        lang_sections = [
            ("DE", r"## Deutsch[\s\S]*?(?:### Suchbegriffe|### Schlüsselwörter)[^\n]*\n([\s\S]*?)(?=---|\Z)"),
            ("EN", r"## English[\s\S]*?(?:### Search Keywords|### Keywords)[^\n]*\n([\s\S]*?)(?=---|\Z)"),
            ("ES", r"## Español[\s\S]*?### Palabras clave[^\n]*\n([\s\S]*?)(?=---|\Z)"),
            ("ZH", r"## 简体中文[\s\S]*?### 关键词[^\n]*\n([\s\S]*?)(?=---|\Z)"),
            ("JA", r"## 日本語[\s\S]*?### キーワード[^\n]*\n([\s\S]*?)(?=---|\Z)"),
            ("RU", r"## Русский[\s\S]*?### Ключевые слова[^\n]*\n([\s\S]*?)(?=\Z)"),
        ]

        for lang, pattern in lang_sections:
            match = re.search(pattern, content)
            if not match:
                findings.append(f"STORE_LISTING.md: Keine Keywords für {lang} gefunden.")
                continue
            lines = [line.strip() for line in match.group(1).strip().splitlines() if line.strip()]
            keywords = []
            for line in lines:
                m = re.match(r"^\d+\.\s*(.+)$", line)
                if m:
                    keywords.append(m.group(1).strip().lower())
                elif "," in line:
                    for k in line.split(","):
                        if k.strip():
                            keywords.append(k.strip().lower())

            if len(keywords) > 7:
                findings.append(f"STORE_LISTING.md ({lang}): Zu viele Keywords ({len(keywords)} > 7, Richtlinie 10.1.3 verletzt).")
            elif len(keywords) == 0:
                findings.append(f"STORE_LISTING.md ({lang}): Keine Keywords extrahiert.")
            else:
                passed.append(f"STORE_LISTING.md ({lang}): {len(keywords)}/7 Keywords (Richtlinie 10.1.3)")

            trademark_hits = [kw for kw in keywords if kw in BANNED_TRADEMARKS]
            if trademark_hits:
                findings.append(f"STORE_LISTING.md ({lang}): Markenbegriffe in Keywords gefunden: {trademark_hits}")
            else:
                passed.append(f"STORE_LISTING.md ({lang}): Keine geschützten Markenbegriffe")

    # 5. Staging-Dateien in releases/windowsstore/
    ws_files = {
        "releases/windowsstore/BUILD.md": "Build-Anleitung",
        "releases/windowsstore/WACK_PROTOCOL.md": "WACK-Protokoll",
        "releases/windowsstore/store_settings.json": "Store-Einstellungen",
        "releases/windowsstore/store_listing_de.md": "Store Listing Deutsch",
        "releases/windowsstore/store_listing_en.md": "Store Listing Englisch",
        "releases/windowsstore/store_listing_es.md": "Store Listing Spanisch",
        "releases/windowsstore/store_listing_zh.md": "Store Listing Chinesisch",
        "releases/windowsstore/store_listing_ja.md": "Store Listing Japanisch",
        "releases/windowsstore/store_listing_ru.md": "Store Listing Russisch",
        "releases/windowsstore/StoreLogo.png": "StoreLogo 50x50",
    }
    for rel_p, lbl in ws_files.items():
        fpath = project_root / rel_p
        if not fpath.exists():
            findings.append(f"Release-Staging-Datei fehlt: {rel_p} ({lbl})")
        elif fpath.stat().st_size < 10:
            findings.append(f"Release-Staging-Datei zu klein: {rel_p}")
        else:
            passed.append(f"Release-Staging-Datei {rel_p} ({lbl}) OK")

    return passed, findings


def run_store_readiness_check(project_root: Path = PROJECT_ROOT) -> tuple[bool, list[str]]:
    """Kompatibilitäts-Wrapper für bestehende Testaufrufe."""
    passed, findings = check_store_readiness(project_root)
    return len(findings) == 0, findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Store-Readiness Preflight Checker für PDFtoPDFocr")
    parser.add_argument("--allow-blockers", action="store_true", help="Beendet auch bei Warnungen mit Exit-Code 0")
    args = parser.parse_args()

    passed, findings = check_store_readiness(PROJECT_ROOT)
    print("=== STORE-READINESS PREFLIGHT REPORT (PDFtoPDFocr) ===")
    for p in passed:
        print(f"  [OK] {p}")
    if findings:
        print(f"\n=== GEFUNDENE PROBLEME ({len(findings)}) ===")
        for f in findings:
            print(f"  [FEHLER] {f}")
        if args.allow_blockers:
            print("\n[HINWEIS] Beendet mit Exit 0 wegen --allow-blockers Flag.")
            return 0
        return 1
    print(f"\n[ERFOLG] Alle {len(passed)} Store-Readiness-Prüfungen bestanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
