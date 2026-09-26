---
name: 1cli-tools
description: >-
  Use before writing a helper script or choosing a CLI for data, YAML, text
  edits, lint, security, media or browser work; before npm install/ci, global
  tsc, agent-browser, vercel, gh agent-task/skill, uv tool or ffmpeg; and when
  an install succeeds but a package fails. Lists what is installed on this Mac
  and capabilities newer than model memory. Markdown corpus search belongs to
  1md-search.
---

# CLI На Этом Mac

Память модели не знает, что установлено на этом Mac, и старее установленных
версий. Готовый инструмент дешевле своего скрипта; знакомое имя не означает
знакомые возможности.

## Что Уже Установлено

Перечень сверен 2026-09-26. Перед использованием — `command -v TOOL`.

| Работа | Инструменты |
|---|---|
| данные: JSONL, CSV, JSON, история сессий | `duckdb` — SQL прямо по файлам и glob, `jq`, `gron` |
| YAML, frontmatter Markdown | `yq --front-matter=extract` |
| поиск и замена в тексте | `rg`, `fd`, `sd` — без различий BSD/GNU `sed` |
| структура кода | `ast-grep` — поиск и переписывание по AST |
| Markdown | `md` (md-tools), `rumdl`, `markdownlint-cli2`, `mdq`, `lychee` — ссылки |
| JS/TS | `biome`, `eslint`, `prettier`, `stylelint`, `tsc` 7, `vitest` 5, `knip`, `dependency-cruiser`, `publint`, `attw`, `syncpack` |
| Python | `ruff`, `pyright`, `mypy`, `pytest`, `coverage`, `vulture`, `deptry`, `xenon` |
| shell и CI | `shellcheck`, `shfmt`, `actionlint`, `pre-commit`, `just`, `gtimeout` (coreutils) — `timeout` в macOS нет |
| безопасность | `semgrep`, `gitleaks`, `trufflehog`, `trivy`, `osv-scanner`, `bandit`, `pip-audit` |
| браузер и UI | `agent-browser`, `playwright`, `impeccable detect` — анти-паттерны UI |
| медиа и документы | `ffmpeg`, `whisper-cli`, `fpcalc`, `pdftotext`, `soffice` |
| сервисы | `gh`, `vercel`, `supabase`, `firecrawl`, `ntn` — Notion |
| модели и агенты | `claude`, `hermes`, `droid`, Codex — `/Applications/ChatGPT.app/Contents/Resources/codex` |
| токены и скилы | `token-counter`, `qv-skill` — проверка пакета скила |

Нужного нет — сравни установку через `brew`, `npm -g` или `uv tool` со своим
кодом.

## Тихие Ловушки

- Успешный `npm install` не доказывает, что install-скрипты зависимостей
  выполнены: npm 12 блокирует их по умолчанию → [npm 12](references/npm-12.md).
- `brew upgrade node` может откатить глобальный npm до комплектного →
  [обновление](references/runtime-update.md).
- Оболочка инструмента Bash здесь — zsh: `$VAR` с несколькими аргументами не
  делится на слова, `=слово` без кавычек раскрывается как путь команды, а
  `for f in $(…)` рвёт пути с пробелами — используй `-z | xargs -0`.
- Абзац Markdown часто одна строка: `cut -c` молча прячет её конец, а
  `rg -M 300 --max-columns-preview` помечает обрезанное.
- `npx --no-install lychee` добавляет строки `npm notice`, и `tail -1` может
  вернуть пустую строку — вызывай `lychee` напрямую.

## Открой Один Reference В Текущий Момент

| Момент решения | Получить |
|---|---|
| выбрать workflow в `agent-browser` | [version-matched bundled skills](references/agent-browser-skills.md) |
| выбрать browser evidence/diagnostic | [встроенные diagnostics](references/agent-browser-diagnostics.md) |
| искать структуру или переписывать AST | [`ast-grep` 0.45](references/ast-grep.md) |
| npm install пропустил lifecycle script | [npm 12 allowScripts](references/npm-12.md) |
| проверить vulnerabilities изолированного Python CLI | [`uv tool audit`](references/uv-tool-audit.md) |
| пересобрать environment Python CLI | [`uv tool install --reinstall`](references/uv-tool-rebuild.md) |
| запустить глобальный TypeScript 7 | [новые compiler defaults](references/typescript-7.md) |
| работать с большим Markdown corpus | [локальный md-tools](references/markdown-knowledge.md) |
| работать с GitHub agent session | [`gh agent-task`](references/github-agent-task.md) |
| искать/обновлять GitHub agent skill | [`gh skill`](references/github-skills.md) |
| выбрать Vercel agent/platform route | [новые команды Vercel 60](references/vercel-agent-platform.md) |
| выбрать codec в локальном FFmpeg | [возможности active build](references/ffmpeg-build.md) |
| обновить конфликтующие active CLI | [owner и совместный smoke](references/runtime-update.md) |

## Вернись В Задачу

1. Сверь active version с live-help командой из reference; при drift live help
   побеждает. Project-local owner/config сильнее global.
2. Используй capability, если она меняет ход задачи. Discovery не разрешает
   mutation или network.
3. Верни `TOOL VERSION · capability → changed action` либо `no relevant delta`.
