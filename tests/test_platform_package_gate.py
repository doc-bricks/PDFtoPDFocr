from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
AUFGABEN_PATH = ROOT / "AUFGABEN.txt"


def test_macos_linux_package_gate_documents_non_goal_before_store_and_pwa():
    gate = ROOT / "MACOS_LINUX_PACKAGE_GATE.md"
    text = gate.read_text(encoding="utf-8")

    assert "aktuell nicht gestartet" in text
    assert "Source-Smoke" in text
    assert "Windows-Store" in text
    assert "Web/PWA-Companion" in text
    assert "DMG" in text
    assert "AppImage" in text


@pytest.mark.skipif(
    not AUFGABEN_PATH.exists(),
    reason=(
        "AUFGABEN.txt ist laut .gitignore bewusst lokal/nicht versioniert; "
        "der Sync-Check gilt nur, wenn eine lokale Kopie vorliegt."
    ),
)
def test_task_and_porting_plan_are_synchronized_with_package_gate():
    tasks = AUFGABEN_PATH.read_text(encoding="utf-8")
    porting = (ROOT / "PORTIERUNGSPLAN.md").read_text(encoding="utf-8")

    assert "[x] P3: Eigene macOS-/Linux-Desktop-Packages" in tasks
    assert "DONE 2026-07-03" in tasks
    assert "MACOS_LINUX_PACKAGE_GATE.md" in tasks
    assert "P3: Paket-Gate dokumentiert" in porting
    assert "keine eigene Paketlinie" in porting
