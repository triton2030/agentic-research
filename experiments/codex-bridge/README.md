# codex-bridge

Вызов Codex (ChatGPT) из Claude Code. Зеркало `claude-bridge` (тот гоняет Claude
из Codex; этот — Codex из Claude).

Три профиля — по оси «что Codex может ПИСАТЬ» (читает во всех весь диск):

- **Консультант / ревьюер** (`codex_review.py`) — read-only, ничего не пишет.
  Два способа дать контекст:
  - **`task` (default)** — задание/вопрос БЕЗ транскрипта, как вызов субагента.
    Codex видит файлы проекта, но не историю сессии. Дёшево и быстро — основной
    режим. `codex_review.py "задание"`.
  - **`review` / `ask`** — с транскриптом текущей сессии Claude: стороннее ревью
    ХОДА работы или вопрос «по нашему диалогу». Дороже; бери, только когда Codex
    реально нужна история, а не файлы проекта.
- **Исследователь** (`codex_investigate.py`) — читает весь проект и диск; ПРОЕКТ
  для записи недостижим на уровне sandbox (cwd=out, `workspace_write`), не
  постфактум-проверкой. Выходная папка Codex — `run_dir/out/`. Для «изучи X,
  собери данные, напиши отчёт»: Codex складывает артефакты в `out/`, Claude
  забирает `result.json` (uniform-контракт) и сливает фан-аут кодом. Как вызов
  субагента: транскрипт не тянется.
- **Флот воркеров** (`codex_orchestrate.py`) — guarded shared-worktree
  workspace-write. Claude как оркестратор раздаёт file-disjoint задачи, backend
  валидирует контракт до запуска Codex, гонит N Codex параллельно (`AsyncCodex`
  + лимит concurrency), пишет run ledger и проверяет aggregate postflight scope.

Управляется глобальным скиллом **`1codex`** (`~/.claude/skills/1codex/`).

## Long-run control

Долгие запуски должны быть Claude-native background Bash jobs. Backend не
управляет процессами Claude: он пишет свежий `run_dir`, компактный stdout и
файловые результаты, чтобы Claude мог продолжать работу и по необходимости
читать `events.jsonl` / `result.json`.

Для background-safe режима используй `--summary-stdout --run-dir PATH`.
`PATH` должен быть свежим: каталог создаёт backend. Stdout будет коротким JSON
с `run_id`, `run_dir`, статусами и путями; полный ответ лежит на диске.
`--heartbeat-sec N` пишет `heartbeat` events во время Codex-run-а (`0`
отключает). `Monitor` можно включать только как filtered watcher поверх
`events.jsonl`; raw stdout/stderr не мониторить.

## Audit surface — только `runs/`

Единственный audit/debug owner прогона — каталог `runs/<run_id>/` (`manifest.json`,
`events.jsonl`, `results.jsonl`, `result.json`). Bridge стартует Codex-threads с
`ephemeral=True`, поэтому они не материализуются в общий `~/.codex` session store.

**История Codex Desktop НЕ является audit surface для bridge** — не ищи прогоны
там. SDK под капотом запускает тот же локальный движок `codex app-server`, что и
Desktop, и делит с ним `~/.codex`; без `ephemeral` каждый вызов всплывал бы там
как новый чат. `~/.codex` остаётся общим owner-ом только для auth/config/runtime.
Доказательство в каждом прогоне — поле `codex.thread_ephemeral` в `result.json`.

## Модель и runtime-доступ

Backend явно закрепляет Codex turn defaults: `model=gpt-5.5`,
`effort=xhigh` (Extra High). Это больше не зависит от текущего
`~/.codex/config.toml`; флаги `--model` и `--effort` остаются только для
осознанного override.

`--effort minimal` использовать нельзя: turn'у по умолчанию доступны инструменты
(`web_search`/`image_gen`), а Codex отвечает `HTTP 400 — "The following tools
cannot be used with reasoning.effort 'minimal': image_gen, web_search"`. Нижний
рабочий порог — `low`.

Permissions тоже задаются backend-ом явно:

- reviewer: `Sandbox.read_only` + `ApprovalMode.deny_all`;
- write-fleet: `Sandbox.workspace_write` + `ApprovalMode.auto_review`.

