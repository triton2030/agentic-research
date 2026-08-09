---
description: "Проверенная карта локальных инструментов и моментов их выбора."
---

# Local Tool Map

Снимок от 2026-08-09. Проверять active command или app перед первым применением.
Открывать только раздел текущей задачи; не запускать весь каталог.

## Markdown

- `md` — ориентирование, поиск, sections, graph и impact в большом corpus.
- `mdq` — выбор известных структурных элементов Markdown.
- `rg` + `fd` — точный текст, путь и файловый scope.
- `rumdl` или `markdownlint-cli2` — lint по существующему project config.
- `lychee` — ссылки; live URL validation использует network.

## Код и зависимости

- `ast-grep` — syntax-aware search и controlled rewrite.
- `graphify` — cross-file graph, paths и affected nodes.
- `depcruise` — JS/TS dependency rules и reachability.
- `knip` — unused JS/TS files, exports и dependencies.
- `rg` + compiler/tests — минимальная связка для точного локального изменения.

## Проверки

- JS/TS — `biome`, `eslint`, `tsc`, `vitest`, `prettier`.
- Python — `ruff`, `pyright`, `mypy`, `pytest`, `coverage`.
- Python cleanup — `deptry`, `vulture`, `xenon`.
- Shell/CI — `shellcheck`, `shfmt`, `actionlint`.
- Packages — `attw`, `publint`, `syncpack`.
- Всегда предпочитать checker, уже настроенный проектом.

## UI И Браузер

- `impeccable detect` — UI anti-patterns в файлах или rendered URL.
- `agent-browser` — интерактивная проверка, screenshots, traces и visual diff.
- `playwright` — повторяемые browser tests.
- Figma, Linearity, Open Design и Pencil установлены, но требуют доступного
  UI-control.
- Blender доступен как приложение и headless executable.

## Медиа И Документы

- `ffmpeg` / `ffprobe` — видео, аудио, кадры, overlay и conversion.
- `cwebp` / `dwebp` — WebP conversion.
- Poppler — PDF metadata, text extraction и page rendering.
- LibreOffice — офисные документы и headless conversion.

## Данные, Автоматизация И Delivery

- `jq` / `gron` — JSON inspection и преобразование представления.
- `sqlite3` — локальные SQLite datasets.
- `token-counter` — оценка размера текстового context.
- `just` / `pre-commit` — project recipes и configured checks.
- `gh`, `vercel`, `supabase` — repository, deployment и backend operations.

## Security

- `gitleaks` / `trufflehog` — secret candidates.
- `semgrep` / `bandit` — source analysis.
- `osv-scanner` / `pip-audit` — dependency vulnerabilities.
- `trivy` — filesystem, image, secret и misconfiguration scanning.
