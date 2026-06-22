#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""PDFtoPDFocr - OCR processing GUI for PDF files.

A PySide6 application that processes PDF files using OCR (text recognition)
and saves the result as a new PDF with the suffix "_ocred.pdf" in the same folder.
Uses pdf2image + pytesseract + pikepdf (no PyMuPDF required).
Missing Tesseract language packs are automatically downloaded from GitHub.
"""

import json
import logging
import sys, os, io, shutil, requests, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List

# PySide6
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem,
    QFileDialog, QLabel, QComboBox, QMessageBox
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QThread, Signal

# OCR / PDF libs
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import pikepdf

# Utilities
ICON_OK, ICON_ERR, ICON_BROOM, ICON_TRASH = "✓", "⚠", "🧹", "🗑"
SUPPORTED_EXTS = {".pdf"}
APP_NAME = "PDFtoPDFocr"
APP_VERSION = "1.0.4"
EXPORT_SCHEMA = "pdftopdfocr-job-v1"
DEFAULT_OCR_DPI = 300

# ===== i18n =====

def _load_translations() -> dict:
    """Lädt translations.json aus dem Skript-Verzeichnis."""
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
    """Gibt den übersetzten String für key in der aktuellen Sprache zurück.

    Falls kein Eintrag vorhanden ist, wird key als Fallback zurückgegeben.
    Unterstützt Platzhalter via str.format(**kwargs).

    Args:
        key: Schlüssel aus translations.json.
        **kwargs: Optionale Platzhalter-Werte (z.B. lang="deu").

    Returns:
        Übersetzter String.
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


def _app_base_dir() -> Path:
    """Returns the script or PyInstaller extraction directory."""
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))


