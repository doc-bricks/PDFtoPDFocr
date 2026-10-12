<img src="assets/banner.png" width="100%" alt="Баннер PDFtoPDFocr">

[English](README.md) | [Deutsch](README_de.md) | [Español](README_es.md) | [中文](README_zh.md) | [日本語](README_ja.md) | [Русский](README_ru.md)

# PDFtoPDFocr — поиск по PDF со сканов и изображений

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Версия 1.1.4](https://img.shields.io/badge/version-1.1.4-blue.svg)](pyproject.toml)
[![Лицензия MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Платформы](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](#voraussetzungen--plattformmatrix)

PDFtoPDFocr — настольное приложение, которое с помощью Tesseract OCR преобразует сканированные PDF и изображения в PDF с поиском по тексту. Поддерживаются пакетная обработка, выбор языка OCR и сохранение исходных файлов.

Для OCR и сборки PDF используются локальные инструменты. Если файла данных Tesseract для выбранного языка нет, приложение может загрузить его с GitHub. Приложение не предоставляет сетевой экран или песочницу, блокирующую сетевой доступ.

> Эта краткая вводная заменяет прежний подробный README: [README_ru-archive-2026-10-12.md](README_ru-archive-2026-10-12.md). В архивной инструкции актуальные утверждения исправлены; исходный текст без изменений доступен в [коммите 3cfce468](https://github.com/doc-bricks/PDFtoPDFocr/blob/3cfce468f20307bcbc158dd969c3ad304f34b4fe/README_ru.md).

Контекст для машинной обработки: [`llms.txt`](llms.txt) · [Политика безопасности](SECURITY.md) · [Перечень лицензий сторонних компонентов](THIRD_PARTY_LICENSES.md)

## Быстрая навигация

1. [Обзор интерфейса](#visual-showcase)
2. [Архитектура](#systemarchitektur--komponenten-workflow)
3. [Локальный поток данных](#lokaler-datenfluss--datenschutz-isolation)
4. [Быстрый старт](#schnelleinstieg--kernabläufe)
5. [Функции](#funktionen--features)
6. [Сценарии использования](#zielgruppen--auffindbarkeit)
7. [Сравнение инструментов](#vergleichsmatrix--alternativen)
8. [Доступность](#barrierefreiheit--tastenkürzel)
9. [Требования](#voraussetzungen--plattformmatrix)
10. [Установка](#installation--portables-setup)
11. [Использование](#nutzung--ausführungsrichtlinien)
12. [Связанные проекты](#geschwister-tools--ökosystem)
13. [Тесты](#tests--qualitätsprüfung)
14. [Лицензии сторонних компонентов](#drittanbieter-lizenzen--transparenz)
15. [Конфиденциальность и безопасность](#datenschutz--sicherheitsmodell)
16. [Сборка настольного приложения](#exe--distributions-packaging)
17. [Контекст для LLM](#maschinenlesbarer-llm-kontext)
18. [Лицензия и правовое уведомление](#gesetzlicher-hinweis--lizenz)

<a id="visual-showcase"></a>
<a id="visuelle-showcase-galerie"></a>
## Обзор интерфейса

Снимки экрана и подробное описание интерфейса находятся в [архивной инструкции](README_ru-archive-2026-10-12.md#visual-showcase).

<a id="system-architecture--component-workflow"></a>
<a id="systemarchitektur--komponenten-workflow"></a>
## Архитектура

Пользователь → настольное приложение → Poppler преобразует страницы PDF в изображения → Tesseract распознаёт текст → приложение создаёт PDF с поиском. Если нет языковых данных для выбранного OCR-языка, приложение может запросить их у GitHub.

<a id="four-view-architectural-topology-projection"></a>
<a id="vier-sichten-architektur-topologie-projektion"></a>
### Подробности архитектуры

Подробные схемы компонентов и рабочих процессов находятся в [архивной инструкции](README_ru-archive-2026-10-12.md#four-view-architectural-topology-projection).

<a id="local-data-flow--privacy-isolation"></a>
<a id="lokaler-datenfluss--datenschutz-isolation"></a>
## Локальный поток данных

Для обработки PDF используются локальные инструменты. В исходном коде есть запрос к GitHub для получения недостающих языковых данных Tesseract. Это описание поведения приложения, а не системного ограничения сети. Область действия политики безопасности и контакты указаны в [`SECURITY.md`](SECURITY.md).

<a id="quick-start--key-operations"></a>
<a id="schnelleinstieg--kernabläufe"></a>
## Быстрый старт

```bash
git clone https://github.com/doc-bricks/PDFtoPDFocr.git
cd PDFtoPDFocr
python -m venv .venv
```

Активируйте среду ровно одной командой, подходящей для вашей оболочки:

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Командная строка Windows:

```bat
.\.venv\Scripts\activate.bat
```

macOS или Linux:

```bash
source .venv/bin/activate
```

Затем установите зависимости и запустите приложение:

```bash
python -m pip install -r requirements.txt
python PDFtoPDFocr_2.py
```

Python-wheel, собранный из этого репозитория, содержит только метаданные дистрибутива и не устанавливает настольное приложение. Для запуска приложения используйте этот исходный checkout.

Tesseract OCR и Poppler устанавливаются отдельно; см. [требования](#voraussetzungen--plattformmatrix). В Windows также доступен [`START.bat`](START.bat).

<a id="core-features"></a>
<a id="funktionen--features"></a>
## Функции

- Пакетная обработка сканированных PDF и изображений.
- Выбор языка OCR; недостающие данные Tesseract можно загрузить с GitHub.
- Создание PDF с доступным поиском при сохранении исходных файлов.
- Экспорт манифеста задания из приложения.

Подробный порядок работы описан в [архивной инструкции по функциям](README_ru-archive-2026-10-12.md#core-features).

<a id="target-personas--discoverability"></a>
<a id="zielgruppen--auffindbarkeit"></a>
## Сценарии использования

Приложение предназначено для настольных процессов преобразования сканов или изображений в PDF с поиском по тексту. Это не правовая, медицинская или нормативная сертификация.

<a id="comparative-matrix--alternatives"></a>
<a id="vergleichsmatrix--alternativen"></a>
## Сравнение инструментов

Мы не ведём проверенное сравнение функций или соответствия требованиям с другими продуктами. Оценивайте альтернативы по их актуальной документации и собственным требованиям.

<a id="accessibility--keyboard-shortcuts"></a>
<a id="barrierefreiheit--tastenkürzel"></a>
## Доступность

В приложении есть сочетания клавиш и метаданные доступности. Независимая проверка соответствия WCAG не заявляется. Подробности см. в [примечаниях об интерфейсе](README_ru-archive-2026-10-12.md#accessibility--keyboard-shortcuts).

<a id="requirements--platform-matrix"></a>
<a id="voraussetzungen--plattformmatrix"></a>
## Требования

Для запуска из исходного кода требуется Python 3.10 или новее. Заявленные минимальные версии пакетов Python:

| Пакет | Минимальная версия |
| --- | ---: |
| PySide6 | 6.5.0 |
| pytesseract | 0.3.13 |
| Pillow | 10.4.0 |
| pdf2image | 1.17.0 |
| pikepdf | 8.15.1 |
| requests | 2.33.1 |

Эти же требования перечислены в [`requirements.txt`](requirements.txt) и [`pyproject.toml`](pyproject.toml). Tesseract OCR и Poppler также должны находиться в PATH или быть указаны через поддерживаемые локальные пути. Windows — основная цель для пакетной сборки; на macOS и Linux приложение запускается из исходного кода.

<a id="installation--portable-setup"></a>
<a id="installation--portables-setup"></a>
## Установка

Клонируйте репозиторий и установите пакеты Python из [`requirements.txt`](requirements.txt) в активную виртуальную среду. Tesseract и Poppler устанавливаются отдельно. При отсутствии выбранных языковых данных приложение может загрузить их с GitHub во время работы.

<a id="usage--execution-guidelines"></a>
<a id="nutzung--ausführungsrichtlinien"></a>
## Использование

1. Запустите [`python PDFtoPDFocr_2.py`] или используйте [`START.bat`](START.bat) в Windows.
2. Добавьте PDF или изображения и выберите язык OCR.
3. Запустите OCR и проверьте полученный PDF.
4. При необходимости экспортируйте из приложения манифест задания.

<a id="tests--quality-verification"></a>
<a id="tests--qualitätsprüfung"></a>
## Тесты

При активной виртуальной среде установите зависимости для разработки командой [`python -m pip install -r requirements-dev.txt`]; этот файл включает [`requirements.txt`](requirements.txt), pytest и ruff. Запустите [`python -m pytest`]. Для проверки согласованности переводов также есть [`python manage_translations.py --check`].

<a id="sibling-tools--ecosystem"></a>
<a id="geschwister-tools--ökosystem"></a>
## Связанные проекты

| Проект | Смежная задача |
| --- | --- |
| [DokuReader](https://github.com/doc-bricks/DokuReader) | Локальная библиотека документов и организация PDF. |
| [UniversalDocsGrabber](https://github.com/doc-bricks/UniversalDocsGrabber) | Загрузка вложений электронной почты и организация документов в Windows. |
| [UniversalInvoiceMail](https://github.com/doc-bricks/UniversalInvoiceMail) | Извлечение данных счетов и экспорт CSV в стиле DATEV. |

Это самостоятельные проекты; ссылки показывают смежные задачи, а не общую среду выполнения или поток данных.

<a id="third-party-licenses--transparency"></a>
<a id="drittanbieter-lizenzen--transparenz"></a>
## Лицензии сторонних компонентов

В [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md) и [`THIRD_PARTY_LICENSES.txt`](THIRD_PARTY_LICENSES.txt) приведена выбранная информация о лицензиях зависимостей и включённых инструментов. Это справочный перечень, а не сертификат соответствия для каждого способа распространения или использования.

<a id="privacy--security-model"></a>
<a id="datenschutz--sicherheitsmodell"></a>
## Конфиденциальность и безопасность

Приложение использует локальные инструменты OCR и PDF; в исходном коде также есть запрос для получения недостающих языковых данных Tesseract. Приложение не предоставляет брандмауэр, песочницу или границу системных привилегий. Потоки данных описаны в [`PRIVACY_POLICY.md`](PRIVACY_POLICY.md), а политика ответа и контакты сопровождающих — в [`SECURITY.md`](SECURITY.md).

<a id="exe--distribution-packaging"></a>
<a id="exe--distributions-packaging"></a>
## Сборка настольного приложения

Локальную сборку для Windows можно подготовить командой [`python build_release.py --clean`] или с помощью [`build_exe.bat`](build_exe.bat). Параметр [`--clean`] удаляет [`dist/`], [`build/`] и [`.build_venv/`], затем создаёт новую среду сборки и запускает PyInstaller. Скрипт использует отдельный список зависимостей сборки. Артефакты создаются локально; публикация релиза не выполняется.

<a id="machine-readable-llm-context"></a>
<a id="maschinenlesbarer-llm-kontext"></a>
## Контекст для LLM

[`llms.txt`](llms.txt) — краткий машиночитаемый индекс файлов репозитория и команд разработки.

<a id="statutory-notice--license"></a>
<a id="contributing--license"></a>
<a id="gesetzlicher-hinweis--lizenz"></a>
<a id="mitwirken--lizenz"></a>
## Лицензия и правовое уведомление

Проект предоставляется по [лицензии MIT](LICENSE). Применимость таких норм, как § 521 BGB, зависит от конкретных правоотношений и применимого законодательства; эта документация не устанавливает общего освобождения от ответственности.
