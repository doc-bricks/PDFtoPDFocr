#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""PDFtoPDFocr - OCR processing GUI for PDF files.

A PySide6 application that processes PDF files using OCR (text recognition)
and saves the result as a new PDF with the suffix "_ocred.pdf" in the same folder.
Uses pdf2image + pytesseract + pikepdf (no PyMuPDF required).
Missing Tesseract language packs are automatically downloaded from GitHub.
"""

import io
import json
import logging
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import List
import uuid
from datetime import datetime, timezone
import requests

# PySide6
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QColor, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# OCR / PDF libs
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import pikepdf

# Utilities
ICON_OK, ICON_ERR, ICON_BROOM, ICON_TRASH = "✓", "⚠", "🧹", "🗑"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
SUPPORTED_EXTS = {".pdf"} | IMAGE_EXTS
APP_NAME = "PDFtoPDFocr"
APP_VERSION = "1.1.3"
EXPORT_SCHEMA = "pdftopdfocr-job-v1"
DEFAULT_OCR_DPI = 300
MERGE_SUBFOLDER_NAME = "Einzeldateien"


def get_project_root() -> Path:
    """Liefert das Root-Verzeichnis des Projekts bzw. das PyInstaller-Bundle-Verzeichnis."""
    if getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def get_app_icon_path() -> Path:
    """Liefert den Pfad zum Standard-App-Icon (bevorzugt assets/icon.png oder PDFtoPDFocr.ico)."""
    root = get_project_root()
    candidates = [
        Path(sys.executable).with_name("PDFtoPDFocr.ico") if getattr(sys, "frozen", False) else None,
        Path(sys.executable).with_name("icon.png") if getattr(sys, "frozen", False) else None,
        root / "assets" / "icon.png",
        root / "assets" / "app_icon.ico",
        root / "assets" / "icon.ico",
        root / "PDFtoPDFocr.ico",
        root / "PDFtoPDFocr.png",
        root / "ICO.ico",
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return root / "PDFtoPDFocr.ico"


def get_app_icon() -> QIcon:
    """Erzeugt ein QIcon aus den vorhandenen App-Icon-Pfaden."""
    icon_path = get_app_icon_path()
    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()


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


def get_language() -> str:
    """Gibt die aktuell aktive UI-Sprache zurück."""
    return _LANG


# ===== UI-Sprache: Persistenz (Welle-1 U1) =====

_UI_LANGUAGES = ("de", "en")


def _ui_config_dir() -> Path:
    """Per-User-Konfigverzeichnis (auch bei read-only Store-Install schreibbar)."""
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(
            os.path.expanduser("~"), ".config"
        )
    return Path(base) / "PDFtoPDFocr"


def _ui_config_path() -> Path:
    return _ui_config_dir() / "config.json"


def load_ui_language() -> str:
    """Gespeicherte UI-Sprache ('de'/'en'), Default 'de'."""
    try:
        with open(_ui_config_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        lang = data.get("ui_language", "de") if isinstance(data, dict) else "de"
    except (OSError, ValueError):
        lang = "de"
    return lang if lang in _UI_LANGUAGES else "de"


def save_ui_language(lang: str) -> bool:
    """Persistiert die UI-Sprache in der App-Konfiguration; True bei Erfolg."""
    if lang not in _UI_LANGUAGES:
        return False
    return _update_app_config({"ui_language": lang})


def _update_app_config(updates: dict) -> bool:
    """Liest die App-Konfiguration, mischt `updates` ein und schreibt sie zurueck.

    Gemeinsamer Persistenzmechanismus fuer UI-Sprache (U6) und Exportordner (U4):
    beide leben in derselben config.json, damit auch unter Store-Sandboxing
    (read-only Installationsverzeichnis) nur EIN beschreibbarer Ort noetig ist.
    """
    data = {}
    try:
        with open(_ui_config_path(), "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            data = loaded
    except (OSError, ValueError):
        data = {}
    data.update(updates)
    try:
        _ui_config_dir().mkdir(parents=True, exist_ok=True)
        with open(_ui_config_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False


def load_export_folder() -> str | None:
    """Gespeicherter Exportordner (U4), oder None wenn nicht gesetzt."""
    try:
        with open(_ui_config_path(), "r", encoding="utf-8") as f:
            data = json.load(f)
        folder = data.get("export_folder") if isinstance(data, dict) else None
    except (OSError, ValueError):
        folder = None
    return folder or None


def save_export_folder(folder: str | None) -> bool:
    """Persistiert den Exportordner (U4); None/"" setzt auf Standard zurueck."""
    return _update_app_config({"export_folder": folder or ""})


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


# ===== Merge/Stapeln (Welle-1 U2/U3/U4/U5) =====

def resolve_export_folder(
    source_path: str | Path, configured_folder: str | Path | None
) -> Path:
    """Resolves the target folder for a merge (U4): configured export folder if it
    exists, otherwise the folder of the source file (default per U3).

    Args:
        source_path: A file whose parent folder serves as the fallback.
        configured_folder: User-configured export folder, or None/empty.

    Returns:
        The resolved export folder path.
    """
    if configured_folder:
        candidate = Path(configured_folder)
        if candidate.is_dir():
            return candidate
    return Path(source_path).parent


def merge_ocr_outputs(
    output_paths: list[str],
    merged_name: str,
    export_folder: str | Path,
    subfolder_name: str = MERGE_SUBFOLDER_NAME,
) -> Path:
    """Merges already-OCRed single-file result PDFs into one collective PDF (U2).

    Per U3, the individual page PDFs are moved into `export_folder/subfolder_name`
    and the collective PDF is written at the root of `export_folder`.

    Args:
        output_paths: OCR result PDFs, in the desired page/merge order.
        merged_name: File name for the collective PDF.
        export_folder: Target folder for the collective PDF (see resolve_export_folder).
        subfolder_name: Name of the subfolder that receives the individual pages.

    Returns:
        Path to the written collective PDF.

    Raises:
        ValueError: If fewer than 2 output paths are given.
    """
    if len(output_paths) < 2:
        raise ValueError("merge_ocr_outputs benötigt mindestens 2 Dateien")

    export_folder = Path(export_folder)
    export_folder.mkdir(parents=True, exist_ok=True)
    subfolder = export_folder / subfolder_name
    subfolder.mkdir(parents=True, exist_ok=True)

    merged = pikepdf.Pdf.new()
    opened_sources: list[pikepdf.Pdf] = []
    try:
        for p in output_paths:
            src_pdf = pikepdf.Pdf.open(p)
            opened_sources.append(src_pdf)
            merged.pages.extend(src_pdf.pages)
        merged_path = export_folder / merged_name
        merged.save(merged_path)
    finally:
        for src_pdf in opened_sources:
            try:
                src_pdf.close()
            except Exception:
                pass
        merged.close()

    # Einzelseiten erst NACH dem Speichern der Sammel-PDF verschieben, damit ein
    # Fehlschlag beim Merge keine Dateien verwaist zurücklässt.
    for p in output_paths:
        src_path = Path(p)
        if not src_path.exists():
            continue
        dest = subfolder / src_path.name
        if dest.exists():
            dest = subfolder / f"{src_path.stem}_{uuid.uuid4().hex[:8]}{src_path.suffix}"
        shutil.move(str(src_path), str(dest))

    return merged_path


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

    def _load_source_images(self, src_path: str) -> List[Image.Image]:
        """Loads the page images for a source file: PDF pages via Poppler, or the
        frame(s) of an image file directly (U1 -- multi-page TIFF yields one
        image per frame, JPG/PNG yield a single image).

        Args:
            src_path: Path to a PDF or image (JPG/PNG/TIFF) file.

        Returns:
            List of PIL images, one per page/frame.
        """
        ext = os.path.splitext(src_path)[1].lower()
        if ext not in IMAGE_EXTS:
            poppler_path = self.poppler_path or None
            return convert_from_path(src_path, dpi=300, poppler_path=poppler_path)

        images: List[Image.Image] = []
        with Image.open(src_path) as im:
            frame_count = getattr(im, "n_frames", 1)
            for i in range(frame_count):
                im.seek(i)
                images.append(im.copy())
        return images

    def _ocr_pdf(self, src_path: str, lang: str) -> bool:
        """Führt OCR auf einer PDF- oder Bilddatei aus (läuft im Worker-Thread)."""
        try:
            images: List[Image.Image] = self._load_source_images(src_path)

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
    """QListWidget with drag-and-drop support for PDF/image files and folders.

    Supports two drag-and-drop modes (U2/U5):
    - External drop (Explorer): files/folders are added to the list. A whole
      folder is tagged with a batch id so it can be auto-merged later (U5).
    - Internal drag (reordering rows): row order becomes the merge/page order
      used by "Markierte mergen" (U2 -- "Stapel-Reihenfolge = Seitenreihenfolge").
    """
    delete_requested = Signal()
    folder_dropped = Signal(str, str)  # batch_id, folder_path

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)
        self.setDragEnabled(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

    def dragEnterEvent(self, e):
        if e.source() is self or e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dragMoveEvent(self, e):
        if e.source() is self:
            super().dragMoveEvent(e)
        else:
            e.acceptProposedAction()

    def dropEvent(self, e):
        if e.source() is self and not e.mimeData().hasUrls():
            # Interne Umsortierung: neue Zeilenreihenfolge = Merge-/Stapelreihenfolge.
            super().dropEvent(e)
            return
        for url in e.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isdir(path):
                batch_id = str(uuid.uuid4())
                self.add_folder(path, batch_id=batch_id)
                self.folder_dropped.emit(batch_id, path)
            elif os.path.isfile(path):
                self.add_file(path)
        e.acceptProposedAction()

    def keyPressEvent(self, event):
        """Supports keyboard removal for selected files without changing the compact UI."""
        if event.key() == Qt.Key_Delete and self.selectedItems():
            self.delete_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def add_folder(self, folder, batch_id=None):
        """Adds all supported files from a folder to the list.

        Args:
            folder: Path to the directory to scan.
            batch_id: If set, tags all added items as belonging to this
                folder-drop batch (U5 automatic merge).
        """
        for fname in sorted(os.listdir(folder)):
            full = os.path.join(folder, fname)
            if os.path.isfile(full):
                self.add_file(full, batch_id=batch_id)

    def add_file(self, filepath, batch_id=None):
        """Adds a single file to the list if it has a supported extension and is not already listed.

        Args:
            filepath: Absolute path to the file to add.
            batch_id: If set, tags the item as belonging to a folder-drop batch (U5).
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
        item.setData(Qt.UserRole + 3, batch_id)
        self.addItem(item)


