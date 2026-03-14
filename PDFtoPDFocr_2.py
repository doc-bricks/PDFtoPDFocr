#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""PDFtoPDFocr - OCR processing GUI for PDF files.

A PyQt5 application that processes PDF files using OCR (text recognition)
and saves the result as a new PDF with the suffix "_ocred.pdf" in the same folder.
Uses pdf2image + pytesseract + pikepdf (no PyMuPDF required).
Missing Tesseract language packs are automatically downloaded from GitHub.
"""

import platform
import logging
import sys, os, io, shutil, subprocess, requests, tempfile, zipfile
from pathlib import Path
from typing import List

# PyQt5
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem,
    QFileDialog, QLabel, QComboBox, QMessageBox
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# OCR / PDF libs
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import pikepdf

# Utilities
ICON_OK, ICON_ERR, ICON_BROOM, ICON_TRASH = "✓", "⚠", "🧹", "🗑"
SUPPORTED_EXTS = {".pdf"}

# ===== i18n =====

def _load_translations() -> dict:
    """Laedt translations.json aus dem Skript-Verzeichnis."""
    try:
        base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, "translations.json")
        with open(path, "r", encoding="utf-8") as f:
            import json
            return json.load(f)
    except Exception:
        return {}

_TRANSLATIONS = _load_translations()
_LANG = "de"  # Standard: Deutsch; wechselbar via set_language()


def set_language(lang: str) -> None:
    """Setzt die aktive Sprache (z.B. 'de' oder 'en')."""
    global _LANG
    _LANG = lang


def tr(key: str, **kwargs) -> str:
    """Gibt den uebersetzten String fuer key in der aktuellen Sprache zurueck.

    Falls kein Eintrag vorhanden ist, wird key als Fallback zurueckgegeben.
    Unterstuetzt Platzhalter via str.format(**kwargs).

    Args:
        key: Schluessel aus translations.json.
        **kwargs: Optionale Platzhalter-Werte (z.B. lang="deu").

    Returns:
        Uebersetzter String.
    """
    entry = _TRANSLATIONS.get(key, {})
    text = entry.get(_LANG, entry.get("de", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text

# Defaults
DEFAULT_TESSDATA_CANDIDATES = [
    r"C:\Program Files\Tesseract-OCR\tessdata",
    r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
    "/usr/share/tesseract-ocr/4.00/tessdata",
    "/usr/share/tesseract-ocr/tessdata",
    "/usr/local/share/tessdata"
]


def get_katarakt_path() -> str:
    """Returns the path to the katarakt executable, downloading it if not present.

    Optional helper; retained for compatibility.

    Returns:
        Absolute path to the katarakt binary, or empty string on failure.
    """
    if os.name == "nt":
        base_dir = Path(os.getenv("LOCALAPPDATA", Path.home()))
        exe_name = "katarakt.exe"
    else:
        base_dir = Path.home() / ".local" / "share"
        exe_name = "katarakt"

    katarakt_dir = base_dir / "pdfocr" / "katarakt"
    katarakt_dir.mkdir(parents=True, exist_ok=True)

    exe_path = katarakt_dir / exe_name

    if not exe_path.exists():
        try:
            url = ("https://github.com/JKamlah/katarakt/releases/latest/download/katarakt-windows.zip"
                   if os.name == "nt" else
                   "https://github.com/JKamlah/katarakt/releases/latest/download/katarakt-linux.zip")

            zip_path = katarakt_dir / "katarakt.zip"
            r = requests.get(url, stream=True, timeout=30)
            if r.status_code == 200:
                with open(zip_path, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(katarakt_dir)
                zip_path.unlink()
                if exe_path.exists() and os.name != "nt":
                    exe_path.chmod(0o755)
            else:
                QMessageBox.critical(None, tr("error_title"),
                    tr("error_katarakt_download_failed", status=r.status_code))
                return ""
        except Exception as e:
            QMessageBox.critical(None, tr("error_title"),
                tr("error_katarakt_load_failed", error=e))
            return ""

    return str(exe_path)


def ensure_katarakt() -> bool:
    """Checks whether katarakt is available, downloading it if necessary.

    Returns:
        True if the binary exists after the check, False otherwise.
    """
    exe = get_katarakt_path()
    return bool(exe and os.path.exists(exe))


def get_tessdata_dir() -> str:
    """Locates the Tesseract tessdata directory, or creates a local fallback.

    Returns:
        Path to the tessdata directory as a string.
    """
    env_dir = os.environ.get("TESSDATA_PREFIX")
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    for c in DEFAULT_TESSDATA_CANDIDATES:
        if os.path.isdir(c):
            return c
    fallback = os.path.join(os.getcwd(), "tessdata")
    os.makedirs(fallback, exist_ok=True)
    return fallback


def ensure_tesseract(lang: str) -> bool:
    """Verifies that Tesseract and the requested language pack are available.

    Downloads the language traineddata file from tesseract-ocr/tessdata_best if missing.

    Args:
        lang: Tesseract language code (e.g. "deu", "eng").

    Returns:
        True if Tesseract and the language pack are ready, False otherwise.
    """
    if not shutil.which("tesseract"):
        QMessageBox.critical(None, tr("error_title"),
            tr("error_tesseract_not_found"))
        return False

    tessdata_dir = get_tessdata_dir()
    os.makedirs(tessdata_dir, exist_ok=True)
    target = os.path.join(tessdata_dir, f"{lang}.traineddata")

    if not os.path.exists(target):
        try:
            url = f"https://github.com/tesseract-ocr/tessdata_best/raw/main/{lang}.traineddata"
            r = requests.get(url, stream=True, timeout=30)
            if r.status_code == 200:
                with open(target, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
                QMessageBox.information(None, tr("info_download_title"),
                    tr("info_lang_downloaded", lang=lang))
            else:
                QMessageBox.critical(None, tr("error_title"),
                    tr("error_lang_download_failed", lang=lang, status=r.status_code))
                return False
        except Exception as e:
            QMessageBox.critical(None, tr("error_title"),
                tr("error_lang_load_failed", lang=lang, error=e))
            return False

    return True


class OCRWorker(QThread):
    """Fuehrt OCR-Verarbeitung im Hintergrund aus, sodass die GUI responsiv bleibt.

    Signals:
        file_done(str, bool): Pfad + Erfolgsstatus fuer jede fertige Datei.
        progress(str): Statusmeldung fuer das Label.
        finished_all(): Alle Dateien wurden verarbeitet.
    """
    file_done = pyqtSignal(str, bool)
    progress = pyqtSignal(str)
    finished_all = pyqtSignal()

    def __init__(self, pending_paths: list, lang: str, poppler_path: str = "", parent=None):
        super().__init__(parent)
        self.pending_paths = pending_paths
        self.lang = lang
        self.poppler_path = poppler_path

    def run(self):
        for path in self.pending_paths:
            self.progress.emit(f"Verarbeite: {os.path.basename(path)} ...")
            success = self._ocr_pdf(path, self.lang)
            self.file_done.emit(path, success)
        self.finished_all.emit()

    def _ocr_pdf(self, src_path: str, lang: str) -> bool:
        """Fuehrt OCR auf einer PDF-Datei aus (laeuft im Worker-Thread)."""
        try:
            poppler_path = self.poppler_path or None
            images: List[Image.Image] = convert_from_path(src_path, dpi=300, poppler_path=poppler_path)

            out_pdf = pikepdf.Pdf.new()
            try:
                for img in images:
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, lang=lang, extension='pdf')
                    if not pdf_bytes:
                        continue
                    try:
                        src_pdf = pikepdf.Pdf.open(io.BytesIO(pdf_bytes))
                        out_pdf.pages.extend(src_pdf.pages)
                        src_pdf.close()
                    except Exception as e:
                        logging.warning(f"PDF operation failed: {e}")
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        try:
                            tmp.write(pdf_bytes)
                            tmp.flush()
                            tmp.close()
                            src_pdf = pikepdf.Pdf.open(tmp.name)
                            out_pdf.pages.extend(src_pdf.pages)
                            src_pdf.close()
                        finally:
                            try:
                                os.unlink(tmp.name)
                            except Exception as e:
                                logging.warning(f"PDF operation failed: {e}")

                dst_path = os.path.splitext(src_path)[0] + "_ocred.pdf"
                out_pdf.save(dst_path)
            finally:
                out_pdf.close()
            return True
        except Exception as e:
            print(f"OCR-Fehler bei {src_path}: {e}")
            return False


class PDFListWidget(QListWidget):
    """QListWidget with drag-and-drop support for PDF files and folders."""

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dragMoveEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                self.add_folder(path)
            elif os.path.isfile(path):
                self.add_file(path)
        e.acceptProposedAction()

    def add_folder(self, folder):
        """Adds all supported files from a folder to the list.

        Args:
            folder: Path to the directory to scan.
        """
        for fname in os.listdir(folder):
            full = os.path.join(folder, fname)
            if os.path.isfile(full):
                self.add_file(full)

    def add_file(self, filepath):
        """Adds a single file to the list if it has a supported extension and is not already listed.

        Args:
            filepath: Absolute path to the file to add.
        """
        if os.path.splitext(filepath)[1].lower() not in SUPPORTED_EXTS:
            return
        for idx in range(self.count()):
            if self.item(idx).data(Qt.UserRole) == filepath:
                return
        item = QListWidgetItem(os.path.basename(filepath))
        item.setData(Qt.UserRole, filepath)
        item.setData(Qt.UserRole + 1, 'pending')
        self.addItem(item)


class OCRConverterGUI(QWidget):
    """Main application window for batch OCR processing of PDF files."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("window_title"))
        self.resize(640, 520)
        self.layout = QVBoxLayout(self)
        self._ocr_worker = None  # Referenz auf laufenden QThread

        self.list_widget = PDFListWidget()
        self.layout.addWidget(self.list_widget)

        # Spracheinstellung
        lang_layout = QHBoxLayout()
        lang_label = QLabel(tr("label_ocr_lang"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["deu", "eng", "fra", "spa"])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        self.layout.addLayout(lang_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton(tr("btn_add_file"))
        self.btn_start = QPushButton(tr("btn_start"))
        self.btn_refresh = QPushButton(f"{ICON_BROOM} {tr('btn_refresh')}")
        self.btn_delete = QPushButton(f"{ICON_TRASH} {tr('btn_delete')}")
        for b in (self.btn_add_file, self.btn_start, self.btn_refresh, self.btn_delete):
            btn_layout.addWidget(b)
        self.layout.addLayout(btn_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # Events
        self.btn_add_file.clicked.connect(self.open_file_dialog)
        self.btn_start.clicked.connect(self.on_start)
        self.btn_refresh.clicked.connect(self.on_refresh)
        self.btn_delete.clicked.connect(self.on_delete)

        # Poppler-Pfad: leer = pdf2image nutzt System-Poppler
        self.poppler_path = ""

    def open_file_dialog(self):
        """Opens a file dialog to select PDF files and adds them to the list."""
        files, _ = QFileDialog.getOpenFileNames(self, tr("dialog_select_files"), "", tr("filter_pdf"))
        for f in files:
            self.list_widget.add_file(f)

    def on_start(self):
        """Startet OCR-Verarbeitung fuer alle ausstehenden Dateien in einem QThread (GUI bleibt responsiv)."""
        self.status_label.setText("")
        pending_items = [self.list_widget.item(i) for i in range(self.list_widget.count())
                         if self.list_widget.item(i).data(Qt.UserRole + 1) == 'pending']
        if not pending_items:
            self.status_label.setText(tr("status_no_files"))
            return

        lang = self.lang_combo.currentText()
        if not ensure_tesseract(lang):
            return

        # Worker starten
        pending_paths = [it.data(Qt.UserRole) for it in pending_items]
        self._ocr_worker = OCRWorker(pending_paths, lang, self.poppler_path, parent=self)
        self._ocr_worker.progress.connect(self._on_ocr_progress)
        self._ocr_worker.file_done.connect(self._on_file_done)
        self._ocr_worker.finished_all.connect(self._on_ocr_finished)
        self.btn_start.setEnabled(False)
        self._ocr_worker.start()

    def _on_ocr_progress(self, msg: str):
        """Statusmeldung vom Worker empfangen."""
        self.status_label.setText(msg)
        self.status_label.setStyleSheet("")

    def _on_file_done(self, path: str, success: bool):
        """Ergebnis einer einzelnen Datei anzeigen."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == path:
                if success:
                    item.setText(f"{ICON_OK} {os.path.basename(path)}")
                    item.setForeground(QColor('green'))
                    item.setData(Qt.UserRole + 1, 'done')
                else:
                    item.setText(f"{ICON_ERR} {os.path.basename(path)}")
                    item.setForeground(QColor('orange'))
                    item.setData(Qt.UserRole + 1, 'error')
                break

    def _on_ocr_finished(self):
        """Alle Dateien verarbeitet."""
        self.btn_start.setEnabled(True)
        self.status_label.setText(tr("status_done"))
        self.status_label.setStyleSheet("color: green; font-weight: bold;")

    def on_refresh(self):
        """Clears the file list and resets the status label."""
        self.list_widget.clear()
        self.status_label.setText("")
        self.status_label.setStyleSheet("")

    def on_delete(self):
        """Removes the currently selected entries from the file list."""
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = OCRConverterGUI()
    gui.show()
    sys.exit(app.exec_())
