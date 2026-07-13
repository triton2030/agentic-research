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

## Audit surface — только run_dir прогона

Единственный audit/debug owner прогона — его `run_dir` (`manifest.json`,
`events.jsonl`, `results.jsonl`, `result.json`). Default для всех трёх входов —
**локально в проекте работы**: `<project>/_workspace/codex-artifacts/<run_id>/`
(создаёт backend; артефакты не сыплются в чужое репо, субагентам это рабочая
зона — подпапки/архив свободно; при желании добавь `_workspace/` в `.gitignore`
проекта). `--run-dir PATH` — явный override; legacy `<backend>/runs/` остаётся
только fallback-ом без `--project`. Bridge стартует Codex-threads с
`ephemeral=True`, поэтому они не материализуются в общий `~/.codex` session
store. Единственное исключение — диалог ревьюера (`--dialog` / `--continue`):
такой тред персистентен (иначе resume невозможен), а run_dir для него
создаётся автоматически даже без флагов — audit owner обязателен.

**История Codex Desktop НЕ является audit surface для bridge** — не ищи прогоны
там. SDK под капотом запускает тот же локальный движок `codex app-server`, что и
Desktop, и делит с ним `~/.codex`; без `ephemeral` каждый вызов всплывал бы там
как новый чат. `~/.codex` остаётся общим owner-ом только для auth/config/runtime.
Доказательство в каждом прогоне — поле `codex.thread_ephemeral` в `result.json`.

## Модель и runtime-доступ

Backend явно закрепляет Codex turn defaults: `model=gpt-5.6-sol`,
`effort=xhigh` (Extra High). Это больше не зависит от текущего
`~/.codex/config.toml`; флаги `--model` и `--effort` остаются только для
осознанного override.

Это текущий потолок под ChatGPT-биллингом, проверено живыми пробниками
2026-07-10: `gpt-5.6-pro` и `gpt-5.6` (без суффикса) возвращают `HTTP 400 —
"not supported when using Codex with a ChatGPT account"`; наверху работает
только `gpt-5.6-sol` — тот же model ID, что в живом `~/.codex/config.toml`.
(Исторический probe 2026-07-02 аналогично отсёк `gpt-5.5-pro`.)

Вниз шкала есть. Движок несёт три слага 5.6-семейства — `gpt-5.6-sol` /
`gpt-5.6-terra` / `gpt-5.6-luna` (strings бинаря 0.144.2); `luna` и `terra`
проверены живыми пробниками 2026-07-13: `completed` под ChatGPT-auth, ~5-6 с
на `--effort low`. Это осознанный downgrade через `--model` для быстрых и
массовых прогонов: `luna` — экстра-быстрая неглубокая (широкий поиск/разведка
роем параллельных агентов), `terra` — средняя. Default остаётся
`gpt-5.6-sol`: на глубоких одиночных прогонах луной не экономить.

**Codex binary.** `gpt-5.6-sol` требует более новый движок, чем пинит SDK:
бандл-бинарь `codex-cli 0.137.0a4` (openai-codex 0.1.0b3) отвечает `HTTP 400 —
"requires a newer version of Codex"`. Поэтому `resolve_codex_bin()` в
`codex_defaults.py` подставляет в `CodexConfig.codex_bin` бинарь ChatGPT
Desktop (`/Applications/ChatGPT.app/Contents/Resources/codex`, на 2026-07-10 —
`0.144.0a4`; авто-обновляется вместе с приложением), с fallback на бандл SDK,
если приложения нет. Fallback означает возврат старого движка — свежие модели
на нём снова 400, поэтому он не молчаливый: entrypoint печатает
`SDK_BUNDLE_WARNING` в stderr, а фактический движок фиксируется в ledger —
`codex_bin` + `binary_source` (`chatgpt-app` | `sdk-bundle`) в блоке `codex`
каждого manifest/result и в stderr-banner (`binary=…`).

