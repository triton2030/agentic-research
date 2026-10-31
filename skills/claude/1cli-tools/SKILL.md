---
name: 1cli-tools
description: >-
  Use before writing a helper script or choosing a CLI for data, YAML, text
  edits, lint, security, media, browser, disk-space or system-health work;
  before npm or pnpm install/ci, running .ts with node, global tsc,
  agent-browser, vercel, gh, uv tool or ffmpeg; and when an install succeeds
  but a package fails. Lists what is installed on this Mac and where familiar
  commands silently break. Markdown corpus search belongs to 1md-search.
---

# CLI На Этом Mac

Твоя память не знает, что здесь установлено, и старее этих версий. Здесь —
только то, чего не скажет `--help`: что есть, где привычное тихо ломается
и что появилось после твоей памяти. Точный синтаксис — живой `--help`; он
побеждает этот текст. Сверено 2026-10-31; перед использованием —
`TOOL --version`: `command -v` не видит сломанную обёртку.

## Что Есть

| Работа | Инструменты |
|---|---|
| данные: JSONL, CSV, JSON, SQLite, история сессий | `duckdb` — SQL прямо по файлам и glob, `jq`, `gron`, `sqlite3` |
| PostgreSQL 17 | `psql`, `pgbench`, `pg_dump`, `pg_restore` |
| YAML, frontmatter | `yq --front-matter=extract` |
| текст | `rg`, `fd`, `sd` — без различий BSD/GNU `sed` |
| код | `ast-grep` — поиск и переписывание по AST, `ast-grep outline` — символы файла; `graphify` — локальный граф кода: `query`, `affected` |
| Markdown | `md` (md-tools, свой: `orient`, `search`, `edit-context`, `impact` по корпусу; `md tools --json`), `rumdl`, `markdownlint-cli2`, `mdq`, `lychee` |
| JS/TS | `pnpm`, `bun` — `bun file.ts` выполняет TS с `enum` и `namespace`, на которых `node file.ts` падает; `bun check` — типы без сборки; `biome`, `eslint`, `prettier`, `stylelint`, `tsc` 7, `vitest`, `knip`, `dependency-cruiser`, `publint`, `attw`, `syncpack`, `changeset`, `redocly` |
| Python | `ruff`, `pyright`, `mypy`, `pytest`, `coverage`, `vulture`, `deptry`, `xenon` |
| shell и CI | `shellcheck`, `shfmt`, `actionlint`, `pre-commit`, `just`, `timeout`; `caffeinate -d -i <команда>` — Mac не уснёт, пока идёт прогон |
| терминал и git | `tmux`, `watch`, `tree`, `direnv exec <папка> <команда>`, `git-lfs` |
| безопасность | `semgrep`, `gitleaks`, `trufflehog`, `trivy`, `osv-scanner`, `bandit`, `pip-audit` |
| браузер | `agent-browser` — `read <url>` отдаёт страницу Markdown-ом, сам ищет `llms.txt`; `skills list` — инструкции под эту версию; `a11y`, `vitals`, `react`, `diff`; `playwright` — при нестабильном прогоне трасса и `playwright show-trace` |
| медиа и документы | `ffmpeg` (VideoToolbox, SVT-AV1, VMAF), `fpcalc`, `pdftotext`, `soffice` |
| речь в текст | `whisper-cli` — всегда `-m ~/.cache/whisper.cpp/ggml-large-v3-turbo-q5_0.bin -l <язык>`, иначе ищет несуществующую модель и слушает по-английски; VAD — `--vad -vm ~/.cache/whisper.cpp/ggml-silero-v6.2.0.bin` |
| фото | `cwebp`, `dwebp`; numpy, Pillow, pillow-heif, OpenCV, scipy, scikit-image — в user site Python 3.15: видны с `python3 -P`, не с `-I`; `swiftc -O` с macOS Vision — OCR и вырезание (интерпретатор `swift` не успевает); ImageMagick нет |
| диск и система | `ncdu -o- -x <папка>` — дерево размеров JSON; `duf --json`; `mo status --json` (Mole) — память, процессы, температуры; `mo analyze`, `mo uninstall` — приложение с остатками; `btop` |
| сервисы | `gh`, `vercel`, `supabase`, `firecrawl`, `ntn` — Notion, `rclone` — Google Drive (`gdrive`, `gdrive-ro`) по скилу `1google-drive-archive` |
| агенты | `claude`, `droid`, `agy` — Google Antigravity, `muse` — Muse Code; `codex` из PATH — npm; `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex` — отдельный движок, обновляется с приложением, его запускает мост Claude `experiments/codex-bridge` в мастерской agentic-research |
| скилы и токены | `qv-skill` — проверка пакета скила; `token-counter` |

## Тихие Ловушки

- **PATH.** Старые `/usr/local/bin/node` 22, npm 10 и Vercel 39 лежат рядом
  с active в `/opt/homebrew`; первым стоит `~/.local/bin/node` — отдельный
  бинарь nodejs.org: Homebrew его не обновляет, кто поставил — не записано,
  без владельца не меняй. Проверяй
  `which -a` и `realpath`. Проектный pin (`engines`, `.nvmrc`) сильнее
  глобального и сам runtime не переключает.
