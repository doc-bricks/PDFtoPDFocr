# Third-Party Licenses & Software Inventory

**Project:** `PDFtoPDFocr`  
**Organization:** [doc-bricks](https://github.com/doc-bricks)  
**Umbrella Ecosystem:** [open-bricks](https://github.com/open-bricks)  
**Author / Maintainer:** doc-bricks Team / Lukas Geiger (`lukas@open-bricks.org`)  
**Audit Date:** 2026-09-26
**License Compliance Status:** VERIFIED (100% Permissive / OSI-Approved & Copyleft Boundary Isolated)  
**SBOM Level:** Level 1 Software Bill of Materials (Direct, Transitive & Bundled Binaries)

---

## 1. Executive Summary

`PDFtoPDFocr` is a local-first, privacy-respecting Windows desktop application (with Linux/macOS support from source) that converts scanned PDFs and images into searchable PDFs with embedded full-text layers using Tesseract OCR and Poppler.

All third-party runtime libraries, engines, and development dependencies have been audited for licensing compliance:
- **Zero AGPL / SSPL Contamination:** No dependencies utilize network copyleft or restrictive commercial dual-licensing.
- **Dynamic Linking LGPL-3.0 Compliance:** `PySide6` (Qt for Python) is dynamically linked in accordance with Section 4 of the LGPLv3; user-replaceable shared libraries are supported.
- **Strict Subprocess Boundary for External Tools:** External engines (`Poppler` utilities like `pdftoppm` and `pdfinfo`) are invoked exclusively via isolated operating system subprocesses with bounded arguments and sanitization, preserving strict process boundaries without linking GPL code into the application codebase (`INV-ISOLATION-04`).
- **Permissive Core Runtime:** `pytesseract` (Apache-2.0), `Pillow` (HPND permissive), `pdf2image` (MIT), `pikepdf` (MPL-2.0), and `requests` (Apache-2.0) are fully compatible with the primary **MIT License**.

---

## 2. Production Runtime Dependencies

The following direct dependencies are specified in `pyproject.toml` and `requirements.txt`:

| Package | Minimum Floor | License | Author / Organization | Purpose & Usage |
|---------|---------------|---------|-----------------------|-----------------|
| `PySide6` | `>=6.5.0` | LGPL-3.0 / GPL-3.0 | The Qt Company Ltd. | Modern desktop GUI framework, Qt event loop, drag-and-drop file queues, and widgets |
| `pytesseract` | `>=0.3.13` | Apache-2.0 | Google Inc., Matthias Lee | Lightweight Python wrapper for calling the local Tesseract OCR engine |
| `Pillow` | `>=10.4.0` | HPND (Permissive) | Jeffrey A. Clark & contributors | Image decoding, bitmap transformations, and multi-frame TIFF parsing |
| `pdf2image` | `>=1.17.0` | MIT | Edouard Belval | Python module wrapping Poppler utilities for rasterizing PDF pages into memory bitmaps |
| `pikepdf` | `>=8.15.1` | MPL-2.0 | James R. Barlow & contributors | Python C++ bindings for QPDF; handles PDF page manipulation, merging, and metadata assembly |
| `requests` | `>=2.33.1` | Apache-2.0 | Kenneth Reitz & contributors | Controlled HTTP client used strictly for downloading missing official Tesseract language packs on user demand |

---

## 3. Transitive Runtime Dependencies

| Package | License | Dependency Origin | Notes & Permissive Status |
|---------|---------|-------------------|---------------------------|
| `urllib3` | MIT | `requests` | HTTP connection pool and transport layer |
| `certifi` | MPL-2.0 | `requests` | Curated Mozilla root CA certificate bundle |
| `charset-normalizer` | MIT | `requests` | Character encoding detector |
| `idna` | BSD-3-Clause | `requests` | Internationalized Domain Names in Applications (RFC 5891) |
| `packaging` | Apache-2.0 / BSD-2-Clause | `pikepdf`, `pytesseract` | Core utilities for Python package version parsing and metadata |
| `QPDF` (bundled C++) | Apache-2.0 | `pikepdf` | Structural PDF transformation engine; permissive Apache-2.0 license |

---

## 4. Bundled Binaries & External Engine Tools

When distributed in standalone portable form or installed locally, the following third-party engine executables may be bundled or discovered:

| Component | License | Bundled Location | Process Isolation & Boundary |
|-----------|---------|------------------|------------------------------|
| **Tesseract OCR Engine** | Apache-2.0 | `tesseract_portable/` | Invoked as an external CLI subprocess (`tesseract.exe`). Full license at `tesseract_portable/doc/LICENSE`. |
| **Leptonica** | Permissive (zlib-like) | `tesseract_portable/` (`libleptonica-*.dll`) | Image processing foundation library for Tesseract OCR. Free commercial and non-commercial reuse. |
| **Poppler Utilities** | GPL-2.0 or later | `poppler/` (`pdftoppm.exe`, `pdfinfo.exe`) | Invoked strictly via CLI subprocess by `pdf2image`. Not linked into application memory space; source code available from freedesktop.org. |

---

## 5. Development, Linting & Test Dependencies

Development, static analysis, linting, packaging, and contract test suites use the following tools:

| Tool | Minimum Version | License | Purpose / Registry |
|------|-----------------|---------|--------------------|
| `pytest` | `>=9.1.1` | MIT | Test runner for 120+ unit, regression, accessibility, and metadata contract tests |
| `ruff` | `>=0.1.0` | MIT / Apache-2.0 | High-performance Python linter and code formatting validation |
| `setuptools` | `>=61.0` | MIT | PEP 517 / PEP 518 standard build backend |
| `PyInstaller` | `>=6.0.0` | GPL-2.0 with exception | Standalone Windows desktop executable packager (runtime exception allows MIT licensing) |

---

## 6. Governance & Compliance Invariants

`PDFtoPDFocr` enforces ten verifiable governance, privacy, and runtime safety invariants:

| Identifier | Invariant Name | Architectural Guarantee |
|------------|----------------|-------------------------|
| **INV-LOCAL-01** | **100% Local-First & Zero-Egress** | All PDF rasterization, image processing, OCR recognition, and PDF assembly execute 100% locally on-device. No document contents or telemetry are uploaded. |
| **INV-UNPRIV-02** | **Unprivileged RunAsInvoker Non-Elevation** | Runs strictly in standard user mode with standard OS permissions; administrative elevation or root rights are never requested or required. |
| **INV-NONDEST-03** | **Non-Destructive Original File Safety** | Source PDF and image files are strictly preserved and never modified or overwritten; OCR outputs default to `<original>_ocred.pdf` or custom destination folders. |
| **INV-ISOLATION-04** | **Process & Subprocess Boundary Isolation** | External engine utilities (Tesseract, Poppler) run in isolated OS subprocesses with bounded arguments, maintaining clean process boundaries. |
| **INV-BOUNDED-05** | **Bounded Worker Thread Concurrency** | Batch conversions run asynchronously on dedicated background worker threads with cancellation safety and non-blocking GUI responsiveness. |
| **INV-PORTABLE-06** | **Zero-Global-Install Portability** | Portable Tesseract (`tesseract_portable/`) and Poppler (`poppler/`) installations are auto-discovered without requiring global system PATH mutations or registry edits. |
| **INV-MANIFEST-07** | **Portable Job Manifest Integrity** | Job export (`pdftopdfocr-job-v1.json`) produces deterministic execution records and metadata without embedding raw binary document bytes or Base64 payloads. |
| **INV-A11Y-08** | **Accessible Ergonomics & WCAG Conformance** | 100% of UI controls have accessible screen-reader names, localized tooltips, high-contrast indicators, and full keyboard navigation. |
| **INV-FAILCLOSED-09** | **Fail-Closed Batch Error Recovery** | Corrupted PDF pages or missing language models log clean error states and skip problematic frames gracefully without crashing the batch queue. |
| **INV-SLA-10** | **48h Security Response & 5-Day Triage SLA** | Committed vulnerability triage within 5 business days and initial response within 48 hours via [SECURITY.md](SECURITY.md) and security@open-bricks.org. |

---

## 7. Invariant Cross-Reference & Verification Matrix

| Invariant | Code Implementation & Enforcement | Verification Test File | Status |
|---|---|---|:---:|
| `INV-LOCAL-01` | `PDFtoPDFocr_2.py` (Local pipeline, zero outbound telemetry) | `tests/test_security_license_contract.py` | VERIFIED |
| `INV-UNPRIV-02` | `PDFtoPDFocr.spec` (`as_invoker` execution level in PE manifest) | `tests/test_platform_package_gate.py` | VERIFIED |
| `INV-NONDEST-03` | `PDFtoPDFocr_2.py` (Appends `_ocred.pdf`, verifies target separation) | `tests/test_bug_regressions.py` | VERIFIED |
| `INV-ISOLATION-04` | Subprocess invocations via `pytesseract` & `pdf2image` | `tests/test_tesseract_config.py` | VERIFIED |
| `INV-BOUNDED-05` | `OCRThread` (QThread worker with cancellation flag) | `tests/test_bug_regressions.py` | VERIFIED |
| `INV-PORTABLE-06` | Relative path resolution for `tesseract_portable/` & `poppler/` | `tests/test_tesseract_config.py` | VERIFIED |
| `INV-MANIFEST-07` | `PDFtoPDFocr_2.py` (`export_job_manifest`) | `tests/test_export_format.py` | VERIFIED |
| `INV-A11Y-08` | `setAccessibleName`, `setAccessibleDescription`, keyboard hotkeys | `tests/test_ui_accessibility.py` | VERIFIED |
| `INV-FAILCLOSED-09` | Exception traps per page/document with error badge update | `tests/test_bug_regressions.py` | VERIFIED |
| `INV-SLA-10` | Formal response SLA policy in `SECURITY.md` | `tests/test_metadata.py` | VERIFIED |

---

## 8. Unprivileged RunAsInvoker Non-Elevation Certification

`PDFtoPDFocr` is explicitly designed and certified for unprivileged desktop operation:
- **No Administrator Rights:** The application never requests `requireAdministrator` or `highestAvailable` elevation privileges.
- **Windows UAC Manifest:** The build configuration (`PDFtoPDFocr.spec` and `store_package.json`) enforces standard user execution level (`asInvoker`).
- **File System Sandboxing:** Temporary files are written strictly to user-scoped directories (`%TEMP%` or application-local portable cache) without mutating system folders (`C:\Windows`, `C:\Program Files`).
- **Registry Non-Pollution:** No global registry keys or system-level services are installed.

---

## 9. Subprocess Boundary & Copyleft Isolation Guarantee

External tools licensed under copyleft regimes (specifically Poppler under GPL-2.0 or later) are strictly decoupled:
- **No Shared Memory or Dynamic Linking:** The Python application does not link against Poppler C++ shared libraries (`.dll` / `.so`).
- **Process-Level Isolation:** `pdf2image` invokes `pdftoppm.exe` or `pdfinfo.exe` as independent OS subprocesses via standard pipes.
- **LGPL Compliance for Qt:** `PySide6` is dynamically linked according to LGPL-3.0 Section 4, ensuring users retain the right and ability to replace the underlying Qt shared libraries.

---

## 10. Contact & Security Inquiries

For questions regarding third-party licensing, compliance auditing, or vulnerability disclosures, contact:
- **Security Team:** `security@open-bricks.org` / `security@ellmos.ai`
- **Lead Maintainer:** Lukas Geiger (`lukas@open-bricks.org` / `support@lukasgeiger.com`)
