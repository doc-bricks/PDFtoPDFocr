# -*- coding: utf-8 -*-
"""Test suite for application icon assets and multi-platform packaging."""

from PIL import Image
from PySide6.QtWidgets import QApplication

import PDFtoPDFocr_2 as app_module


def _get_qapp():
    return QApplication.instance() or QApplication([])


def test_master_icon_properties():
    """Verify master icon format, size, and RGBA channels."""
    root = app_module.get_project_root()
    master_candidates = [root / "assets" / "icon.png", root / "PDFtoPDFocr.png"]
    for path in master_candidates:
        assert path.exists(), f"Master icon missing: {path}"
        with Image.open(path) as img:
            assert img.format == "PNG"
            assert img.size == (512, 512)
            assert img.mode in ("RGBA", "RGB")


def test_windows_multi_res_ico():
    """Verify Windows ICO contains required multi-resolution layers."""
    root = app_module.get_project_root()
    ico_candidates = [
        root / "PDFtoPDFocr.ico",
        root / "assets" / "icon.ico",
        root / "assets" / "app_icon.ico",
    ]
    required_layers = {(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)}
    for ico_path in ico_candidates:
        assert ico_path.exists(), f"ICO file missing: {ico_path}"
        with Image.open(ico_path) as img:
            assert img.format == "ICO"
            available = set(img.ico.sizes())
            for req in required_layers:
                assert req in available, f"Missing resolution {req} in {ico_path}"


def test_store_and_tile_icons():
    """Verify Windows Store / MSIX tile icons have valid sizes."""
    root = app_module.get_project_root()
    expected_tiles = {
        root / "assets" / "icons" / "icon_44x44.png": (44, 44),
        root / "assets" / "icons" / "icon_50x50.png": (50, 50),
        root / "assets" / "icons" / "icon_150x150.png": (150, 150),
        root / "assets" / "icons" / "icon_310x150.png": (310, 150),
        root / "assets" / "icons" / "icon_310x310.png": (310, 310),
        root / "store_assets" / "Square44x44Logo.png": (44, 44),
        root / "store_assets" / "Square150x150Logo.png": (150, 150),
        root / "store_assets" / "Square310x310Logo.png": (310, 310),
        root / "store_assets" / "Wide310x150Logo.png": (310, 150),
    }
    for file_path, size in expected_tiles.items():
        assert file_path.exists(), f"Tile icon missing: {file_path}"
        with Image.open(file_path) as img:
            assert img.size == size, f"Incorrect dimensions for {file_path}: {img.size} != {size}"


def test_favicon_assets():
    """Verify favicon assets."""
    root = app_module.get_project_root()
    fav_ico = root / "assets" / "favicon.ico"
    fav_png = root / "assets" / "favicon.png"
    assert fav_ico.exists()
    assert fav_png.exists()
    with Image.open(fav_png) as img:
        assert img.size == (64, 64)


def test_runtime_app_icon_loader():
    """Verify get_app_icon_path() and get_app_icon() return valid non-null objects."""
    _app = _get_qapp()
    icon_path = app_module.get_app_icon_path()
    assert icon_path.exists()
    assert icon_path.suffix.lower() in (".ico", ".png")

    qicon = app_module.get_app_icon()
    assert qicon is not None
    assert not qicon.isNull()
