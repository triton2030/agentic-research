---
name: 1cli-tools
description: >-
  Use before writing a helper script or choosing a CLI for data, YAML, text
  edits, lint, security, media, browser, disk-space or system-health work;
  before npm install/ci, global
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

Перечень сверен 2026-09-26; Graphify — 2026-10-02; PostgreSQL, `caffeinate`
и трасса Playwright — 2026-10-10; диск и здоровье системы — 2026-10-18.
Перед использованием — `command -v TOOL`.

| Работа | Инструменты |
|---|---|
| данные: JSONL, CSV, JSON, история сессий | `duckdb` — SQL прямо по файлам и glob, `jq`, `gron` |
| PostgreSQL 17 | `psql`, `pgbench` — нагрузка базы, `pg_dump` и `pg_restore` — копия и восстановление |
| YAML, frontmatter Markdown | `yq --front-matter=extract` |
| поиск и замена в тексте | `rg`, `fd`, `sd` — без различий BSD/GNU `sed` |
| структура кода | `ast-grep` — поиск и переписывание по AST |
| связи кода и последствия изменений | `graphify` 0.9.73 — локальный граф кода; `query` — поиск связей, `affected` — затронутые узлы |
| Markdown | `md` (md-tools), `rumdl`, `markdownlint-cli2`, `mdq`, `lychee` — ссылки |
| JS/TS | `biome`, `eslint`, `prettier`, `stylelint`, `tsc` 7, `vitest` 5, `knip`, `dependency-cruiser`, `publint`, `attw`, `syncpack` |
| Python | `ruff`, `pyright`, `mypy`, `pytest`, `coverage`, `vulture`, `deptry`, `xenon` |
| shell и CI | `shellcheck`, `shfmt`, `actionlint`, `pre-commit`, `just`, `gtimeout` (coreutils) — `timeout` в macOS нет; `caffeinate -d -i <команда>` — Mac не уснёт и не заблокирует экран, пока идёт долгий прогон |
| безопасность | `semgrep`, `gitleaks`, `trufflehog`, `trivy`, `osv-scanner`, `bandit`, `pip-audit` |
| браузер и UI | `agent-browser`, `playwright`; нестабильный браузерный прогон — трасса Playwright при сбое: `tracing.start` и `stopChunk`, разбор — `playwright show-trace` |
| медиа и документы | `ffmpeg`, `whisper-cli`, `fpcalc`, `pdftotext`, `soffice` |
| диск: что занимает место | `ncdu` 2.9 — `ncdu -o- -x <папка>` выдаёт дерево размеров JSON-ом; `duf --json` — свободное место томов; `mo analyze` (Mole) — интерактивно |
| здоровье системы | `mo status --json` (Mole 1.61) — снимок: память и своп, топ процессов, температуры, размер Корзины; `btop` — интерактивный монитор; Stats — монитор владельца в строке меню |
| чистка Mac | Mole: `mo installer`, `mo clean`, `mo purge` — сборки проектов, `mo uninstall` — приложение с остатками; все интерактивные, первый запуск — `--dry-run` |
| сервисы | `gh`, `vercel`, `supabase`, `firecrawl`, `ntn` — Notion |
| модели и агенты | `claude`, `hermes`, `droid`, Codex — `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex` |
| токены и скилы | `token-counter`, `qv-skill` — проверка пакета скила |

Нужного нет — сравни установку через `brew`, `npm -g` или `uv tool` со своим
кодом.

## Тихие Ловушки

- Успешный `npm install` не доказывает, что install-скрипты зависимостей
  выполнены: npm 12 блокирует их по умолчанию → [npm 12](references/npm-12.md).
- `brew upgrade node` может откатить глобальный npm до комплектного →
  [обновление](references/runtime-update.md).
- Оболочка инструмента Bash здесь — bash 5, а не zsh: `setopt` и модификаторы
  вроде `${f:t}` молча не работают, а глоб без совпадений остаётся строкой.
  Проверка совпадения — `compgen -G '<шаблон>'`; пути с пробелами —
  `-z | xargs -0`. Перед массовым `mv` или `rm` по условию выведи список.
- `gdu` здесь — GNU `du` из coreutils, а не анализатор диска gdu; анализ места —
  `ncdu`.
- `mo clean`, `mo purge` и `mo installer` удаляют навсегда, мимо Корзины.
  Кеши `~/.npm/_npx` и `~/.cache/uv` — место запуска MCP-серверов плагинов:
  до их чистки проверь `pgrep -fl 'npx|uvx'`.
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
