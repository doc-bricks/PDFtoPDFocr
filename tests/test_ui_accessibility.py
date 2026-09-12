# -*- coding: utf-8 -*-
"""UX & Accessibility contract and regression tests for PDFtoPDFocr.

Verifies:
1. Complete AccessibleName and AccessibleDescription on all interactive widgets.
2. Complete, informative tooltips in both German and English.
3. Keyboard ergonomics (shortcuts on primary actions, Del + Backspace support).
4. Dynamic retranslation parity for all A11y and tooltip properties.
5. High-contrast WCAG-compliant status feedback and per-item status tooltips.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

import PDFtoPDFocr_2 as app


def _qapp():
    instance = QApplication.instance()
    if instance is None:
        instance = QApplication([])
    return instance


def test_ui_accessibility_names_and_descriptions():
    """All interactive widgets and status labels have accessible names & descriptions."""
    _qapp()
    app.set_language("de")
    gui = app.OCRConverterGUI()
    try:
        # File list
        assert gui.list_widget.accessibleName() == "PDF-Dateiliste"
        assert "Drag-and-drop" in gui.list_widget.accessibleDescription()

        # Language dropdowns
        assert gui.ui_lang_combo.accessibleName() == "Anzeigesprache:"
        assert len(gui.ui_lang_combo.accessibleDescription()) > 10
        assert gui.lang_combo.accessibleName() == "OCR-Sprache:"
        assert len(gui.lang_combo.accessibleDescription()) > 10

        # Action buttons
        assert gui.btn_add_file.accessibleName() == "Datei hinzufügen"
        assert len(gui.btn_add_file.accessibleDescription()) > 10
        assert gui.btn_start.accessibleName() == "Start"
        assert len(gui.btn_start.accessibleDescription()) > 10
        assert gui.btn_export.accessibleName() == "Job-Export"
        assert len(gui.btn_export.accessibleDescription()) > 10
        assert "Löschen" in gui.btn_delete.accessibleName()
        assert len(gui.btn_delete.accessibleDescription()) > 10
        assert "Aktualisieren" in gui.btn_refresh.accessibleName()
        assert len(gui.btn_refresh.accessibleDescription()) > 10

        # Export folder controls
        assert "Exportordner" in gui.btn_choose_export_folder.accessibleName()
        assert len(gui.btn_choose_export_folder.accessibleDescription()) > 10
        assert gui.btn_reset_export_folder.accessibleName() == "Standard"
        assert len(gui.btn_reset_export_folder.accessibleDescription()) > 10

        # Status & info labels
        assert gui.status_label.accessibleName() == "Verarbeitungsstatus"
        assert gui.export_folder_label.accessibleName() == "Exportordner-Anzeige"
    finally:
        gui.close()


def test_ui_tooltips_completeness():
    """All interactive controls expose informative tooltips in active language."""
    _qapp()
    app.set_language("de")
    gui = app.OCRConverterGUI()
    try:
        assert "Strg+O" in gui.btn_add_file.toolTip()
        assert "Strg+Eingabetaste" in gui.btn_start.toolTip()
        assert "Strg+E" in gui.btn_export.toolTip()
        assert "F5" in gui.btn_refresh.toolTip()
        assert "Entf" in gui.btn_delete.toolTip()
        assert "Strg+Umschalt+O" in gui.btn_choose_export_folder.toolTip()
        assert len(gui.btn_reset_export_folder.toolTip()) > 5
        assert len(gui.ui_lang_combo.toolTip()) > 5
        assert len(gui.lang_combo.toolTip()) > 5
    finally:
        gui.close()


def test_ui_keyboard_shortcuts():
    """Primary action buttons have keyboard shortcuts configured."""
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        assert gui.btn_add_file.shortcut().toString() in ("Ctrl+O", "Strg+O")
        assert gui.btn_start.shortcut().toString() in ("Ctrl+Return", "Ctrl+Enter", "Strg+Eingabetaste")
        assert gui.btn_export.shortcut().toString() in ("Ctrl+E", "Strg+E")
        assert gui.btn_refresh.shortcut().toString() == "F5"
        assert gui.btn_delete.shortcut().toString() in ("Del", "Delete", "Entf")
        assert gui.action_merge.shortcut().toString() in ("Ctrl+M", "Strg+M")
        assert gui.btn_choose_export_folder.shortcut().toString() in ("Ctrl+Shift+O", "Strg+Umschalt+O")
    finally:
        gui.close()


def test_file_list_keyboard_removal_del_and_backspace(tmp_path):
    """File list supports removal via both Delete and Backspace keys."""
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        f1 = tmp_path / "a.pdf"
        f2 = tmp_path / "b.pdf"
        f3 = tmp_path / "c.pdf"
        for f in (f1, f2, f3):
            f.write_bytes(b"%PDF-test\n")
            gui.list_widget.add_file(str(f))

        assert gui.list_widget.count() == 3

        # Test Delete key removal
        item0 = gui.list_widget.item(0)
        item0.setSelected(True)
        gui.list_widget.setCurrentItem(item0)
        QTest.keyClick(gui.list_widget, Qt.Key_Delete)
        QApplication.processEvents()

        assert gui.list_widget.count() == 2
        assert gui.list_widget.item(0).data(Qt.UserRole) == str(f2)

        # Test Backspace key removal
        item_rem = gui.list_widget.item(0)
        item_rem.setSelected(True)
        gui.list_widget.setCurrentItem(item_rem)
        QTest.keyClick(gui.list_widget, Qt.Key_Backspace)
        QApplication.processEvents()

        assert gui.list_widget.count() == 1
        assert gui.list_widget.item(0).data(Qt.UserRole) == str(f3)
    finally:
        gui.close()


def test_language_switch_retranslates_accessibility_and_tooltips():
    """Switching language dynamically updates all tooltips and A11y attributes."""
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        # Switch to English
        app.set_language("en")
        gui.retranslate_ui()

        assert gui.windowTitle() == "PDF OCR Tool"
        assert gui.list_widget.accessibleName() == "PDF file list"
        assert gui.btn_add_file.text() == "Add File"
        assert "Ctrl+O" in gui.btn_add_file.toolTip()
        assert "Ctrl+Enter" in gui.btn_start.toolTip()
        assert gui.status_label.accessibleName() == "Processing status"
        assert gui.export_folder_label.accessibleName() == "Export folder display"

        # Switch back to German
        app.set_language("de")
        gui.retranslate_ui()

        assert gui.windowTitle() == "PDF OCR Werkzeug"
        assert gui.list_widget.accessibleName() == "PDF-Dateiliste"
        assert gui.btn_add_file.text() == "Datei hinzufügen"
        assert "Strg+O" in gui.btn_add_file.toolTip()
        assert gui.status_label.accessibleName() == "Verarbeitungsstatus"
    finally:
        gui.close()


def test_file_done_accessible_contrast_and_tooltips(tmp_path):
    """Completion status applies accessible WCAG colors and descriptive tooltips."""
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        f_ok = tmp_path / "ok.pdf"
        f_err = tmp_path / "err.pdf"
        f_ok.write_bytes(b"%PDF\n")
        f_err.write_bytes(b"%PDF\n")

        gui.list_widget.add_file(str(f_ok))
        gui.list_widget.add_file(str(f_err))

        # Initial hover tooltip matches path
        assert gui.list_widget.item(0).toolTip() == str(f_ok)

        # Trigger success
        gui._on_file_done(str(f_ok), True)
        item_ok = gui.list_widget.item(0)
        assert item_ok.data(Qt.UserRole + 1) == "done"
        assert "erfolgreich" in item_ok.toolTip()
        assert item_ok.foreground().color().name() == "#0b6e4f"

        # Trigger failure
        gui._on_file_done(str(f_err), False)
        item_err = gui.list_widget.item(1)
        assert item_err.data(Qt.UserRole + 1) == "error"
        assert "fehlgeschlagen" in item_err.toolTip()
        assert item_err.foreground().color().name() == "#b45309"
    finally:
        gui.close()


def test_initial_and_refresh_status_guidance():
    """Initial launch and list refresh provide clear accessible status guidance."""
    _qapp()
    app.set_language("de")
    gui = app.OCRConverterGUI()
    try:
        assert gui.status_label.text() == "Bereit. Dateien hierher ziehen oder 'Datei hinzufügen' wählen."
        # Retranslate updates guidance
        app.set_language("en")
        gui.retranslate_ui()
        assert gui.status_label.text() == "Ready. Drag files here or select 'Add File'."
        # Refresh restores ready guidance
        gui.status_label.setText("Temporary status")
        gui.on_refresh()
        assert gui.status_label.text() == "Ready. Drag files here or select 'Add File'."
    finally:
        gui.close()
        app.set_language("de")


def test_list_item_double_click_opens_target(tmp_path, monkeypatch):
    """Double-clicking a list item opens the OCR result if present, else source."""
    _qapp()
    gui = app.OCRConverterGUI()
    opened_paths = []
    monkeypatch.setattr(app, "open_file_path", lambda p: opened_paths.append(str(p)) or True)

    try:
        src_file = tmp_path / "doc.pdf"
        src_file.write_bytes(b"%PDF-doc\n")
        gui.list_widget.add_file(str(src_file))
        item = gui.list_widget.item(0)

        # Before OCR: double click opens source file
        gui._on_item_double_clicked(item)
        assert len(opened_paths) == 1
        assert opened_paths[-1] == str(src_file)

        # After OCR: double click opens _ocred.pdf
        ocred_file = tmp_path / "doc_ocred.pdf"
        ocred_file.write_bytes(b"%PDF-ocred\n")
        gui._on_item_double_clicked(item)
        assert len(opened_paths) == 2
        assert opened_paths[-1] == str(ocred_file)
    finally:
        gui.close()


def test_context_menu_actions_and_shortcuts(tmp_path):
    """Context menu provides Open File, Open Folder, Merge (Ctrl+M), and Delete (Del)."""
    _qapp()
    app.set_language("de")
    gui = app.OCRConverterGUI()
    try:
        f1 = tmp_path / "page1.pdf"
        f2 = tmp_path / "page2.pdf"
        f1.write_bytes(b"%PDF\n")
        f2.write_bytes(b"%PDF\n")
        gui.list_widget.add_file(str(f1))
        gui.list_widget.add_file(str(f2))

        # Single item selected
        item0 = gui.list_widget.item(0)
        item0.setSelected(True)

        menu = gui._create_list_context_menu([item0])
        action_texts = [a.text() for a in menu.actions()]
        assert any("Datei öffnen" in a for a in action_texts)
        assert any("Im Ordner anzeigen" in a for a in action_texts)
        assert any("Löschen" in a for a in action_texts)

        # Both items done -> Merge action is offered
        gui._on_file_done(str(f1), True)
        gui._on_file_done(str(f2), True)
        gui.list_widget.item(1).setSelected(True)

        menu2 = gui._create_list_context_menu(gui.list_widget.selectedItems())
        action_texts2 = [a.text() for a in menu2.actions()]
        assert any("Markierte mergen" in a for a in action_texts2)

        open_action = [a for a in menu.actions() if "Datei öffnen" in a.text()][0]
        assert open_action.shortcut().toString() in ("Return", "Enter", "Eingabetaste")
    finally:
        gui.close()


def test_file_list_keyboard_open_return_and_enter(tmp_path, monkeypatch):
    """File list opens selected item when Return or Enter is pressed."""
    _qapp()
    gui = app.OCRConverterGUI()
    opened_paths = []
    monkeypatch.setattr(app, "open_file_path", lambda p: opened_paths.append(str(p)) or True)

    try:
        f1 = tmp_path / "item1.pdf"
        f1.write_bytes(b"%PDF-item1\n")
        gui.list_widget.add_file(str(f1))
        item = gui.list_widget.item(0)
        item.setSelected(True)
        gui.list_widget.setCurrentItem(item)

        # Press Return
        QTest.keyClick(gui.list_widget, Qt.Key_Return)
        QApplication.processEvents()
        assert len(opened_paths) == 1
        assert opened_paths[-1] == str(f1)

        # Press Numpad Enter
        QTest.keyClick(gui.list_widget, Qt.Key_Enter)
        QApplication.processEvents()
        assert len(opened_paths) == 2
        assert opened_paths[-1] == str(f1)
    finally:
        gui.close()


def test_file_list_keyboard_escape_clears_selection(tmp_path):
    """Pressing Escape in the file list clears the selection for keyboard users."""
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        f1 = tmp_path / "doc.pdf"
        f1.write_bytes(b"%PDF-doc\n")
        gui.list_widget.add_file(str(f1))
        item = gui.list_widget.item(0)
        item.setSelected(True)
        gui.list_widget.setCurrentItem(item)
        assert len(gui.list_widget.selectedItems()) == 1

        QTest.keyClick(gui.list_widget, Qt.Key_Escape)
        QApplication.processEvents()
        assert len(gui.list_widget.selectedItems()) == 0
    finally:
        gui.close()


def test_ui_label_buddies_and_tab_order():
    """Form labels have buddies set and tab order is explicitly configured for A11y."""
    _qapp()
    gui = app.OCRConverterGUI()
    try:
        assert gui.ui_lang_label.buddy() == gui.ui_lang_combo
        assert gui.ocr_lang_label.buddy() == gui.lang_combo
    finally:
        gui.close()

