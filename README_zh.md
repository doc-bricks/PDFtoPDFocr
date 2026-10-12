<img src="assets/banner.png" width="100%" alt="PDFtoPDFocr 横幅">

[English](README.md) | [Deutsch](README_de.md) | [Español](README_es.md) | [中文](README_zh.md) | [日本語](README_ja.md) | [Русский](README_ru.md)

# PDFtoPDFocr — 将扫描件和图像转换为可搜索的 PDF

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![版本 1.1.4](https://img.shields.io/badge/version-1.1.4-blue.svg)](pyproject.toml)
[![MIT 许可证](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![平台](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#voraussetzungen--plattformmatrix)

PDFtoPDFocr 是一款桌面应用，使用 Tesseract OCR 将扫描的 PDF 和图像文件转换为可搜索的 PDF。它支持批量输入、选择 OCR 语言，并保留源文件。

OCR 和 PDF 组装使用本地工具。如果缺少所选语言对应的 Tesseract 数据文件，应用可以从 GitHub 下载该文件。应用不提供阻断网络的防火墙或沙箱。

> 本简明入口页取代了原先的详细 README：[README-archive-2026-10-12.md](README-archive-2026-10-12.md)。归档指南已修正当前声明；未经修改的源文件可在[提交 3cfce468](https://github.com/doc-bricks/PDFtoPDFocr/blob/3cfce468f20307bcbc158dd969c3ad304f34b4fe/README_zh.md)查看。

机器可读上下文：[`llms.txt`](llms.txt) · [安全策略](SECURITY.md) · [第三方许可证清单](THIRD_PARTY_LICENSES.md)

## 快速导航

1. [界面概览](#visual-showcase)
2. [架构](#systemarchitektur--komponenten-workflow)
3. [本地数据流](#lokaler-datenfluss--datenschutz-isolation)
4. [快速开始](#schnelleinstieg--kernabläufe)
5. [功能](#funktionen--features)
6. [使用场景](#zielgruppen--auffindbarkeit)
7. [工具比较](#vergleichsmatrix--alternativen)
8. [无障碍支持](#barrierefreiheit--tastenkürzel)
9. [要求](#voraussetzungen--plattformmatrix)
10. [安装](#installation--portables-setup)
11. [使用方法](#nutzung--ausführungsrichtlinien)
12. [相关项目](#geschwister-tools--ökosystem)
13. [测试](#tests--qualitätsprüfung)
14. [第三方许可证](#drittanbieter-lizenzen--transparenz)
15. [隐私与安全](#datenschutz--sicherheitsmodell)
16. [桌面打包](#exe--distributions-packaging)
17. [LLM 上下文](#maschinenlesbarer-llm-kontext)
18. [许可证与法律说明](#gesetzlicher-hinweis--lizenz)

<a id="visual-showcase"></a>
<a id="visuelle-showcase-galerie"></a>
## 界面概览

截图和详细的界面说明见[归档指南](README_zh-archive-2026-10-12.md#visual-showcase)。

<a id="system-architecture--component-workflow"></a>
<a id="systemarchitektur--komponenten-workflow"></a>
## 架构

主要流程：用户 → 桌面应用 → Poppler 将 PDF 页面转换为图像 → Tesseract 识别文本 → 应用生成可搜索的 PDF。若缺少所选 OCR 语言数据，应用可以向 GitHub 请求该文件。

<a id="four-view-architectural-topology-projection"></a>
<a id="vier-sichten-architektur-topologie-projektion"></a>
### 架构详情

组件和工作流的详细视图见[归档指南](README_zh-archive-2026-10-12.md#four-view-architectural-topology-projection)。

<a id="local-data-flow--privacy-isolation"></a>
<a id="lokaler-datenfluss--datenschutz-isolation"></a>
## 本地数据流

PDF 处理使用本地工具。源代码包含从 GitHub 获取缺失 Tesseract 语言数据的请求。这描述的是应用行为，并不构成系统级网络限制。安全策略的适用范围和联系方式见 [`SECURITY.md`](SECURITY.md)。

<a id="quick-start--key-operations"></a>
<a id="schnelleinstieg--kernabläufe"></a>
## 快速开始

```bash
git clone https://github.com/doc-bricks/PDFtoPDFocr.git
cd PDFtoPDFocr
python -m venv .venv
```

请根据所用终端，**只选择并执行一条**激活命令：

PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows 命令提示符：

```bat
.\.venv\Scripts\activate.bat
```

macOS 或 Linux：

```bash
source .venv/bin/activate
```

然后安装依赖并启动应用：

```bash
python -m pip install -r requirements.txt
python PDFtoPDFocr_2.py
```

从此仓库构建的 Python wheel 只包含发行版元数据，不会安装桌面应用。请使用此源代码检出版本运行应用。

Tesseract OCR 和 Poppler 需要单独安装，详见[要求](#voraussetzungen--plattformmatrix)。Windows 还可以使用 [`START.bat`](START.bat)。

<a id="core-features"></a>
<a id="funktionen--features"></a>
## 功能

- 批量处理扫描的 PDF 和图像。
- 选择 OCR 语言；缺失的 Tesseract 语言数据可以从 GitHub 下载。
- 创建可搜索的 PDF，同时保留源文件。
- 从应用导出任务清单。

详细操作步骤见[归档功能指南](README_zh-archive-2026-10-12.md#core-features)。

<a id="target-personas--discoverability"></a>
<a id="zielgruppen--auffindbarkeit"></a>
## 使用场景

本应用面向将扫描件或图像转换为可搜索 PDF 的桌面工作流程。它不代表法律、医疗或合规认证。

<a id="comparative-matrix--alternatives"></a>
<a id="vergleichsmatrix--alternativen"></a>
## 工具比较

我们没有维护经过验证的其他产品功能或合规比较。请根据其最新文档和自己的要求评估替代方案。

<a id="accessibility--keyboard-shortcuts"></a>
<a id="barrierefreiheit--tastenkürzel"></a>
## 无障碍支持

应用包含键盘快捷键和无障碍元数据。我们不声称已通过独立的 WCAG 符合性审计。详见[界面说明](README_zh-archive-2026-10-12.md#accessibility--keyboard-shortcuts)。

<a id="requirements--platform-matrix"></a>
<a id="voraussetzungen--plattformmatrix"></a>
## 要求

从源代码运行需要 Python 3.10 或更高版本。声明的 Python 软件包最低版本如下：

| 软件包 | 最低版本 |
| --- | ---: |
| PySide6 | 6.5.0 |
| pytesseract | 0.3.13 |
| Pillow | 10.4.0 |
| pdf2image | 1.17.0 |
| pikepdf | 8.15.1 |
| requests | 2.33.1 |

相同要求列在 [`requirements.txt`](requirements.txt) 和 [`pyproject.toml`](pyproject.toml) 中。Tesseract OCR 和 Poppler 也必须位于 PATH 中，或通过受支持的本地路径配置。Windows 是主要的打包目标；macOS 和 Linux 适用于从源代码运行。

<a id="installation--portable-setup"></a>
<a id="installation--portables-setup"></a>
## 安装

克隆仓库，并在已激活的虚拟环境中安装 [`requirements.txt`](requirements.txt) 列出的 Python 软件包。Tesseract 和 Poppler 需单独安装。运行时若缺少所选语言数据，应用可以从 GitHub 下载。

<a id="usage--execution-guidelines"></a>
<a id="nutzung--ausführungsrichtlinien"></a>
## 使用方法

1. 运行 [`python PDFtoPDFocr_2.py`]；Windows 也可使用 [`START.bat`](START.bat)。
2. 添加 PDF 或图像文件并选择 OCR 语言。
3. 启动 OCR 并检查生成的 PDF。
4. 需要时从应用导出任务清单。

<a id="tests--quality-verification"></a>
<a id="tests--qualitätsprüfung"></a>
## 测试

激活虚拟环境后，运行 [`python -m pip install -r requirements-dev.txt`] 安装开发依赖；该文件包含 [`requirements.txt`](requirements.txt)、pytest 和 ruff。使用 [`python -m pytest`] 运行测试。还可用 [`python manage_translations.py --check`] 检查翻译一致性。

<a id="sibling-tools--ecosystem"></a>
<a id="geschwister-tools--ökosystem"></a>
## 相关项目

| 项目 | 相邻用途 |
| --- | --- |
| [DokuReader](https://github.com/doc-bricks/DokuReader) | 本地文档库和 PDF 整理。 |
| [UniversalDocsGrabber](https://github.com/doc-bricks/UniversalDocsGrabber) | 下载电子邮件附件并在 Windows 上整理文档。 |
| [UniversalInvoiceMail](https://github.com/doc-bricks/UniversalInvoiceMail) | 发票提取与 DATEV 风格 CSV 导出。 |

这些是相互独立的项目；链接说明相邻用途，不表示共用运行环境或数据流。

<a id="third-party-licenses--transparency"></a>
<a id="drittanbieter-lizenzen--transparenz"></a>
## 第三方许可证

[`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) 和 [`THIRD_PARTY_LICENSES.txt`](THIRD_PARTY_LICENSES.txt) 列出部分依赖项和捆绑工具的许可证信息。这是信息清单，不是针对所有分发方式或用途的合规认证。

<a id="privacy--security-model"></a>
<a id="datenschutz--sicherheitsmodell"></a>
## 隐私与安全

应用使用本地 OCR 和 PDF 工具；其源代码也包含获取缺失 Tesseract 语言数据的请求。应用不提供防火墙、沙箱或操作系统权限隔离边界。数据流详情见 [`PRIVACY_POLICY.md`](PRIVACY_POLICY.md)，维护者的响应政策和报告联系方式见 [`SECURITY.md`](SECURITY.md)。

<a id="exe--distribution-packaging"></a>
<a id="exe--distributions-packaging"></a>
## 桌面打包

可以使用 [`python build_release.py --clean`] 或 [`build_exe.bat`](build_exe.bat) 准备本地 Windows 构建。[`--clean`] 会先删除 [`dist/`]、[`build/`] 和 [`.build_venv/`]，然后创建新的构建环境并运行 PyInstaller。该脚本使用单独的构建依赖列表。产物只在本地生成，不会发布版本。

<a id="machine-readable-llm-context"></a>
<a id="maschinenlesbarer-llm-kontext"></a>
## LLM 上下文

[`llms.txt`](llms.txt) 是仓库文件和开发命令的简短机器可读索引。

<a id="statutory-notice--license"></a>
<a id="contributing--license"></a>
<a id="gesetzlicher-hinweis--lizenz"></a>
<a id="mitwirken--lizenz"></a>
## 许可证与法律说明

本项目依据 [MIT 许可证](LICENSE)提供。§ 521 BGB 等法定规则是否适用，取决于具体法律关系和适用法律；本文档不作一概免责。
