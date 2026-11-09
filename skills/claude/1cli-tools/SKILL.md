---
name: 1cli-tools
description: >-
  Use before writing a helper script or choosing a CLI for data, YAML, text
  edits, lint, security, media, browser, disk-space or system-health work;
  before npm or pnpm install/ci, running .ts with node, global tsc,
  agent-browser, browse, vercel, gh, uv tool or ffmpeg; and when an install succeeds
  but a package fails. Lists what is installed on this Mac and where familiar
  commands silently break. Markdown corpus search belongs to 1md-search.
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/versions.sh)
---

# CLI На Этом Mac

Твоя память не знает, что здесь установлено, и старее этих версий. Здесь —
только то, чего не скажет `--help`: что есть, где привычное тихо ломается
и что появилось после твоей памяти. Точный синтаксис — живой `--help`; он
побеждает этот текст. Перечень сверен 2026-10-31.

Версии сейчас: !`${CLAUDE_SKILL_DIR}/scripts/versions.sh`

Ловушки с номером версии проверены на этом номере: если живая версия ушла
от него, сверь ловушку по `--help` и предложи правку (раздел «Нашёл
Расхождение»). Версию инструмента вне этой строки смотри `TOOL --version`:
`command -v` не видит сломанную обёртку.

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
| браузер | `agent-browser` — свой Chromium без окна, для проверки своих страниц: не трогает Chrome владельца; `read <url>` отдаёт страницу Markdown-ом, сам ищет `llms.txt`; `skills list` — инструкции под эту версию; `a11y`, `vitals`, `react`, `diff`. `browse` (OpenCode) — настоящий Chrome владельца через расширение, когда нужны его входы на сайты: `browse execute` выполняет сценарий Playwright с условиями и ожиданиями за один вызов. `playwright` — при нестабильном прогоне трасса и `playwright show-trace` |
| медиа и документы | `ffmpeg` (VideoToolbox, SVT-AV1, VMAF), `fpcalc`, `pdftotext`, `soffice` |
| речь в текст | `whisper-cli` — всегда `-m ~/.cache/whisper.cpp/ggml-large-v3-turbo-q5_0.bin -l <язык>`, иначе ищет несуществующую модель и слушает по-английски; VAD — `--vad -vm ~/.cache/whisper.cpp/ggml-silero-v6.2.0.bin` |
| фото | `cwebp`, `dwebp`; numpy, Pillow, pillow-heif, OpenCV, scipy, scikit-image — в user site Python 3.15: видны с `python3 -P`, не с `-I`; `swiftc -O` с macOS Vision — OCR и вырезание (интерпретатор `swift` не успевает); ImageMagick нет |
| диск и система | `ncdu -o- -x <папка>` — дерево размеров JSON; `duf --json`; `mo status --json` (Mole) — память, процессы, температуры; `mo analyze`, `mo uninstall` — приложение с остатками; `btop` |
| сервисы | `gh`, `vercel`, `supabase`, `firecrawl`, `ntn` — Notion, `rclone` — Google Drive (`gdrive`, `gdrive-ro`) по скилу `1google-drive-archive` |
| агенты | `claude`, `droid`, `agy` — Google Antigravity, `muse` — Muse Code; `codex` из PATH — npm; `/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex` — отдельный движок, обновляется с приложением, его запускает мост Claude `experiments/codex-bridge` в мастерской agentic-research |
| скилы и токены | `qv-skill` — проверка пакета скила; `token-counter` |

## Тихие Ловушки

Ловушки отдельных работ — в справках. Открой справку до первой команды
своей работы:

- ставишь, обновляешь или чинишь пакет, runtime или CLI — npm, pnpm, uv,
  brew, node, PATH —
  [установка-и-обновление.md](references/установка-и-обновление.md): там
  случаи, когда установка проходит успешно, а пакет не работает или затирает
  чужое;
- запускаешь или проверяешь TypeScript — `tsc`, LSP-плагин TypeScript,
  dependency-cruiser, вывод `npm run` и `npx` —
  [javascript-и-typescript.md](references/javascript-и-typescript.md);
- запрашиваешь DuckDB, в том числе по транскриптам Claude —
  [данные.md](references/данные.md).

Остальные ловушки:

- **Shell инструмента Bash — bash 5**, не zsh: `setopt` и `${f:t}` молча
  не работают, пустой глоб остаётся строкой; проверка — `compgen -G`, пути
  с пробелами — `-z | xargs -0`. Перед массовым `mv`/`rm` выведи список.
