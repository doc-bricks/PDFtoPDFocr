# Selected Third-Party License Information

**Project:** `PDFtoPDFocr`  
**Organization:** [doc-bricks](https://github.com/doc-bricks)  
**Umbrella Ecosystem:** [open-bricks](https://github.com/open-bricks)
**Author / Maintainer:** doc-bricks Team / Lukas Geiger (`lukas@open-bricks.org`)
**Inventory snapshot:** 2026-10-01; scope note updated 2026-10-12
**Scope:** Selected license information recorded for declared dependencies and external tools; not a complete SBOM, legal review, or compliance certification.
**Attribution & Notice:** See `NOTICE` file in repository root
**Plain-Text Companion:** See `THIRD_PARTY_LICENSES.txt` in repository root

---

## 1. Executive Summary

`PDFtoPDFocr` is a desktop application that uses Tesseract OCR and Poppler to create searchable PDFs from scanned PDFs and images. The application source can request missing Tesseract language data from GitHub.

This page records selected license labels and component information from the project files. Dependency versions are not pinned to a single resolved environment, bundled files can vary by build, and this page does not establish license compatibility for every use or distribution. Process boundaries describe how tools are launched; they do not create a security sandbox or determine legal obligations. Check the exact notices and license terms for the versions and artifacts being distributed.

---

## 2. Production Runtime Dependencies

The following direct dependencies are specified in `pyproject.toml` and `requirements.txt`:

| Package | Minimum Floor | License | Author / Organization | Purpose & Usage |
|---------|---------------|---------|-----------------------|-----------------|
| `PySide6` | `>=6.5.0` | Observed in the 6.8.3 package metadata: `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; the metadata also names `LicenseRef-Qt-Commercial` | The Qt Company Ltd. | Modern desktop GUI framework, Qt event loop, drag-and-drop file queues, and widgets |
| `pytesseract` | `>=0.3.13` | Apache-2.0 | Google Inc., Matthias Lee | Lightweight Python wrapper for calling the local Tesseract OCR engine |
| `Pillow` | `>=10.4.0` | HPND (Permissive) | Jeffrey A. Clark & contributors | Image decoding, bitmap transformations, and multi-frame TIFF parsing |
| `pdf2image` | `>=1.17.0` | MIT | Edouard Belval | Python module wrapping Poppler utilities for rasterizing PDF pages into memory bitmaps |
| `pikepdf` | `>=8.15.1` | MPL-2.0 | James R. Barlow & contributors | Python C++ bindings for QPDF; handles PDF page manipulation, merging, and metadata assembly |
| `requests` | `>=2.33.1` | Apache-2.0 | Kenneth Reitz & contributors | Controlled HTTP client used strictly for downloading missing official Tesseract language packs on user demand |

---

## 3. Reported Transitive Runtime Dependencies

| Package | Recorded License | Dependency Origin | Role |
|---------|---------|-------------------|---------------------------|
| `urllib3` | MIT | `requests` | HTTP connection pool and transport layer |
| `certifi` | MPL-2.0 | `requests` | Curated Mozilla root CA certificate bundle |
| `charset-normalizer` | MIT | `requests` | Character encoding detector |
| `idna` | BSD-3-Clause | `requests` | Internationalized Domain Names in Applications (RFC 5891) |
| `packaging` | Apache-2.0 / BSD-2-Clause | `pikepdf`, `pytesseract` | Core utilities for Python package version parsing and metadata |
| `QPDF` (bundled C++) | Apache-2.0 | `pikepdf` | Structural PDF transformation engine; permissive Apache-2.0 license |

---

## 4. External Engine Tools

When distributed in standalone portable form or installed locally, the following third-party engine executables may be bundled or discovered:

| Component | Recorded License | Possible bundled location | Application use |
|-----------|---------|------------------|------------------------------|
| **Tesseract OCR Engine** | Apache-2.0 | `tesseract_portable/` when included in a build | Launched through the OCR wrapper. See the license file shipped with the exact engine distribution. |
| **Leptonica** | See bundled distribution | `tesseract_portable/` when included in a build | Image-processing library used by Tesseract; consult the notices shipped with the exact files. |
| **Poppler Utilities** | GPL-2.0 or later | `poppler/` when included in a build | `pdf2image` launches Poppler utilities such as `pdftoppm` and `pdfinfo`; process launch does not determine distribution obligations. |

---

## 5. Development, Linting & Test Dependencies

Development, static analysis, linting, packaging, and contract test suites use the following tools:

| Tool | Minimum Version | License | Purpose / Registry |
|------|-----------------|---------|--------------------|
| `pytest` | `>=9.1.1` | MIT | Test runner; the configured suite changes over time |
| `ruff` | `>=0.9.0` | MIT / Apache-2.0 | Python linter used by project checks |
| `setuptools` | `>=61.0` | MIT | PEP 517 / PEP 518 standard build backend |
| `PyInstaller` | `>=6.0.0` | Observed in 6.22.3 metadata: `GPL-2.0-or-later WITH Bootloader-exception` | Standalone Windows desktop executable packager; the exception text covers compiled bootloader and related files, not the application bundle as a whole |

The PySide6 license field records package metadata observed on 2026-10-12 for PySide6, PySide6_Essentials, PySide6_Addons, and shiboken6 version 6.8.3. It does not identify the terms for every version allowed by the `>=6.5.0` floor or every Qt module in a release build. Qt documents commercial and open-source licensing options, notes that some modules use GPL terms, and recommends checking the components used by an application. See [Qt Licensing](https://doc.qt.io/qt-6/licensing.html) and [Licenses Used in Qt for Python](https://doc.qt.io/qtforpython-6/licenses.html), then inspect notices for the exact distributed files.

---

## 6. Scope and distribution notes

- The project source declares direct Python dependencies in `pyproject.toml`; `requirements.txt` also lists application dependencies. The actual installed versions depend on the environment.
- Some release builds can include external binaries. The files included in a specific archive should be checked against that archive's notices and license files.
- The application launches Tesseract and Poppler through external-tool interfaces. This implementation fact is not a sandbox, privilege boundary, or legal conclusion about a distribution.
- PyInstaller 6.22.3 declares GPLv2-or-later with a special exception. Its `COPYING.txt` describes permission to link or embed compiled bootloader and related files; GPL terms still apply in other respects. Review PyInstaller runtime hooks, modules, and every bundled dependency separately.
- The project license is MIT. Third-party components retain their own license terms; this page does not give a blanket conclusion about combinations, modifications, or redistribution.

## 7. Contact & Security Inquiries

For questions regarding third-party licensing, compliance auditing, or vulnerability disclosures, contact:
- **Security Team:** `security@open-bricks.org` / `security@ellmos.ai`
- **Lead Maintainer:** Lukas Geiger (`lukas@open-bricks.org` / `support@lukasgeiger.com`)
