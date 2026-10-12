<img src="assets/banner.png" width="100%" alt="PDFtoPDFocr バナー">

[English](README.md) | [Deutsch](README_de.md) | [Español](README_es.md) | [中文](README_zh.md) | [日本語](README_ja.md) | [Русский](README_ru.md)

# PDFtoPDFocr — スキャン画像を検索可能な PDF に変換

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version 1.1.4](https://img.shields.io/badge/version-1.1.4-blue.svg)](pyproject.toml)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#voraussetzungen--plattformmatrix)

PDFtoPDFocr は、Tesseract OCR を使ってスキャン PDF や画像ファイルを検索可能な PDF に変換するデスクトップアプリです。複数ファイルの処理、OCR 言語の選択、元ファイルの保持に対応しています。

OCR と PDF の作成にはローカルツールを使います。選択した言語の Tesseract データファイルがない場合、アプリは GitHub からそのファイルをダウンロードできます。アプリはネットワークを遮断するファイアウォールやサンドボックスを提供しません。

> この簡潔な入口ページは、詳細版の旧 README [README_ja-archive-2026-10-12.md](README_ja-archive-2026-10-12.md) に置き換わりました。アーカイブ版は現在の主張を修正したガイドです。未変更の原文は[コミット 3cfce468](https://github.com/doc-bricks/PDFtoPDFocr/blob/3cfce468f20307bcbc158dd969c3ad304f34b4fe/README_ja.md)で確認できます。

機械可読コンテキスト: [`llms.txt`](llms.txt) · [セキュリティポリシー](SECURITY.md) · [サードパーティライセンス一覧](THIRD_PARTY_LICENSES.md)

## クイックナビゲーション

1. [画面の概要](#visual-showcase)
2. [アーキテクチャ](#systemarchitektur--komponenten-workflow)
3. [ローカルデータフロー](#lokaler-datenfluss--datenschutz-isolation)
4. [クイックスタート](#schnelleinstieg--kernabläufe)
5. [機能](#funktionen--features)
6. [利用例](#zielgruppen--auffindbarkeit)
7. [ツールの比較](#vergleichsmatrix--alternativen)
8. [アクセシビリティ](#barrierefreiheit--tastenkürzel)
9. [要件](#voraussetzungen--plattformmatrix)
10. [インストール](#installation--portables-setup)
11. [使い方](#nutzung--ausführungsrichtlinien)
12. [関連プロジェクト](#geschwister-tools--ökosystem)
13. [テスト](#tests--qualitätsprüfung)
14. [サードパーティライセンス](#drittanbieter-lizenzen--transparenz)
15. [プライバシーとセキュリティ](#datenschutz--sicherheitsmodell)
16. [デスクトップのパッケージ化](#exe--distributions-packaging)
17. [LLM コンテキスト](#maschinenlesbarer-llm-kontext)
18. [ライセンスと法的注記](#gesetzlicher-hinweis--lizenz)

<a id="visual-showcase"></a>
<a id="visuelle-showcase-galerie"></a>
## 画面の概要

スクリーンショットと詳しい画面操作の説明は[アーカイブ版ガイド](README_ja-archive-2026-10-12.md#visual-showcase)にあります。

<a id="system-architecture--component-workflow"></a>
<a id="systemarchitektur--komponenten-workflow"></a>
## アーキテクチャ

ユーザー → デスクトップアプリ → Poppler が PDF ページを画像化 → Tesseract がテキストを認識 → アプリが検索可能な PDF を作成します。選択された OCR 言語のデータがない場合、アプリは GitHub にリクエストできます。

<a id="four-view-architectural-topology-projection"></a>
<a id="vier-sichten-architektur-topologie-projektion"></a>
### アーキテクチャの詳細

コンポーネントと処理フローの詳細図は[アーカイブ版ガイド](README_ja-archive-2026-10-12.md#four-view-architectural-topology-projection)を参照してください。

<a id="local-data-flow--privacy-isolation"></a>
<a id="lokaler-datenfluss--datenschutz-isolation"></a>
## ローカルデータフロー

PDF の処理にはローカルツールを使います。ソースコードには、不足している Tesseract 言語データを取得する GitHub リクエストが含まれます。これはアプリの動作を説明するもので、システム全体のネットワーク制限を示すものではありません。セキュリティポリシーの範囲と連絡先は [`SECURITY.md`](SECURITY.md) にあります。

<a id="quick-start--key-operations"></a>
<a id="schnelleinstieg--kernabläufe"></a>
## クイックスタート

```bash
git clone https://github.com/doc-bricks/PDFtoPDFocr.git
cd PDFtoPDFocr
python -m venv .venv
```

使用するシェルに合わせて、次のうち **1 つだけ** を実行して環境を有効化します。

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows コマンドプロンプト:

```bat
.\.venv\Scripts\activate.bat
```

macOS または Linux:

```bash
source .venv/bin/activate
```

続けて依存パッケージをインストールし、アプリを起動します。

```bash
python -m pip install -r requirements.txt
python PDFtoPDFocr_2.py
```

このリポジトリから作成される Python wheel には配布メタデータのみが含まれ、デスクトップアプリはインストールされません。アプリの実行にはこのソースチェックアウトを使用してください。

Tesseract OCR と Poppler は別途インストールしてください。[要件](#voraussetzungen--plattformmatrix)を参照してください。Windows では [`START.bat`](START.bat) も使えます。

<a id="core-features"></a>
<a id="funktionen--features"></a>
## 機能

- スキャン PDF と画像をまとめて処理します。
- OCR 言語を選択できます。不足する Tesseract 言語データは GitHub から取得できます。
- 元ファイルを保持しながら検索可能な PDF を作成します。
- アプリからジョブマニフェストをエクスポートできます。

詳しい手順は[アーカイブ版の機能ガイド](README_ja-archive-2026-10-12.md#core-features)にあります。

<a id="target-personas--discoverability"></a>
<a id="zielgruppen--auffindbarkeit"></a>
## 利用例

スキャンや画像を検索可能な PDF に変換するデスクトップ作業を想定しています。法務、医療、コンプライアンスの認証を示すものではありません。

<a id="comparative-matrix--alternatives"></a>
<a id="vergleichsmatrix--alternativen"></a>
## ツールの比較

他製品との機能・コンプライアンス比較を検証済み情報として提供していません。各製品の最新ドキュメントと利用条件を確認してください。

<a id="accessibility--keyboard-shortcuts"></a>
<a id="barrierefreiheit--tastenkürzel"></a>
## アクセシビリティ

キーボードショートカットとアクセシビリティ用メタデータがあります。独立した WCAG 適合監査を受けたとは主張していません。詳しくは[画面に関するノート](README_ja-archive-2026-10-12.md#accessibility--keyboard-shortcuts)を参照してください。

<a id="requirements--platform-matrix"></a>
<a id="voraussetzungen--plattformmatrix"></a>
## 要件

ソースから実行するには Python 3.10 以降が必要です。Python パッケージの宣言済み最低バージョンは次のとおりです。

| パッケージ | 最低バージョン |
| --- | ---: |
| PySide6 | 6.5.0 |
| pytesseract | 0.3.13 |
| Pillow | 10.4.0 |
| pdf2image | 1.17.0 |
| pikepdf | 8.15.1 |
| requests | 2.33.1 |

同じ要件は [`requirements.txt`](requirements.txt) と [`pyproject.toml`](pyproject.toml) に記載されています。Tesseract OCR と Poppler も PATH 上に置くか、対応するローカルパスで設定してください。Windows は主なパッケージ化対象で、macOS と Linux はソースからの実行対象です。

<a id="installation--portable-setup"></a>
<a id="installation--portables-setup"></a>
## インストール

リポジトリをクローンし、アクティブな仮想環境に [`requirements.txt`](requirements.txt) の Python パッケージをインストールします。Tesseract と Poppler は別途導入します。選択した言語データがなければ、実行時に GitHub から取得できます。

<a id="usage--execution-guidelines"></a>
<a id="nutzung--ausführungsrichtlinien"></a>
## 使い方

1. [`python PDFtoPDFocr_2.py`] を実行します。Windows では [`START.bat`](START.bat) も使えます。
2. PDF または画像を追加し、OCR 言語を選択します。
3. OCR を開始し、生成された PDF を確認します。
4. 必要に応じてアプリからジョブマニフェストをエクスポートします。

<a id="tests--quality-verification"></a>
<a id="tests--qualitätsprüfung"></a>
## テスト

仮想環境を有効にしてから [`python -m pip install -r requirements-dev.txt`] を実行してください。このファイルには [`requirements.txt`](requirements.txt)、pytest、ruff が含まれます。テストは [`python -m pytest`] で実行します。翻訳の整合性は [`python manage_translations.py --check`] でも確認できます。

<a id="sibling-tools--ecosystem"></a>
<a id="geschwister-tools--ökosystem"></a>
## 関連プロジェクト

| プロジェクト | 関連する作業 |
| --- | --- |
| [DokuReader](https://github.com/doc-bricks/DokuReader) | ローカルの文書ライブラリと PDF の整理。 |
| [UniversalDocsGrabber](https://github.com/doc-bricks/UniversalDocsGrabber) | メール添付のダウンロードと Windows 上での文書整理。 |
| [UniversalInvoiceMail](https://github.com/doc-bricks/UniversalInvoiceMail) | 請求書の抽出と DATEV 形式を参考にした CSV エクスポート。 |

それぞれ独立したプロジェクトです。関連する用途を示すリンクであり、共通の実行環境やデータフローを意味しません。

<a id="third-party-licenses--transparency"></a>
<a id="drittanbieter-lizenzen--transparenz"></a>
## サードパーティライセンス

[`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) と [`THIRD_PARTY_LICENSES.txt`](THIRD_PARTY_LICENSES.txt) に、依存パッケージや同梱ツールのライセンス情報の一部を掲載しています。情報一覧であり、すべての配布形態や用途に対する適合認証ではありません。

<a id="privacy--security-model"></a>
<a id="datenschutz--sicherheitsmodell"></a>
## プライバシーとセキュリティ

アプリはローカルの OCR・PDF ツールを使います。ソースコードには不足する Tesseract 言語データを取得するリクエストも含まれます。ファイアウォール、サンドボックス、OS 権限境界は提供しません。データの流れは [`PRIVACY_POLICY.md`](PRIVACY_POLICY.md)、報告窓口と対応方針は [`SECURITY.md`](SECURITY.md) を確認してください。

<a id="exe--distribution-packaging"></a>
<a id="exe--distributions-packaging"></a>
## デスクトップのパッケージ化

Windows 向けのローカルビルドは [`python build_release.py --clean`] または [`build_exe.bat`](build_exe.bat) で準備できます。[`--clean`] は新しいビルド環境を作成して PyInstaller を実行する前に [`dist/`]、[`build/`]、[`.build_venv/`] を削除します。スクリプトは専用のビルド依存一覧を使います。成果物はローカルに作られ、リリースは公開されません。

<a id="machine-readable-llm-context"></a>
<a id="maschinenlesbarer-llm-kontext"></a>
## LLM コンテキスト

[`llms.txt`](llms.txt) はリポジトリのファイルと開発コマンドを示す、短い機械可読インデックスです。

<a id="statutory-notice--license"></a>
<a id="contributing--license"></a>
<a id="gesetzlicher-hinweis--lizenz"></a>
<a id="mitwirken--lizenz"></a>
## ライセンスと法的注記

プロジェクトは [MIT ライセンス](LICENSE)で提供されています。§ 521 BGB などの法規が適用されるかは、具体的な法律関係と適用法によります。この文書は一律の免責を定めるものではありません。
