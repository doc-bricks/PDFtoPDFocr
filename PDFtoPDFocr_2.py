#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""PDFtoPDFocr - OCR processing GUI for PDF files.

A PyQt5 application that processes PDF files using OCR (text recognition)
and saves the result as a new PDF with the suffix "_ocred.pdf" in the same folder.
Uses pdf2image + pytesseract + pikepdf (no PyMuPDF required).
Missing Tesseract language packs are automatically downloaded from GitHub.
"""

import platform
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
from PyQt5.QtCore import Qt

# OCR / PDF libs
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import pikepdf

# Utilities
ICON_OK, ICON_ERR, ICON_BROOM, ICON_TRASH = "✓", "⚠", "🧹", "🗑"
SUPPORTED_EXTS = {".pdf"}

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
                QMessageBox.critical(None, "Fehler",
                    f"Katarakt-Download fehlgeschlagen (HTTP {r.status_code}).")
                return ""
        except Exception as e:
            QMessageBox.critical(None, "Fehler",
                f"Katarakt konnte nicht geladen werden:\n{e}")
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
        QMessageBox.critical(None, "Fehler",
            "Tesseract OCR wurde nicht gefunden.\nBitte installieren: https://tesseract-ocr.github.io/tessdoc/Installation.html")
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
                QMessageBox.information(None, "Download",
                    f"Sprachpaket '{lang}' wurde automatisch heruntergeladen.")
            else:
                QMessageBox.critical(None, "Fehler",
                    f"Download von {lang}.traineddata fehlgeschlagen (HTTP {r.status_code}).")
                return False
        except Exception as e:
            QMessageBox.critical(None, "Fehler",
                f"Sprachpaket '{lang}' konnte nicht geladen werden:\n{e}")
            return False

    return True


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
        self.setWindowTitle("PDF OCR Tool (pdf2image + Tesseract)")
        self.resize(640, 520)
        self.layout = QVBoxLayout(self)

        self.list_widget = PDFListWidget()
        self.layout.addWidget(self.list_widget)

        # Spracheinstellung
        lang_layout = QHBoxLayout()
        lang_label = QLabel("OCR-Sprache:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["deu", "eng", "fra", "spa"])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        self.layout.addLayout(lang_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton("Datei hinzufügen")
        self.btn_start = QPushButton("Start")
        self.btn_refresh = QPushButton(f"{ICON_BROOM} Refresh")
        self.btn_delete = QPushButton(f"{ICON_TRASH} Delete")
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

        # Optional: Poppler-Pfad-Eingabe (falls gebraucht)
        # Der Benutzer kann POPPLER_PATH als Umgebungsvariable setzen oder hier anpassen.
        # Wenn leer, wird pdf2image versuchen, Poppler aus PATH zu nutzen.
        self.poppler_path = ""  # leer = pdf2image nutzt System-Poppler

    def open_file_dialog(self):
        """Opens a file dialog to select PDF files and adds them to the list."""
        files, _ = QFileDialog.getOpenFileNames(self, "Wähle PDF-Dateien", "", "PDF-Dateien (*.pdf)")
        for f in files:
            self.list_widget.add_file(f)

    def on_start(self):
        """Starts OCR processing for all pending files in the list."""
        self.status_label.setText("")
        pending = [self.list_widget.item(i) for i in range(self.list_widget.count())
                   if self.list_widget.item(i).data(Qt.UserRole + 1) == 'pending']
        if not pending:
            self.status_label.setText("Keine neuen Dateien zum Verarbeiten.")
            return

        lang = self.lang_combo.currentText()

        # Optional: Katarakt prüfen (nicht zwingend nötig hier)
        # if not ensure_katarakt():
        #     return

        # Tesseract sicherstellen
        if not ensure_tesseract(lang):
            return

        for item in pending:
            path = item.data(Qt.UserRole)
            self.status_label.setText(f"Verarbeite: {os.path.basename(path)} ...")
            # Process pending GUI events so the window remains responsive
            # between files. Full freeze during OCR of a single file is a known
            # limitation (would require QThread refactor).
            QApplication.processEvents()
            success = self.ocr_pdf(path, lang)
            if success:
                item.setText(f"{ICON_OK} {os.path.basename(path)}")
                item.setForeground(QColor('green'))
                item.setData(Qt.UserRole + 1, 'done')
            else:
                item.setText(f"{ICON_ERR} {os.path.basename(path)}")
                item.setForeground(QColor('orange'))
                item.setData(Qt.UserRole + 1, 'error')
            QApplication.processEvents()

        if all(self.list_widget.item(i).data(Qt.UserRole + 1) != 'pending'
               for i in range(self.list_widget.count())):
            self.status_label.setText("Prozess abgeschlossen!")
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

    def ocr_pdf(self, src_path: str, lang: str) -> bool:
        """Converts a PDF to a searchable OCR PDF and saves it with the suffix ``_ocred.pdf``.

        Pipeline: pdf2image renders pages → pytesseract generates per-page PDFs
        → pikepdf merges all pages into one output file.

        Args:
            src_path: Absolute path to the source PDF.
            lang: Tesseract language code (e.g. "deu", "eng").

        Returns:
            True on success, False if an exception occurred.
        """
        try:
            poppler_path = self.poppler_path or None

            # Rendern aller Seiten als PIL-Images
            images: List[Image.Image] = convert_from_path(src_path, dpi=300, poppler_path=poppler_path)

            # Prepare an empty pikepdf document for the merged result
            out_pdf = pikepdf.Pdf.new()
            try:
                for img in images:
                    if img.mode != "RGB":
                        img = img.convert("RGB")

                    # OCR auf dem Bild -> PDF-Bytes
                    pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, lang=lang, extension='pdf')
                    if not pdf_bytes:
                        continue

                    # Öffne die von Tesseract erzeugte Ein-Seiten-PDF mit pikepdf und hänge die Seiten an
                    try:
                        src_pdf = pikepdf.Pdf.open(io.BytesIO(pdf_bytes))
                        out_pdf.pages.extend(src_pdf.pages)
                        src_pdf.close()
                    except Exception:
                        # Fallback über temporäre Datei falls pikepdf Probleme macht
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
                            except Exception:
                                pass

                # Ergebnis speichern
                dst_path = os.path.splitext(src_path)[0] + "_ocred.pdf"
                out_pdf.save(dst_path)
            finally:
                out_pdf.close()
            return True

        except Exception as e:
            print(f"OCR-Fehler bei {src_path}: {e}")
            return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = OCRConverterGUI()
    gui.show()
    sys.exit(app.exec_())