- **Локальные сборки.** `md-tools` (uv editable), `qv-skill`, `plugin-eval`
  не заменяй одноимёнными пакетами из registry. `graphify` закреплён `==0.9.73`
  в receipt `uv tool`: подсказку uv обновить его без владельца не выполняй.
- **Скрипты зависимостей.** npm 12 и pnpm 11+ блокируют install-скрипты
  зависимостей, а install завершается успехом. npm:
  `npm approve-scripts --allow-scripts-pending` покажет заблокированное
  (пусто — причина другая), подробности — `npm help approve-scripts`.
  pnpm: `pnpm ignored-builds`, затем `pnpm approve-builds PKG` (без аргумента
  интерактивен, `--all` снимает защиту целиком).
- **pnpm 11+.** Настройки — в `pnpm-workspace.yaml`: поле `pnpm`
  в `package.json` и не-auth ключи `.npmrc` молча игнорируются; пакет моложе
  суток не ставится → [релиз 11](https://github.com/pnpm/pnpm/releases/tag/v11.0.0).
- **`brew upgrade node`** может вернуть комплектный npm поверх нового: после
  него проверь `npm --version` и поставь свежий npm обратно.
- **Конфликт версий.** Если две active версии конфликтуют, pin
  проекта не требует старую и менеджеры предлагают обновить обе — обнови обе
  одним проходом, затем повтори обе `--version` и упавшую команду; так решил
  владелец.
- **`uv tool`.** Окружение на Python из Homebrew ломается со сменой его
  minor-версии (`environment not found`). `uv tool install NAME --reinstall`
  забывает прежние `--with`: возьми их из `~/.local/share/uv/tools/NAME/uv-receipt.toml`.
  `uv tool audit` без lockfile падает; без переустановки окружение проверяет
  `pip-audit --path <site-packages окружения>`.
- **DuckDB 2.0** в сессии агента печатает Markdown: результат больше 1000 строк
  или 10 тыс. байт — только первые и последние строки, ячейка — до 500 знаков,
  ошибки — JSON в stderr. Все данные — `-csv` или `-json`; подробности —
  `duckdb -c '.help agent'`. `~` и `!~` теперь ищут частичное
  совпадение — старые запросы молча меняют результат →
  [миграция](https://duckdb.org/docs/2.0/operations_manual/migration.html).
- **Глобальный `tsc` 7** вне проекта: `strict`, `target es2025`,
  `esModuleInterop` включены по умолчанию.
- **ast-grep 0.50+** молча пропускает custom languages из `sgconfig.yml`:
  `--custom-languages allow`.
- **`vercel setup`** ставит плагин в агентов и скил в `~/.agents/skills`
  мимо `npx skills` — согласуй с владельцем.
- **Shell инструмента Bash — bash 5**, не zsh: `setopt` и `${f:t}` молча
  не работают, пустой глоб остаётся строкой; проверка — `compgen -G`, пути
  с пробелами — `-z | xargs -0`. Перед массовым `mv`/`rm` выведи список.
- **`gdu`** — GNU `du` из coreutils; размеры — `ncdu`.
- **Mole** (`mo clean`, `purge`, `installer`) удаляет мимо Корзины, первый
  запуск — `--dry-run`. `~/.npm/_npx` и `~/.cache/uv` — место запуска
  MCP-серверов: до чистки `pgrep -fl 'npx|uvx'`.
- **`md search`** шлёт запрос и изменения корпуса во внешний embedding endpoint.
- **Длинные строки.** Абзац Markdown — часто одна строка: `cut -c` прячет
  конец, `rg -M 300 --max-columns-preview` помечает обрезанное.
- **`lychee`** вызывай напрямую: через `npx` вывод засоряют `npm notice`.

## Новое После Твоей Памяти

| Инструмент | Что | Где подробности |
|---|---|---|
| `gh` | `repo read-file`/`read-dir` без клона, `--attach 'file.png#alt'` в issue/PR, `pr checkout --worktree`, `skill`, `agent-task` | `gh <cmd> --help`, [releases](https://github.com/cli/cli/releases) |
| `vercel` 65 | `ci` — прогоны и логи CI, `deploy --verify`, `agent init` — AGENTS.md, `api`, `sandbox`, `traces`; `logs` по умолчанию runtime, CDN — `logs requests` | `vercel help <cmd>` |
| Python 3.15 | UTF-8 по умолчанию — `encoding=` в `open()` не обязателен; `lazy import` | [What's New](https://docs.python.org/3.15/whatsnew/3.15.html) |

## Нашёл Расхождение

Скил держится свежим находками агентов. Инструмент сломался, обновился,
повёл себя не так, как здесь написано, или нашлась ловушка, которой здесь
нет, — по ходу любой работы добавь в итог отдельную строку-предложение
правки этого скила: что увидел и какой командой проверить. Субагент передаёт
её родителю. Без поручения владельца скил сам не правь: правка глобальная
и идёт через проверку.