- **Дробь через запятую** (bash 5.3). `$EPOCHREALTIME` и `printf '%.2f'`
  пишут `1,50`, хотя `locale` показывает `C`, и `bc` падает с `Parse error`.
  Замер времени начинай с `export LC_ALL=C`.
- **Проектный pin node** (`engines`, `.nvmrc`) сильнее глобального и сам
  runtime не переключает.
- **`rg` без пути** читает stdin: в оболочке агента он открыт, и поиск
  висит до тайм-аута. Всегда давай путь: `rg x .`.
- **`rg` и дефис** (15.2). `-h` — краткая справка, а не «без имени файла»:
  это `-I` (`--no-filename`). Образец с `-` в начале, например Matrix event id
  без `$`, читается как флаг: `rg -F '-x' f` молча даёт exit 1. Пиши
  `rg -e "$x"` или `rg -- "$x" f`.
- **Длинные строки.** Абзац Markdown — часто одна строка: `cut -c` прячет
  конец, `rg -M 300 --max-columns-preview` помечает обрезанное.
- **ast-grep 0.50+** молча пропускает custom languages из `sgconfig.yml`:
  `--custom-languages allow`.
- **`gdu`** — GNU `du` из coreutils; размеры — `ncdu`.
- **Mole** (`mo clean`, `purge`, `installer`) удаляет мимо Корзины, первый
  запуск — `--dry-run`. `~/.npm/_npx` и `~/.cache/uv` — место запуска
  MCP-серверов: до чистки `pgrep -fl 'npx|uvx'`.
- **`md search`** шлёт запрос и изменения корпуса во внешний embedding endpoint.
- **`lychee`** вызывай напрямую: через `npx` вывод засоряют `npm notice`.
- **`gh issue view N --comments`** (2.103) печатает только комментарии, без тела
  задачи; у задачи без комментариев — пустой вывод. Тело и комментарии вместе —
  `gh issue view N --json body,comments`.
- **`agent-browser`**: ссылки `@eN` из `snapshot` живут до следующего `open`,
  потом `Unknown ref`. Нажатие по роли переживает перезагрузку:
  `agent-browser find role button click --name "…"`.
- **`browse execute`** (0.0.16) без `--rm` или `--session` на каждый вызов
  заводит новую сессию и оставляет вкладку в Chrome владельца. Разовый вызов —
  `--rm`; несколько — `browse session new`, затем `--session <имя>`, в конце
  `browse session delete <имя>`. `page.screenshot()` снимает окно владельца
  в полном разрешении экрана: в замере 3392×2046, 5 МБ, 0,9 с;
  `{type: 'jpeg', scale: 'css'}` — 70 КБ за 0,06 с.

## Новое После Твоей Памяти

| Инструмент | Что | Где подробности |
|---|---|---|
| `gh` | `repo read-file`/`read-dir <путь> -R owner/repo` без клона (репозиторий вторым аргументом — ошибка `accepts at most 1 arg(s)`), `--attach 'file.png#alt'` в issue/PR, `pr checkout --worktree`, `skill`, `agent-task` | `gh <cmd> --help`, [releases](https://github.com/cli/cli/releases) |
| `vercel` 65 | `ci` — прогоны и логи CI, `deploy --verify`, `agent init` — AGENTS.md, `api`, `sandbox`, `traces`; `logs` по умолчанию runtime, CDN — `logs requests` | `vercel help <cmd>` |
| Python 3.15 | UTF-8 по умолчанию — `encoding=` в `open()` не обязателен; `lazy import` | [What's New](https://docs.python.org/3.15/whatsnew/3.15.html) |

## Нашёл Расхождение

Скил держится свежим находками агентов. Инструмент сломался, обновился,
повёл себя не так, как здесь написано, или нашлась ловушка, которой здесь
нет, — по ходу любой работы добавь в итог отдельную строку-предложение
правки этого скила: что увидел и какой командой проверить. Субагент передаёт
её родителю. Без поручения владельца скил сам не правь: правка глобальная
и идёт через проверку.

Ловушку одной работы предлагай в её справку, в тело — только нужную любой
задаче: после сжатия разговора Claude Code возвращает скил обрезанным
до первых 5 000 токенов, и разросшееся тело теряет конец.
