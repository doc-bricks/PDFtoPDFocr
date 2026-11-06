"""
Tests für Windows-Store-Artefakte und -Materialien in PDFtoPDFocr.
Prüft Vollständigkeit, Konsistenz, Bildauflösungen und Richtlinienkonformität der Store-Metadaten (Tier-2 6-Sprachen-Standard).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PUBLISHER = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
EXPECTED_IDENTITY = "Geiger.PDFtoPDFocr"
EXPECTED_LANGUAGES = ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]
BANNED_TRADEMARKS = {"windows", "microsoft", "google", "gmail", "apple", "adobe", "outlook"}


class TestStoreMaterials(unittest.TestCase):

    def test_store_package_json_exists_and_is_valid(self):
        path = PROJECT_ROOT / "store_package.json"
        self.assertTrue(path.exists(), "store_package.json fehlt")
        data = json.loads(path.read_text(encoding="utf-8"))
        required = [
            "app_name", "publisher", "publisher_display", "identity_name",
            "version", "description", "executable", "capabilities",
            "category", "age_rating", "privacy_url", "support_url",
            "license", "languages"
        ]
        for field in required:
            self.assertIn(field, data, f"Pflichtfeld '{field}' fehlt in store_package.json")

    def test_store_package_publisher_matches_expected(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            data["publisher"], EXPECTED_PUBLISHER,
            "publisher CN stimmt nicht mit Partner-Center-Konto überein",
        )
        self.assertEqual(
            data["identity_name"], EXPECTED_IDENTITY,
            f"identity_name != {EXPECTED_IDENTITY}",
        )

    def test_store_package_executable_configured(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            data["executable"], "PDFtoPDFocr.exe",
            "executable in store_package.json muss PDFtoPDFocr.exe sein",
        )

    def test_store_package_urls_are_https(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(
            data.get("privacy_url", "").startswith("https://"),
            f"privacy_url '{data.get('privacy_url')}' muss eine HTTPS-URL sein"
        )
        self.assertTrue(
            data.get("support_url", "").startswith("https://"),
            f"support_url '{data.get('support_url')}' muss eine HTTPS-URL sein"
        )

    def test_store_package_json_has_six_tier2_languages(self):
        path = PROJECT_ROOT / "store_package.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        languages = data.get("languages", [])
        for expected in EXPECTED_LANGUAGES:
            self.assertIn(expected, languages, f"Sprache {expected} fehlt in store_package.json languages")

        for code in ["de", "en", "es", "zh", "ja", "ru"]:
            desc_k = f"description_{code}"
            self.assertIn(desc_k, data, f"{desc_k} fehlt in store_package.json")
            self.assertLessEqual(len(data[desc_k]), 100, f"{desc_k} überschreitet 100 Zeichen")
            kw_k = f"keywords_{code}"
            self.assertIn(kw_k, data, f"{kw_k} fehlt in store_package.json")
            self.assertEqual(len(data[kw_k]), 7, f"{kw_k} muss genau 7 Keywords haben")
            for kw in data[kw_k]:
                self.assertLessEqual(len(kw), 30, f"Keyword '{kw}' in {kw_k} > 30 Zeichen")
                self.assertNotIn(kw.lower(), BANNED_TRADEMARKS, f"Markenname '{kw}' in {kw_k}")

    def test_store_assets_exist_and_dimensions(self):
        asset_dir = PROJECT_ROOT / "store_assets"
        self.assertTrue(asset_dir.exists(), "store_assets/ Verzeichnis fehlt")
        expected_icons = {
            "Square44x44Logo.png": (44, 44),
            "StoreLogo.png": (50, 50),
            "Square150x150Logo.png": (150, 150),
            "Wide310x150Logo.png": (310, 150),
            "Square310x310Logo.png": (310, 310),
        }
        for icon_name, expected_size in expected_icons.items():
            icon_path = asset_dir / icon_name
            self.assertTrue(icon_path.exists(), f"Icon {icon_name} fehlt in store_assets/")
            with Image.open(icon_path) as im:
                self.assertEqual(
                    im.size, expected_size,
                    f"Icon {icon_name} hat falsche Dimension: {im.size} != {expected_size}"
                )

    def test_store_listing_exists_and_compliant(self):
        path = PROJECT_ROOT / "STORE_LISTING.md"
        self.assertTrue(path.exists(), "STORE_LISTING.md fehlt")
        content = path.read_text(encoding="utf-8")
        self.assertGreater(len(content.strip()), 500, "STORE_LISTING.md ist zu kurz")
        self.assertIn("## Deutsch", content, "STORE_LISTING.md enthält keinen deutschen Abschnitt")
        self.assertIn("## English", content, "STORE_LISTING.md enthält keinen englischen Abschnitt")
        self.assertIn("## Español", content, "STORE_LISTING.md enthält keinen spanischen Abschnitt")
        self.assertIn("## 简体中文", content, "STORE_LISTING.md enthält keinen chinesischen Abschnitt")
        self.assertIn("## 日本語", content, "STORE_LISTING.md enthält keinen japanischen Abschnitt")
        self.assertIn("## Русский", content, "STORE_LISTING.md enthält keinen russischen Abschnitt")

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
            self.assertIsNotNone(match, f"Keine Keywords für {lang} in STORE_LISTING.md gefunden")
            lines = [l.strip() for l in match.group(1).strip().splitlines() if l.strip()]
            keywords = []
            for line in lines:
                m = re.match(r"^\d+\.\s*(.+)$", line)
                if m:
                    keywords.append(m.group(1).strip().lower())
                elif "," in line:
                    for k in line.split(","):
                        if k.strip():
                            keywords.append(k.strip().lower())
            self.assertEqual(len(keywords), 7, f"Keywords in {lang} != 7 (gefunden: {len(keywords)})")
            for kw in keywords:
                self.assertNotIn(kw, BANNED_TRADEMARKS, f"Verbotene Marke '{kw}' in Keywords für {lang}")

    def test_release_staging_complete(self):
        ws_files = [
            "releases/windowsstore/BUILD.md",
            "releases/windowsstore/WACK_PROTOCOL.md",
            "releases/windowsstore/store_settings.json",
            "releases/windowsstore/store_listing_de.md",
            "releases/windowsstore/store_listing_en.md",
            "releases/windowsstore/store_listing_es.md",
            "releases/windowsstore/store_listing_zh.md",
            "releases/windowsstore/store_listing_ja.md",
            "releases/windowsstore/store_listing_ru.md",
            "releases/windowsstore/StoreLogo.png",
        ]
        for rel_p in ws_files:
            fpath = PROJECT_ROOT / rel_p
            self.assertTrue(fpath.exists(), f"Release-Staging-Datei fehlt: {rel_p}")
            self.assertGreater(fpath.stat().st_size, 10, f"Datei {rel_p} zu klein")

    def test_check_store_readiness_script_passes(self):
        script_path = PROJECT_ROOT / "scripts" / "check_store_readiness.py"
        self.assertTrue(script_path.exists(), "scripts/check_store_readiness.py fehlt")
        res = subprocess.run([sys.executable, "-X", "utf8", str(script_path)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(res.returncode, 0, f"check_store_readiness.py schlug fehl:\n{res.stdout}\n{res.stderr}")


if __name__ == "__main__":
    unittest.main()