Шкала reasoning effort для bridge заканчивается на `xhigh`: живой
`config.toml` уже использует `ultra`, но wire-схема SDK (enum
`ReasoningEffort`) его не знает — `ultra` режется pydantic-валидацией даже
через `config_overrides` (проверено 2026-07-10). Появится в SDK — поднять.

Нижний рабочий порог — `low`, и он enforced: `--effort` ниже (`minimal`/`none`)
отсекается на валидации флагов (`REASONING_EFFORTS` в `codex_defaults.py`).
Причина: turn'у по умолчанию доступны инструменты (`web_search`/`image_gen`), и
Codex на `minimal` отвечает `HTTP 400 — "The following tools cannot be used with
reasoning.effort 'minimal': image_gen, web_search"` — валидация превращает этот
поздний runtime-фейл в мгновенный.

Permissions тоже задаются backend-ом явно:

- reviewer: `Sandbox.read_only` + `ApprovalMode.deny_all`;
- write-fleet: `Sandbox.workspace_write` + `ApprovalMode.auto_review`.

`Sandbox.full_access` не является default: он может менять файлы вне git/project
scope, а значит backend не сможет честно доказать postflight allowlist. Максимум
для v1 — свободная работа внутри workspace-write под declared `files`,
dirty-gate, ledger и scope-check.

## Биллинг: только ChatGPT-аккаунт, не API

Все SDK-входы (review / investigate / orchestrate, а также
`codex_threads.py archive/unarchive`; `list` SDK не запускает вовсе) перед
запуском дочернего codex-процесса вырезают из окружения `OPENAI_API_KEY` /
`CODEX_API_KEY` / `OPENAI_BASE_URL` (см. `cbcommon.py`), чтобы случайная
переменная не увела вызов на платный API. Строка `env чист` / `вырезано из
env: …` в логах подтверждает именно вычистку ключей; сам ChatGPT-login backend
не проверяет — auth берётся из твоего `codex login` (`auth_mode=chatgpt`), той
же подписки, что у интерактивного терминала.

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

# Диалог: персистентный тред → уточнения/возражения следующей репликой:
.venv/bin/python codex_review.py "ВОПРОС СОВЕТНИКУ" --dialog        # печатает thread_id
.venv/bin/python codex_review.py "УТОЧНЕНИЕ" --continue THREAD_ID   # контекст цел

