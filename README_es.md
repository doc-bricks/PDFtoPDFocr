<img src="assets/banner.png" width="100%" alt="Banner de PDFtoPDFocr">

[English](README.md) | [Deutsch](README_de.md) | [Español](README_es.md) | [中文](README_zh.md) | [日本語](README_ja.md) | [Русский](README_ru.md)

# PDFtoPDFocr — PDFs con texto buscable a partir de escaneos e imágenes

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Versión 1.1.4](https://img.shields.io/badge/version-1.1.4-blue.svg)](pyproject.toml)
[![Licencia MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Plataformas](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#voraussetzungen--plattformmatrix)

PDFtoPDFocr es una aplicación de escritorio que convierte PDF escaneados e imágenes en PDF con texto buscable mediante Tesseract OCR. Admite lotes, selección del idioma OCR y conserva los archivos de origen.

El OCR y la creación de PDF utilizan herramientas locales. Si falta el archivo de datos de Tesseract para el idioma elegido, la aplicación puede descargarlo desde GitHub. La aplicación no ofrece un cortafuegos ni una sandbox que bloquee la red.

> Esta entrada concisa sustituye al README detallado anterior: [README-archive-2026-10-12.md](README-archive-2026-10-12.md). La guía archivada tiene sus afirmaciones actuales corregidas; la fuente original está disponible en el [commit 3cfce468](https://github.com/doc-bricks/PDFtoPDFocr/blob/3cfce468f20307bcbc158dd969c3ad304f34b4fe/README_es.md).

Contexto legible por máquinas: [`llms.txt`](llms.txt) · [Política de seguridad](SECURITY.md) · [Inventario de licencias de terceros](THIRD_PARTY_LICENSES.md)

## Navegación rápida

1. [Galería visual](#visual-showcase)
2. [Arquitectura](#systemarchitektur--komponenten-workflow)
3. [Flujo de datos local](#lokaler-datenfluss--datenschutz-isolation)
4. [Inicio rápido](#schnelleinstieg--kernabläufe)
5. [Funciones](#funktionen--features)
6. [Casos de uso](#zielgruppen--auffindbarkeit)
7. [Comparación de herramientas](#vergleichsmatrix--alternativen)
8. [Accesibilidad](#barrierefreiheit--tastenkürzel)
9. [Requisitos](#voraussetzungen--plattformmatrix)
10. [Instalación](#installation--portables-setup)
11. [Uso](#nutzung--ausführungsrichtlinien)
12. [Proyectos relacionados](#geschwister-tools--ökosystem)
13. [Pruebas](#tests--qualitätsprüfung)
14. [Licencias de terceros](#drittanbieter-lizenzen--transparenz)
15. [Privacidad y seguridad](#datenschutz--sicherheitsmodell)
16. [Empaquetado de escritorio](#exe--distributions-packaging)
17. [Contexto para LLM](#maschinenlesbarer-llm-kontext)
18. [Licencia y nota legal](#gesetzlicher-hinweis--lizenz)

<a id="visual-showcase"></a>
<a id="visuelle-showcase-galerie"></a>
## Galería visual

Las capturas y el recorrido detallado por la interfaz están en la [guía archivada](README_es-archive-2026-10-12.md#visual-showcase).

<a id="system-architecture--component-workflow"></a>
<a id="systemarchitektur--komponenten-workflow"></a>
## Arquitectura

Usuario → aplicación de escritorio → Poppler convierte páginas PDF en imágenes → Tesseract reconoce el texto → la aplicación crea un PDF buscable. Si faltan datos del idioma OCR elegido, la aplicación puede solicitarlos a GitHub.

<a id="four-view-architectural-topology-projection"></a>
<a id="vier-sichten-architektur-topologie-projektion"></a>
### Detalles de arquitectura

Las vistas detalladas de componentes y flujos están en la [guía archivada](README_es-archive-2026-10-12.md#four-view-architectural-topology-projection).

<a id="local-data-flow--privacy-isolation"></a>
<a id="lokaler-datenfluss--datenschutz-isolation"></a>
## Flujo de datos local

El procesamiento de PDF usa herramientas locales. El código fuente incluye una solicitud a GitHub para obtener datos de idioma de Tesseract que falten. Esto describe el comportamiento de la aplicación; no implica una restricción de red para todo el sistema. El alcance y el contacto de seguridad figuran en [`SECURITY.md`](SECURITY.md).

<a id="quick-start--key-operations"></a>
<a id="schnelleinstieg--kernabläufe"></a>
## Inicio rápido

```bash
git clone https://github.com/doc-bricks/PDFtoPDFocr.git
cd PDFtoPDFocr
python -m venv .venv
```

Activa el entorno con exactamente un comando, según tu terminal:

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Símbolo del sistema:

```bat
.\.venv\Scripts\activate.bat
```

macOS o Linux:

```bash
source .venv/bin/activate
```

Después instala los requisitos e inicia la aplicación:

```bash
python -m pip install -r requirements.txt
python PDFtoPDFocr_2.py
```

La rueda de Python construida desde este repositorio contiene solo metadatos de distribución; no instala la aplicación de escritorio. Usa este checkout del código fuente para ejecutar la aplicación.

Instala Tesseract OCR y Poppler por separado; consulta los [requisitos](#voraussetzungen--plattformmatrix). En Windows también está disponible [`START.bat`](START.bat).

<a id="core-features"></a>
<a id="funktionen--features"></a>
## Funciones

- Procesa en lotes PDF escaneados e imágenes.
- Permite elegir el idioma OCR; los datos que falten pueden descargarse desde GitHub.
- Crea PDF con texto buscable y conserva intactos los archivos de origen.
- Exporta un manifiesto de trabajo desde la aplicación.

La [guía archivada de funciones](README_es-archive-2026-10-12.md#core-features) contiene el recorrido detallado.

<a id="target-personas--discoverability"></a>
<a id="zielgruppen--auffindbarkeit"></a>
## Casos de uso

La aplicación está pensada para flujos de escritorio que convierten escaneos o imágenes en PDF con texto buscable. No es una certificación legal, médica ni de cumplimiento normativo.

<a id="comparative-matrix--alternatives"></a>
<a id="vergleichsmatrix--alternativen"></a>
## Comparación de herramientas

No mantenemos una comparación verificada de funciones o cumplimiento con otros productos. Evalúa las alternativas según su documentación actual y tus propios requisitos.

<a id="accessibility--keyboard-shortcuts"></a>
<a id="barrierefreiheit--tastenkürzel"></a>
## Accesibilidad

La aplicación incluye atajos de teclado y metadatos de accesibilidad. No se afirma que exista una auditoría independiente de conformidad WCAG. Consulta las [notas detalladas de interfaz](README_es-archive-2026-10-12.md#accessibility--keyboard-shortcuts).

<a id="requirements--platform-matrix"></a>
<a id="voraussetzungen--plattformmatrix"></a>
## Requisitos

Para ejecutar el código fuente se necesita Python 3.10 o posterior. Las versiones mínimas declaradas para los paquetes Python son:

| Paquete | Versión mínima |
| --- | ---: |
| PySide6 | 6.5.0 |
| pytesseract | 0.3.13 |
| Pillow | 10.4.0 |
| pdf2image | 1.17.0 |
| pikepdf | 8.15.1 |
| requests | 2.33.1 |

Los mismos requisitos aparecen en [`requirements.txt`](requirements.txt) y [`pyproject.toml`](pyproject.toml). Tesseract OCR y Poppler también deben estar en PATH o configurarse mediante las rutas locales admitidas. Windows es el principal destino empaquetado; macOS y Linux son destinos para ejecutar desde el código fuente.

<a id="installation--portable-setup"></a>
<a id="installation--portables-setup"></a>
## Instalación

Clona el repositorio e instala en el entorno virtual activo los paquetes Python de [`requirements.txt`](requirements.txt). Tesseract y Poppler se instalan por separado. Si faltan datos del idioma seleccionado, la aplicación puede descargarlos desde GitHub durante la ejecución.

<a id="usage--execution-guidelines"></a>
<a id="nutzung--ausführungsrichtlinien"></a>
## Uso

1. Inicia [`python PDFtoPDFocr_2.py`] o usa [`START.bat`](START.bat) en Windows.
2. Añade PDF o imágenes y elige el idioma OCR.
3. Inicia el OCR y revisa el PDF resultante.
4. Si lo necesitas, exporta el manifiesto de trabajo desde la aplicación.

<a id="tests--quality-verification"></a>
<a id="tests--qualitätsprüfung"></a>
## Pruebas

Con el entorno virtual activo, instala las dependencias de desarrollo con [`python -m pip install -r requirements-dev.txt`]; este archivo incluye [`requirements.txt`](requirements.txt), pytest y ruff. Ejecuta [`python -m pytest`]. También se ofrece [`python manage_translations.py --check`] para comprobar la coherencia de las traducciones.

<a id="sibling-tools--ecosystem"></a>
<a id="geschwister-tools--ökosystem"></a>
## Proyectos relacionados

| Proyecto | Tarea relacionada |
| --- | --- |
| [DokuReader](https://github.com/doc-bricks/DokuReader) | Biblioteca local de documentos y organización de PDF. |
| [UniversalDocsGrabber](https://github.com/doc-bricks/UniversalDocsGrabber) | Descarga de adjuntos de correo y organización de documentos en Windows. |
| [UniversalInvoiceMail](https://github.com/doc-bricks/UniversalInvoiceMail) | Extracción de facturas y exportación CSV de estilo DATEV. |

Son proyectos independientes; los enlaces describen tareas relacionadas, no una ejecución conjunta ni un flujo de datos compartido.

<a id="third-party-licenses--transparency"></a>
<a id="drittanbieter-lizenzen--transparenz"></a>
## Licencias de terceros

[`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) y [`THIRD_PARTY_LICENSES.txt`](THIRD_PARTY_LICENSES.txt) recogen información seleccionada sobre licencias de dependencias y herramientas incluidas. Es un inventario informativo, no una certificación de cumplimiento para cada distribución o uso.

<a id="privacy--security-model"></a>
<a id="datenschutz--sicherheitsmodell"></a>
## Privacidad y seguridad

La aplicación usa herramientas locales de OCR y PDF; el código fuente también contiene una solicitud para obtener datos de idioma de Tesseract que falten. No proporciona cortafuegos, sandbox ni una frontera de privilegios del sistema operativo. Consulta [`PRIVACY_POLICY.md`](PRIVACY_POLICY.md) para conocer los flujos de datos y [`SECURITY.md`](SECURITY.md) para la política de respuesta y los contactos.

<a id="exe--distribution-packaging"></a>
<a id="exe--distributions-packaging"></a>
## Empaquetado de escritorio

Se puede preparar una compilación local para Windows con [`python build_release.py --clean`] o [`build_exe.bat`](build_exe.bat). La opción [`--clean`] elimina [`dist/`], [`build/`] y [`.build_venv/`] antes de crear un entorno de compilación nuevo y ejecutar PyInstaller. El script usa su propia lista de dependencias de compilación. Crea artefactos locales y no publica una versión.

<a id="machine-readable-llm-context"></a>
<a id="maschinenlesbarer-llm-kontext"></a>
## Contexto para LLM

[`llms.txt`](llms.txt) es un índice breve y legible por máquinas de los archivos del repositorio y los comandos de desarrollo.

<a id="statutory-notice--license"></a>
<a id="contributing--license"></a>
<a id="gesetzlicher-hinweis--lizenz"></a>
<a id="mitwirken--lizenz"></a>
## Licencia y nota legal

El proyecto se ofrece bajo la [licencia MIT](LICENSE). La aplicación de normas legales como el § 521 BGB depende de la relación jurídica concreta y de la legislación aplicable; esta documentación no concede una exención general de responsabilidad.