class OCRConverterGUI(QWidget):
    """Main application window for batch OCR processing of PDF files."""

    def __init__(self):
        super().__init__()
        # UI-Sprache aus persistenter Konfiguration laden, bevor Widgets gebaut werden.
        set_language(load_ui_language())
        self.setWindowTitle(tr("window_title"))
        self.resize(640, 520)

        app_icon = get_app_icon()
        if not app_icon.isNull():
            self.setWindowIcon(app_icon)

        self.layout = QVBoxLayout(self)
        self._ocr_worker = None  # Referenz auf laufenden QThread

        # UI-Sprachumschaltung (Welle-1 U1: sichtbarer DE/EN-Schalter, oben platziert)
        ui_lang_layout = QHBoxLayout()
        self.ui_lang_label = QLabel(tr("label_ui_lang"))
        self.ui_lang_combo = QComboBox()
        self.ui_lang_combo.addItem("Deutsch", "de")
        self.ui_lang_combo.addItem("English", "en")
        self.ui_lang_combo.setCurrentIndex(0 if get_language() == "de" else 1)
        self.ui_lang_combo.currentIndexChanged.connect(self._on_ui_language_changed)
        ui_lang_layout.addWidget(self.ui_lang_label)
        ui_lang_layout.addWidget(self.ui_lang_combo)
        ui_lang_layout.addStretch(1)
        self.layout.addLayout(ui_lang_layout)

        self.list_widget = PDFListWidget()
        self.list_widget.setAccessibleName(tr("a11y_file_list_name"))
        self.list_widget.setAccessibleDescription(tr("a11y_file_list_description"))
        self.list_widget.setToolTip(tr("a11y_file_list_description"))
        self.layout.addWidget(self.list_widget)

        # Exportordner-Einstellung (U4): konfigurierbar, Fallback = Quellordner (U3-Default)
        self.export_folder: str | None = load_export_folder()
        self._batch_folders: dict[str, str] = {}
        self._merged_batches: set[str] = set()

        export_layout = QHBoxLayout()
        self.export_folder_label = QLabel("")
        self.btn_choose_export_folder = QPushButton(tr("btn_export_folder"))
        self.btn_reset_export_folder = QPushButton(tr("btn_export_folder_reset"))
        export_layout.addWidget(self.export_folder_label, 1)
        export_layout.addWidget(self.btn_choose_export_folder)
        export_layout.addWidget(self.btn_reset_export_folder)
        self.layout.addLayout(export_layout)
        self._update_export_folder_label()

        # OCR-Spracheinstellung (Tesseract-Sprachpaket -- NICHT die UI-Sprache)
        lang_layout = QHBoxLayout()
        self.ocr_lang_label = QLabel(tr("label_ocr_lang"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["deu", "eng", "fra", "spa"])
        lang_layout.addWidget(self.ocr_lang_label)
        lang_layout.addWidget(self.lang_combo)
        self.layout.addLayout(lang_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add_file = QPushButton(tr("btn_add_file"))
        self.btn_start = QPushButton(tr("btn_start"))
        self.btn_export = QPushButton(tr("btn_export_job"))
        self.btn_refresh = QPushButton(f"{ICON_BROOM} {tr('btn_refresh')}")
        self.btn_delete = QPushButton(f"{ICON_TRASH} {tr('btn_delete')}")
        self.btn_delete.setToolTip(tr("tooltip_delete"))
        self.btn_delete.setAccessibleDescription(tr("a11y_delete_description"))
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
        self.list_widget.delete_requested.connect(self.on_delete)
        self.btn_choose_export_folder.clicked.connect(self.on_choose_export_folder)
        self.btn_reset_export_folder.clicked.connect(self.on_reset_export_folder)
        self.list_widget.customContextMenuRequested.connect(self._show_list_context_menu)
        self.list_widget.folder_dropped.connect(self._register_batch_folder)

        # Poppler-Pfad: leer = pdf2image nutzt System-Poppler
        self.poppler_path = ""

    def _on_ui_language_changed(self, index: int):
        """Wechselt die UI-Sprache, persistiert sie und stellt die Oberflaeche live um."""
        lang = self.ui_lang_combo.itemData(index) or "de"
        set_language(lang)
        save_ui_language(lang)
        self.retranslate_ui()

    def retranslate_ui(self):
        """Setzt alle sichtbaren, uebersetzten Texte in der aktuellen Sprache neu."""
        self.setWindowTitle(tr("window_title"))
        self.ui_lang_label.setText(tr("label_ui_lang"))
        self.ocr_lang_label.setText(tr("label_ocr_lang"))
        self.btn_add_file.setText(tr("btn_add_file"))
        self.btn_start.setText(tr("btn_start"))
        self.btn_export.setText(tr("btn_export_job"))
        self.btn_refresh.setText(f"{ICON_BROOM} {tr('btn_refresh')}")
        self.btn_delete.setText(f"{ICON_TRASH} {tr('btn_delete')}")
        self.btn_choose_export_folder.setText(tr("btn_export_folder"))
        self.btn_reset_export_folder.setText(tr("btn_export_folder_reset"))
        self._update_export_folder_label()

    def open_file_dialog(self):
        """Opens a file dialog to select PDF or image files and adds them to the list (U1)."""
        files, _ = QFileDialog.getOpenFileNames(
            self, tr("dialog_select_files"), "", tr("filter_pdf_images")
        )
        for f in files:
            self.list_widget.add_file(f)

    # ===== Exportordner-Einstellung (U4) =====

    def _update_export_folder_label(self):
        """Refreshes the label that shows the currently configured export folder."""
        folder_text = self.export_folder or tr("label_export_folder_default")
        self.export_folder_label.setText(tr("label_export_folder", folder=folder_text))

    def on_choose_export_folder(self):
        """Opens a folder dialog and persists the chosen export folder (U4)."""
        folder = QFileDialog.getExistingDirectory(
            self, tr("dialog_choose_export_folder"), self.export_folder or ""
        )
        if folder:
            self.export_folder = folder
            save_export_folder(folder)
            self._update_export_folder_label()

    def on_reset_export_folder(self):
        """Resets the export folder to the default (source folder per file, U3/U4)."""
        self.export_folder = None
        save_export_folder(None)
        self._update_export_folder_label()

    # ===== Merge/Stapeln (U2/U3/U5) =====

    def _show_list_context_menu(self, pos):
        """Shows the 'Markierte mergen' context menu for selected list entries (U2)."""
        if not self.list_widget.selectedItems():
            return
        menu = QMenu(self)
        merge_action = QAction(tr("action_merge_selected"), self)
        merge_action.triggered.connect(self.merge_selected)
        menu.addAction(merge_action)
        menu.exec(self.list_widget.mapToGlobal(pos))

    def _selected_done_items_in_list_order(self) -> list:
        """Returns the selected, already OCRed items in current list order.

        List order reflects the drag-reordered stack order (U2), independent
        of the order in which items were selected.
        """
        selected_paths = {it.data(Qt.UserRole) for it in self.list_widget.selectedItems()}
        return [
            self.list_widget.item(i)
            for i in range(self.list_widget.count())
            if self.list_widget.item(i).data(Qt.UserRole) in selected_paths
            and self.list_widget.item(i).data(Qt.UserRole + 1) == "done"
        ]

    def merge_selected(
        self, checked: bool = False, target_path: str | Path | None = None
    ) -> Path | None:
        """Merges the selected, already OCRed results into one collective PDF (U2/U3).

        Args:
            checked: Unused; matches the QAction/QPushButton `triggered`/`clicked` signature.
            target_path: If given, skips the save dialog (used by tests and by
                the auto-merge path is NOT routed through here, see
                `_auto_merge_completed_batches`).

        Returns:
            Path to the written collective PDF, or None if merging was aborted
            or not possible (fewer than 2 completed results selected).
        """
        del checked
        done_items = self._selected_done_items_in_list_order()
        if len(done_items) < 2:
            if target_path is None:
                QMessageBox.information(self, tr("info_export_title"), tr("info_merge_need_two"))
            return None

        output_paths = [
            os.path.splitext(it.data(Qt.UserRole))[0] + "_ocred.pdf" for it in done_items
        ]

        if target_path is None:
            first_source = done_items[0].data(Qt.UserRole)
            default_folder = resolve_export_folder(first_source, self.export_folder)
            chosen_path, _ = QFileDialog.getSaveFileName(
                self,
                tr("dialog_merge_save"),
                str(default_folder / "merged.pdf"),
                tr("filter_pdf"),
            )
            if not chosen_path:
                return None
            target_path = chosen_path

        target = Path(target_path)
        try:
            merged_path = merge_ocr_outputs(output_paths, target.name, target.parent)
        except Exception as e:
            QMessageBox.critical(self, tr("error_title"), tr("error_merge_failed", error=e))
            return None

        self.status_label.setText(tr("status_merge_saved", filename=merged_path.name))
        self.status_label.setStyleSheet("color: #0b6e4f; font-weight: bold;")
        return merged_path

    def _register_batch_folder(self, batch_id: str, folder_path: str):
        """Remembers which folder a folder-drop batch originated from (U5)."""
        self._batch_folders[batch_id] = folder_path

    def _auto_merge_completed_batches(self):
        """Automatically merges folder-drop batches once all their files are
        processed (U5): the whole dropped folder becomes one collective PDF
        plus a subfolder with the individual OCR results.
        """
        batch_items: dict[str, list] = {}
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            batch_id = item.data(Qt.UserRole + 3)
            if batch_id:
                batch_items.setdefault(batch_id, []).append(item)

        for batch_id, items in batch_items.items():
            if batch_id in self._merged_batches:
                continue
            if any(it.data(Qt.UserRole + 1) == "pending" for it in items):
                continue  # Batch noch nicht vollstaendig verarbeitet
            done_items = [it for it in items if it.data(Qt.UserRole + 1) == "done"]
            if len(done_items) < 2:
                continue
            folder = self._batch_folders.get(batch_id)
            if not folder:
                continue
            outputs = [
                os.path.splitext(it.data(Qt.UserRole))[0] + "_ocred.pdf" for it in done_items
            ]
            # U5-Default: Sammel-PDF landet IM abgelegten Ordner selbst (nicht dessen
            # Elternordner) -- resolve_export_folder ist fuer Datei-Pfade gedacht,
            # `folder` hier ist bereits der Zielordner.
            configured = Path(self.export_folder) if self.export_folder else None
            export_folder = configured if configured and configured.is_dir() else Path(folder)
            merged_name = f"{os.path.basename(os.path.normpath(folder))}_merged.pdf"
            try:
                merge_ocr_outputs(outputs, merged_name, export_folder)
                self._merged_batches.add(batch_id)
                self.status_label.setText(tr("status_merge_saved", filename=merged_name))
                self.status_label.setStyleSheet("color: #0b6e4f; font-weight: bold;")
            except Exception as e:
                logging.warning(f"Auto-Merge fuer Batch {batch_id} fehlgeschlagen: {e}")

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
        self._auto_merge_completed_batches()

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
    app_icon = get_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    gui = OCRConverterGUI()
    gui.show()
    sys.exit(app.exec())