`Sandbox.full_access` не является default: он может менять файлы вне git/project
scope, а значит backend не сможет честно доказать postflight allowlist. Максимум
для v1 — свободная работа внутри workspace-write под declared `files`,
dirty-gate, ledger и scope-check.

## Биллинг: только ChatGPT-аккаунт, не API

Оба скрипта перед запуском дочернего codex-процесса вырезают из окружения
`OPENAI_API_KEY` / `CODEX_API_KEY` / `OPENAI_BASE_URL` (см. `cbcommon.py`),
чтобы случайная переменная не увела вызов на платный API. Codex использует твой
`codex login` (`auth_mode=chatgpt`) — ту же подписку, что и интерактивный
терминал. В логах строка `env чист` или `вырезано из env: …` подтверждает это.

Это прямое зеркало того, как `claude-bridge` вырезает `ANTHROPIC_API_KEY`.

## Установка

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt   # openai-codex
```

SDK тянет собственный пиннутый бинарь `codex`; он читает глобальный
`~/.codex/auth.json`, поэтому отдельный логин не нужен.

## Консультант / ревьюер

```bash
# DEFAULT — задание/вопрос без транскрипта (Codex видит файлы проекта):
.venv/bin/python codex_review.py "Проверь, нет ли гонки в codex_orchestrate.py"
.venv/bin/python codex_review.py --task "Сверь README с реальными флагами кода"

# Стороннее ревью ХОДА текущей сессии (нужен транскрипт):
.venv/bin/python codex_review.py --mode review

# Вопрос «по нашему диалогу» (нужен транскрипт):
.venv/bin/python codex_review.py --mode ask --question "Где здесь дыра в подходе?"

# Полезные флаги:
#   --task "..."          задание для режима task (или позиционный аргумент)
#   --project PATH        корень проекта (по умолчанию cwd)
#   --transcript FILE     явный .jsonl (review/ask; по умолчанию — текущая сессия)
#   --model gpt-5.5       default закреплён backend-ом
#   --effort xhigh        Extra High reasoning по умолчанию
#   --run-dir PATH        свежий ledger/result каталог
#   --summary-stdout      короткий JSON в stdout, полный ответ в final.md/result.json
#   --heartbeat-sec 120   heartbeat events; 0 отключает
#   --include-thinking    добавить блоки размышлений Claude (review/ask)
#   --max-chars N         бюджет транскрипта (review/ask; хвост сохраняется)
#   --dry-run             собрать промпт без вызова Codex (бесплатно)
```

Режим `task` (default) транскрипт не подхватывает — это и есть смысл: вызов «как
субагент», самодостаточное задание, дёшево и быстро. Режимы `review` / `ask`
берут транскрипт текущей сессии по `CLAUDE_CODE_SESSION_ID` (иначе — свежайший
`.jsonl` в `~/.claude/projects/<кодированный-путь>/`); рендер сжимает лог:
реплики целиком, вызовы инструментов — одной строкой, дампы результатов усечены.

Если задан `--run-dir`, reviewer пишет `manifest.json`, `events.jsonl`,
`prompt.md`, `result.json`, а после реального Codex-run-а — `final.md`.

## Исследователь

```bash
# Codex читает проект, пишет только в свою run_dir/out; ответ забираешь из result.json:
.venv/bin/python codex_investigate.py "Изучи X в проекте и напиши отчёт в out/" --project "$PWD"

# Фоном + компактный stdout (штатный режим под фан-аут):
.venv/bin/python codex_investigate.py "..." --project "$PWD" \
  --run-dir "$B/runs/$(date -u +%Y%m%dT%H%M%SZ)-inv" --summary-stdout --heartbeat-sec 120