# Полезные флаги:
#   --task "..."          задание для режима task (или позиционный аргумент)
#   --project PATH        корень проекта (по умолчанию cwd)
#   --transcript FILE     явный .jsonl (review/ask; по умолчанию — текущая сессия)
#   --model gpt-5.6-sol   default закреплён backend-ом
#   --effort xhigh        Extra High reasoning по умолчанию
#   --run-dir PATH        свежий ledger/result каталог
#   --summary-stdout      короткий JSON в stdout, полный ответ в final.md/result.json
#   --heartbeat-sec 120   heartbeat events; 0 отключает
#   --include-thinking    добавить блоки размышлений Claude (review/ask)
#   --max-chars N         бюджет транскрипта (review/ask; хвост сохраняется)
#   --dry-run             собрать промпт без вызова Codex (бесплатно)
#   --dialog              персистентный тред: thread_id в stderr/ledger, можно --continue
#   --topic "..."         тема диалога для реестра (видна другим агентам в codex_threads.py list)
#   --continue THREAD_ID  следующая реплика в существующий тред (только task-режим)
```

Режим `task` (default) транскрипт не подхватывает — это и есть смысл: вызов «как
субагент», самодостаточное задание, дёшево и быстро. Режимы `review` / `ask`
берут транскрипт текущей сессии по `CLAUDE_CODE_SESSION_ID` (иначе — свежайший
`.jsonl` в `~/.claude/projects/<кодированный-путь>/`); рендер сжимает лог:
реплики целиком, вызовы инструментов — одной строкой, дампы результатов усечены.

Если задан `--run-dir`, reviewer пишет `manifest.json`, `events.jsonl`,
`prompt.md`, `result.json`, а после реального Codex-run-а — `final.md`.

Диалог (`--dialog` / `--continue`) — исключение из ephemeral-дефолта: resume
работает только по rollout на диске (эфемерный тред → «no rollout found»,
проверено живыми пробниками 2026-07-12), поэтому диалоговые треды персистентны
и видны в Desktop-истории. Контракты:

- run_dir создаётся автоматически (audit owner обязателен); ledger фиксирует
  `thread_id`, `thread_persistent`, `resumed_from_thread`, событие `thread`.
- Provenance и статусная доска: `--dialog` пишет в
  `<project>/_workspace/codex-artifacts/dialog-threads.jsonl` событие `start`
  (тема из `--topic` или головы задания, короткий id сессии), `--continue` —
  событие `continue`; `--continue` по умолчанию принимает только треды из
  этого реестра — чужой Desktop/API-тред несёт непроверенные роль и контекст.
  Осознанный override — `--continue-foreign` (после него тред «усыновлён»
  реестром). Свёртка реестра и чистка — `codex_threads.py`:
  `list --project PATH` (тема/ходы/активность/сессия/run на тред; события
  несут `run_dir` — точный путь даже при custom `--run-dir`),
  `archive THREAD_ID | --stale [--older-hours 48]` (штатный SDK
  `thread_archive`; per-target ошибки не обрывают батч, rc=1 при частичном
  провале; `--stale` fail closed на битом реестре) и `unarchive THREAD_ID`.
  Руками `~/.codex` не чистить. Archive-событие provenance НЕ даёт — чужой
  тред нельзя «легализовать» его архивацией. Реестр append-only без локов:
  «чужой живой тред не трогай» — дисциплина агента, не backend-гарантия.
- Пустой THREAD_ID (потерянная `$VAR`) — отказ с кодом 2, не молчаливый новый
  тред. `--dry-run` валидирует CLI/prompt/реестр, но НЕ существование треда
  (`resume_checked=false` в ledger).
- Sandbox/approval переприбиваются на каждом turn'е — resume не ослабляет
  read-only. Реплика в `--continue` уходит без повторной обёртки ролью: роль
  и контекст уже в треде.

## Исследователь

```bash
# Codex читает проект; для записи проект недостижим — пишет себе в run_dir/out
# (+ системный temp); ответ забираешь из result.json:
.venv/bin/python codex_investigate.py "Изучи X в проекте и напиши отчёт в out/" --project "$PWD"

# Фоном + компактный stdout (штатный режим под фан-аут):
.venv/bin/python codex_investigate.py "..." --project "$PWD" \
  --run-dir "$B/runs/$(date -u +%Y%m%dT%H%M%SZ)-inv" --summary-stdout --heartbeat-sec 120
#   --dry-run   собрать промпт без вызова Codex
```

`run_dir` создаётся всегда (в нём живёт `out/`); default —
`<project>/_workspace/codex-artifacts/<run_id>/`. Codex видит в промпте
sandbox-контракт: читать весь диск свободно, складывать артефакты в `cwd`
(=`out/`, подпапки и своя структура — свободно) и в конце `result.md`, проект
не править. Backend пишет уникальный
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

Вторая граница: **MCP-серверы Codex живут вне sandbox** (отдельные процессы
движка) и могут писать в проект. Наблюдалось вживую: serena при онбординге
чужого проекта создала `.serena/` — sandbox это не блокировал, а `scope_status`
поймал (`failed` с точными путями). Поэтому scope-чек — не формальность, а
второй, независимый слой доказательства.

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
#   --model gpt-5.6-sol      default закреплён backend-ом
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
без worker responses. Полный ledger пишется в свежий run_dir
(default `<project>/_workspace/codex-artifacts/<run_id>/`; `manifest.json`,
`events.jsonl`, `results.jsonl`, `result.json`) или в свежий `--run-dir PATH`;
существующий каталог считается ошибкой. Постфлайт scope-чек исключает сам
run_dir и его collapsed-предков (`_workspace/`) — своя площадка прогона не
считается правкой проекта.

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
