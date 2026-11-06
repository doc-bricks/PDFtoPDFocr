"""
Vertragstests für Windows Store Metadaten, Assets und Dokumente von PDFtoPDFocr.
"""

import json
import unittest
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestStoreReadiness(unittest.TestCase):

    def test_store_package_json_exists_and_is_valid(self):
        pkg_path = PROJECT_ROOT / "store_package.json"
        self.assertTrue(pkg_path.exists(), "store_package.json fehlt")
        data = json.loads(pkg_path.read_text(encoding="utf-8"))

        required_fields = [
            "app_name",
            "publisher",
            "publisher_display",
            "identity_name",
            "version",
            "description",
            "executable",
            "capabilities",
            "category",
            "age_rating",
            "privacy_url",
            "support_url",
            "license",
        ]
        for field in required_fields:
            self.assertIn(field, data, f"Pflichtfeld '{field}' fehlt in store_package.json")
            self.assertTrue(str(data[field]).strip(), f"Feld '{field}' darf nicht leer sein")

        self.assertEqual(
            data["publisher"],
            "CN=52596601-BAB4-4F3F-B182-E8F3F273B202",
            "Publisher CN stimmt nicht mit dem Partner-Center-Konto überein",
        )

    def test_version_parity_with_pyproject(self):
        pkg_path = PROJECT_ROOT / "store_package.json"
        pkg_data = json.loads(pkg_path.read_text(encoding="utf-8"))

        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml fehlt")
        pyproject_content = pyproject_path.read_text(encoding="utf-8")

        # extract version from pyproject.toml (e.g. version = "1.1.3")
        import re
        match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_content)
        self.assertIsNotNone(match, "Version konnte nicht aus pyproject.toml gelesen werden")
        pyproject_version = match.group(1)

        # Store version is Quad-Dot (e.g. 1.1.3.0)
        expected_store_version = f"{pyproject_version}.0"
        self.assertEqual(
            pkg_data["version"],
            expected_store_version,
            f"store_package.json Version ({pkg_data['version']}) passt nicht zu pyproject.toml ({expected_store_version})",
        )

    def test_documentation_files_exist_and_nonempty(self):
        docs = [
            ("PRIVACY_POLICY.md", 200),
            ("SUPPORT.md", 200),
            ("STORE_LISTING.md", 200),
            ("WINDOWS_STORE_PREP.md", 200),
            ("THIRD_PARTY_LICENSES.txt", 200),
        ]
        for doc_name, min_bytes in docs:
            p = PROJECT_ROOT / doc_name
            self.assertTrue(p.exists(), f"Dokument '{doc_name}' fehlt")
            content = p.read_text(encoding="utf-8")
            self.assertGreaterEqual(
                len(content.encode("utf-8")),
                min_bytes,
                f"Dokument '{doc_name}' ist verdächtig kurz ({len(content)} Zeichen)",
            )

    def test_store_assets_exist_and_dimensions(self):
        assets_dir = PROJECT_ROOT / "store_assets"
        self.assertTrue(assets_dir.exists(), "store_assets/ Verzeichnis fehlt")

        expected_icons = {
            "Square44x44Logo.png": (44, 44),
            "StoreLogo.png": (50, 50),
            "Square150x150Logo.png": (150, 150),
            "Wide310x150Logo.png": (310, 150),
            "Square310x310Logo.png": (310, 310),
        }

        for icon_name, expected_size in expected_icons.items():
            icon_path = assets_dir / icon_name
            self.assertTrue(icon_path.exists(), f"Icon '{icon_name}' fehlt in store_assets/")
            with Image.open(icon_path) as img:
                self.assertEqual(
                    img.size,
                    expected_size,
                    f"Icon '{icon_name}' hat falsche Dimensionen {img.size} (erwartet: {expected_size})",
                )

    def test_store_listing_keyword_limits(self):
        listing_path = PROJECT_ROOT / "STORE_LISTING.md"
        self.assertTrue(listing_path.exists(), "STORE_LISTING.md fehlt")
        content = listing_path.read_text(encoding="utf-8")

        import re
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
            self.assertIsNotNone(match, f"Keywords für {lang} nicht gefunden")
            lines = [l.strip() for l in match.group(1).strip().splitlines() if l.strip()]
            keywords = []
            for line in lines:
                m = re.match(r"^\d+\.\s*(.+)$", line)
                if m:
                    keywords.append(m.group(1).strip())
                elif "," in line:
                    for k in line.split(","):
                        if k.strip():
                            keywords.append(k.strip())
            self.assertLessEqual(
                len(keywords),
                7,
                f"Zu viele {lang} Keywords ({len(keywords)} > 7, Microsoft Partner Center Policy 10.1.3)",
            )
            self.assertEqual(len(keywords), 7, f"Keywords für {lang} unvollständig ({len(keywords)} != 7)")

    def test_store_package_has_six_tier2_languages(self):
        pkg_path = PROJECT_ROOT / "store_package.json"
        data = json.loads(pkg_path.read_text(encoding="utf-8"))
        for lang in ["de-DE", "en-US", "es-ES", "zh-CN", "ja-JP", "ru-RU"]:
            self.assertIn(lang, data.get("languages", []))
        for code in ["de", "en", "es", "zh", "ja", "ru"]:
            self.assertIn(f"description_{code}", data)
            self.assertLessEqual(len(data[f"description_{code}"]), 100)
            self.assertIn(f"keywords_{code}", data)
            self.assertEqual(len(data[f"keywords_{code}"]), 7)

    def test_check_store_readiness_script_passes(self):
        from scripts.check_store_readiness import run_store_readiness_check

        success, errors = run_store_readiness_check(PROJECT_ROOT)
        self.assertTrue(success, f"check_store_readiness.py meldet Fehler: {errors}")
        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