#   --dry-run   собрать промпт без вызова Codex
```

`run_dir` создаётся всегда (в нём живёт `out/`). Codex видит в промпте
sandbox-контракт: читать весь диск свободно, складывать артефакты в `cwd`
(=`out/`) и в конце `result.md`, проект не править. Backend пишет уникальный
`result.json`: `status`, `artifacts` (файлы, реально созданные в `out/`),
`scope_status` (второе, независимое доказательство «проект не тронут»; из
проверки исключены `out/` и ledger-файлы; `scope=failed` роняет `ok` в false),
`final_response`.

**Гарантия и её граница (проверено эмпирически).** Запись в ПРОЕКТ блокируется
sandbox (`operation not permitted`); чтение вне workspace проходит. Но
enforced-writable множество под `workspace_write` = `cwd` (out) + системный temp
(`/tmp`, `$TMPDIR`) — не только `out/`. Сузить до одного `out/` этим SDK нельзя:
для enum-`Sandbox` он шлёт фиксированную per-turn политику, и
`writable_roots`/`exclude_slash_tmp` через `config_overrides` игнорируются. То
есть гарантия, на которую мы опираемся, — «проект недостижим для записи», а не
«пишет исключительно в out/». Для проекта это безопасно (temp эфемерен и не
является deliverable-поверхностью).

Разделение профилей: ревьюер — только смотрит; исследователь — смотрит и пишет
СЕБЕ (проект не трогает); флот — пишет В ПРОЕКТ под file-disjoint контрактом.

## Флот воркеров

```bash
echo '[
  {"id":"f1","prompt":"Перепиши краткое описание вверху файла короче и яснее","files":["docs/a.md"]},
  {"id":"f2","prompt":"То же для второго файла","files":["docs/b.md"]}
]' | .venv/bin/python codex_orchestrate.py --concurrency 4 --project "$PWD"

# или из файла:
.venv/bin/python codex_orchestrate.py --tasks tasks.json --project "$PWD"
#   --dry-run               validate + ledger без запуска Codex
#   --model gpt-5.5          default закреплён backend-ом
#   --effort xhigh           Extra High reasoning по умолчанию
#   --summary-stdout         короткий JSON в stdout, полный result.json на диске
#   --heartbeat-sec 120      heartbeat events во время Codex workers
#   --verify "pytest ..."   команда проверки после workers и scope-check
```

Вход — JSON-массив задач. `prompt` и `files` обязательны; `id` опционален;
`allow_create: true` разрешает создание отсутствующего файла. `cwd` в задаче
больше не поддерживается: все воркеры запускаются из `--project`. Unknown keys,
не-bool `allow_create`, не-string `id`, absolute paths, `..`, пустые `files`,
overlap между задачами и `concurrency < 1` падают до импорта Codex и до любых
трат.

Выход в stdout — JSON object. По умолчанию он остаётся полным и включает
результаты воркеров. С `--summary-stdout` stdout становится компактным:
`run_id`, `run_dir`, статусы, `codex`, `paths`, счётчики и postflight summary
без worker responses. Полный ledger пишется в свежий `runs/<run_id>/`
(`manifest.json`, `events.jsonl`, `results.jsonl`, `result.json`) или в свежий
`--run-dir PATH`; существующий каталог считается ошибкой.

### Контракт оркестрации (обязателен)

- **File-disjoint enforced.** Backend нормализует `files` и reject-ит overlap
  до запуска Codex. `files` — exact file paths, не directory/prefix scopes.
- **Git safety fail-closed.** Реальный write-run требует рабочий git worktree.
  `--dry-run` может работать вне git, но помечает `git.available=false`.
- **Dirty-overlap gate + fingerprint snapshot.** По умолчанию запуск блокируется,
  если текущие dirty files пересекаются с `files` задач. Override:
  `--allow-dirty-overlap`. Все initial dirty files fingerprint-ятся; если
  воркер меняет любой non-allowlisted dirty file, `scope_status=failed`.
- **Scope-check после запуска.** Изменённые path fingerprints и смена `HEAD`
  проверяются после workers; changed files должны входить в union declared
  `files`, иначе `scope_status=failed`.
- **Verification отдельно.** `worker_status=completed` не равно done.
  `--verify CMD` даёт `verification_status=passed`; без verify статус
  `not_requested`, а `fully_verified=false`.
- **Shared-worktree limitation.** Этот режим не доказывает, какой именно worker
  изменил файл. Worktree isolation и patch reducer — следующий слой, не v1.

## Статус

v1 hardening: read-only reviewer сохранён; write-fleet стал guarded
shared-worktree orchestrator с strict schema, git snapshot scope-check, ledger и
no-spend тестами. Пути в скилле `1codex` абсолютные и привязаны к расположению
этого репо.