def _portable_tesseract_cmd() -> str | None:
    """Finds a bundled Tesseract executable if the portable runtime exists."""
    exe_name = "tesseract.exe" if os.name == "nt" else "tesseract"
    candidates = [
        _app_base_dir() / "tesseract_portable" / exe_name,
        _app_base_dir() / exe_name,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def configure_tesseract() -> str | None:
    """Configures pytesseract to use portable Tesseract before PATH fallback."""
    env_cmd = os.environ.get("TESSERACT_CMD")
    candidates = [
        env_cmd if env_cmd and os.path.isfile(env_cmd) else None,
        _portable_tesseract_cmd(),
        shutil.which("tesseract"),
    ]
    for cmd in candidates:
        if cmd:
            pytesseract.pytesseract.tesseract_cmd = cmd
            return cmd
    return None


def get_tessdata_dir() -> str:
    """Locates the Tesseract tessdata directory, or creates a local fallback.

    Returns:
        Path to the tessdata directory as a string.
    """
    env_dir = os.environ.get("TESSDATA_PREFIX")
    if env_dir and os.path.isdir(env_dir):
        return env_dir
    base_dir = _app_base_dir()
    bundled_tessdata = base_dir / "tesseract_portable" / "tessdata"
    if bundled_tessdata.is_dir():
        return str(bundled_tessdata)
    local_tessdata = base_dir / "tessdata"
    if local_tessdata.is_dir():
        return str(local_tessdata)
    for c in DEFAULT_TESSDATA_CANDIDATES:
        if os.path.isdir(c):
            return c
    fallback = base_dir / "tessdata"
    fallback.mkdir(exist_ok=True)
    return str(fallback)


def ensure_tesseract(lang: str) -> bool:
    """Verifies that Tesseract and the requested language pack are available.

    Downloads the language traineddata file from tesseract-ocr/tessdata_best if missing.

    Args:
        lang: Tesseract language code (e.g. "deu", "eng").

    Returns:
        True if Tesseract and the language pack are ready, False otherwise.
    """
    if not configure_tesseract():
        QMessageBox.critical(None, tr("error_title"),
            tr("error_tesseract_not_found"))
        return False

    tessdata_dir = get_tessdata_dir()
    os.makedirs(tessdata_dir, exist_ok=True)
    os.environ["TESSDATA_PREFIX"] = tessdata_dir
    target = os.path.join(tessdata_dir, f"{lang}.traineddata")

    if not os.path.exists(target):
        try:
            url = f"https://github.com/tesseract-ocr/tessdata_best/raw/main/{lang}.traineddata"
            r = requests.get(url, stream=True, timeout=30)
            if r.status_code == 200:
                # Write to a temp file first; rename atomically so a mid-stream
                # network failure never leaves a truncated .traineddata on disk.
                tmp_fd, tmp_name = tempfile.mkstemp(
                    dir=tessdata_dir, suffix=".traineddata.tmp"
                )
                try:
                    with os.fdopen(tmp_fd, "wb") as f:
                        shutil.copyfileobj(r.raw, f)
                    shutil.move(tmp_name, target)
                except Exception:
                    try:
                        os.unlink(tmp_name)
                    except OSError:
                        pass
                    raise
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


def _utc_now_iso() -> str:
    """Returns a stable UTC timestamp for export payloads."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _manifest_path(raw_path: str) -> str:
    """Normalizes file paths for JSON manifests while preserving relativity."""
    return Path(raw_path).as_posix()


def _export_status(status: str) -> str:
    """Maps internal UI states to the public export schema."""
    return {
        "done": "success",
        "error": "failed",
        "pending": "pending",
    }.get(status, "pending")


def build_job_export_payload(
    file_entries: list[dict],
    ocr_language: str,
    created_at: str | None = None,
) -> dict:
    """Builds the portable OCR job manifest without embedding PDF content."""
    input_files = []
    outputs = []

    for entry in file_entries:
        raw_path = entry["path"]
        source_path = Path(raw_path)
        output_path = source_path.with_name(f"{source_path.stem}_ocred.pdf")
        source_exists = source_path.exists()
        output_exists = output_path.exists()

        input_files.append(
            {
                "name": source_path.name,
                "local_path": _manifest_path(raw_path),
                "size_bytes": source_path.stat().st_size if source_exists else None,
                "missing": not source_exists,
            }
        )
        outputs.append(
            {
                "input_name": source_path.name,
                "input_local_path": _manifest_path(raw_path),
                "output_name": output_path.name,
                "status": _export_status(entry.get("status", "pending")),
                "message": entry.get("message", ""),
                "output_local_path": output_path.as_posix(),
                "output_exists": output_exists,
            }
        )

    return {
        "schema": EXPORT_SCHEMA,
        "app": APP_NAME,
        "app_version": APP_VERSION,
        "created_at": created_at or _utc_now_iso(),
        "ocr_language": ocr_language,
        "input_files": input_files,
        "outputs": outputs,
        "settings": {
            "dpi": DEFAULT_OCR_DPI,
            "preserve_original": True,
            "download_missing_language_pack": True,
        },
    }


def write_job_export(target_path: str | Path, payload: dict) -> Path:
    """Writes the OCR job manifest as UTF-8 JSON without BOM."""
    export_path = Path(target_path)
    export_path.parent.mkdir(parents=True, exist_ok=True)
    export_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return export_path


class OCRWorker(QThread):
    """Führt OCR-Verarbeitung im Hintergrund aus, sodass die GUI responsiv bleibt.

    Signals:
        file_done(str, bool): Pfad + Erfolgsstatus für jede fertige Datei.
        progress(str): Statusmeldung für das Label.
        finished_all(): Alle Dateien wurden verarbeitet.
    """
    file_done = Signal(str, bool)
    progress = Signal(str)
    finished_all = Signal()

    def __init__(self, pending_paths: list, lang: str, poppler_path: str = "", parent=None):
        super().__init__(parent)
        self.pending_paths = pending_paths
        self.lang = lang
        self.poppler_path = poppler_path

    def run(self):
        for path in self.pending_paths:
            self.progress.emit(tr("status_processing", filename=os.path.basename(path)))
            success = self._ocr_pdf(path, self.lang)
            self.file_done.emit(path, success)
        self.finished_all.emit()

    def _ocr_pdf(self, src_path: str, lang: str) -> bool:
        """Führt OCR auf einer PDF-Datei aus (läuft im Worker-Thread)."""
        try:
            poppler_path = self.poppler_path or None
            images: List[Image.Image] = convert_from_path(src_path, dpi=300, poppler_path=poppler_path)

            out_pdf = pikepdf.Pdf.new()
            # FIX: pikepdf kopiert Seiten LAZY -> die Quell-PDFs (und temp-Dateien)
            # muessen bis NACH out_pdf.save() geoeffnet bleiben. Vorher wurde src_pdf
            # im Loop VOR dem Speichern geschlossen (und tmp geloescht) -> korrupte/
            # fehlende OCR-Seiten moeglich. Daher sammeln, erst im finally schliessen.
            page_sources = []  # (pikepdf.Pdf, tmp_path_or_None)
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
                        page_sources.append((src_pdf, None))
                    except Exception as e:
                        logging.warning(f"PDF operation failed: {e}")
                        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        tmp.write(pdf_bytes)
                        tmp.flush()
                        tmp.close()
                        src_pdf = pikepdf.Pdf.open(tmp.name)
                        out_pdf.pages.extend(src_pdf.pages)
                        page_sources.append((src_pdf, tmp.name))

                if len(out_pdf.pages) == 0:
                    raise ValueError("OCR produced no pages — all pages yielded empty PDF bytes")
                dst_path = os.path.splitext(src_path)[0] + "_ocred.pdf"
                out_pdf.save(dst_path)
            finally:
                # Quell-PDFs + temp-Dateien erst NACH save() schliessen/aufraeumen.
                for _src_pdf, _tmp in page_sources:
                    try:
                        _src_pdf.close()
                    except Exception:
                        pass
                    if _tmp:
                        try:
                            os.unlink(_tmp)
                        except OSError:
                            pass
                out_pdf.close()
            return True
        except Exception as e:
            # logging statt print: im windowed-PyInstaller ist sys.stdout None ->
            # print() wuerde den Worker-Thread crashen (finished_all nie emittiert,
            # GUI haengt mit dauerhaft deaktiviertem Start-Button).
            logging.error("OCR-Fehler bei %s: %s", src_path, e)
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
        item.setData(Qt.UserRole + 2, "")
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
        self.btn_export = QPushButton(tr("btn_export_job"))
        self.btn_refresh = QPushButton(f"{ICON_BROOM} {tr('btn_refresh')}")
        self.btn_delete = QPushButton(f"{ICON_TRASH} {tr('btn_delete')}")
        for b in (
            self.btn_add_file,
            self.btn_start,
            self.btn_export,
            self.btn_refresh,
            self.btn_delete,
        ):
            btn_layout.addWidget(b)
        self.layout.addLayout(btn_layout)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # Events
        self.btn_add_file.clicked.connect(self.open_file_dialog)
        self.btn_start.clicked.connect(self.on_start)
        self.btn_export.clicked.connect(self.export_job_manifest)
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
        """Startet OCR-Verarbeitung für alle ausstehenden Dateien in einem QThread (GUI bleibt responsiv)."""
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
                    item.setData(Qt.UserRole + 2, tr("message_ocr_success"))
                else:
                    item.setText(f"{ICON_ERR} {os.path.basename(path)}")
                    item.setForeground(QColor('orange'))
                    item.setData(Qt.UserRole + 1, 'error')
                    item.setData(Qt.UserRole + 2, tr("message_ocr_failed"))
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

    def closeEvent(self, event):
        """Wartet auf laufenden OCR-Worker bevor das Fenster geschlossen wird."""
        if self._ocr_worker is not None and self._ocr_worker.isRunning():
            self._ocr_worker.wait()
        event.accept()

    def on_delete(self):
        """Removes the currently selected entries from the file list."""
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def _collect_job_entries(self) -> list[dict]:
        """Collects the current GUI state for export and later companion use."""
        entries = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            entries.append(
                {
                    "path": item.data(Qt.UserRole),
                    "status": item.data(Qt.UserRole + 1) or "pending",
                    "message": item.data(Qt.UserRole + 2) or "",
                }
            )
        return entries

    def export_job_manifest(
        self,
        checked: bool = False,
        target_path: str | Path | None = None,
        show_feedback: bool = True,
    ) -> Path | None:
        """Exports the current OCR job state to the portable JSON manifest."""
        del checked
        entries = self._collect_job_entries()
        if target_path is None:
            default_dir = Path(entries[0]["path"]).parent if entries else Path.cwd()
            default_name = default_dir / f"{EXPORT_SCHEMA}.json"
            chosen_path, _ = QFileDialog.getSaveFileName(
                self,
                tr("dialog_export_job"),
                str(default_name),
                tr("filter_json"),
            )
            if not chosen_path:
                return None
            target_path = chosen_path

        payload = build_job_export_payload(entries, self.lang_combo.currentText())
        written_path = write_job_export(target_path, payload)
        self.status_label.setText(tr("status_export_saved", filename=written_path.name))
        self.status_label.setStyleSheet("color: #0b6e4f; font-weight: bold;")
        if show_feedback:
            QMessageBox.information(
                self,
                tr("info_export_title"),
                tr("info_export_saved", filename=written_path.name),
            )
        return written_path

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = OCRConverterGUI()
    gui.show()
    sys.exit(app.exec())
