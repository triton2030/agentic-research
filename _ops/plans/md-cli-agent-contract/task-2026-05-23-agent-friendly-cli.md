---
description: "Active handoff task for fixing agent-facing md CLI contracts after research-backed review."
read-before-edit:
  - "[[_ops/PROJECT-ROADMAP.md]]"
  - "[[_ops/project-graph.md]]"
  - "[[_ops/AGENTS.md]]"
  - "[[experiments/md-embedding-server/docs/cli-conventions.md]]"
  - "[[experiments/md-embedding-server/docs/architecture-lock.md]]"
edit-after-edit: []
---
# Task — Сделать `md` CLI исполняемым для агентов

Статус: выполнено, проверено.

Следующий active task:
`task-2026-05-23-md-cli-stabilization-refactor.md` — stabilization refactor
текущего `md` CLI без `v2 rewrite`.

## Зачем

Мы хотим улучшить `md` CLI не ради CLI-comfort, а потому что он стал рабочим
инструментом будущих агентов: `1md-navigator`, `1md-graph`, `1work-review` и
другие skills полагаются на него, чтобы читать Markdown-граф, индексировать
корпуса, проверять изменения и давать следующий шаг.

Сейчас инструмент почти работает, но нарушает главный агентный контракт:
подсказки `_envelope.next_step` и `corpus_state.recommended_action` иногда
нельзя выполнить буквально. Для человека это мелочь, для агента это сбой
управления: он копирует предложенный шаг, получает ошибку и теряет доверие к
инструменту.

## Откуда взяли рамку

Исследования и документы, на которые опираемся:

- SWE-agent ACI paper:
  https://arxiv.org/abs/2405.15793
  Вывод для нас: языковая модель — отдельный тип пользователя интерфейса.
  Ей нужны специально спроектированные команды, навигация, редактирование,
  тесты и информативные ошибки, а не просто человеческий CLI.
- Terminal Is All You Need:
  https://arxiv.org/abs/2603.10664
  Вывод для нас: терминал хорош для human-agent работы, потому что действия
  прозрачны, текстово совместимы с моделью и имеют низкий барьер входа.
  Но эти свойства надо сохранить дизайном CLI.
- Anthropic, Building effective agents:
  https://www.anthropic.com/engineering/building-effective-agents
  Вывод для нас: начинать с простого, не прятать поведение за лишними слоями,
  давать LLM хорошо документированный interface, который легко отлаживать.
- OpenAI Function Calling:
  https://developers.openai.com/api/docs/guides/function-calling
  Вывод для нас: tool outputs должны быть структурными, schema-backed и
  возвращать данные/действия так, чтобы следующий tool call был однозначен.
- OpenAI Structured Outputs:
  https://developers.openai.com/api/docs/guides/structured-outputs
  Вывод для нас: JSON mode недостаточен; агентные контракты должны проверять
  соответствие schema, а не только валидность JSON.
- tau-bench:
  https://arxiv.org/abs/2406.12045
  Вывод для нас: real-world tool agents ломаются не только на reasoning, но и
  на правилах, стабильности, повторяемости tool use и multi-turn state.
- SWE-agent CLI docs:
  https://swe-agent.com/latest/usage/cli/
  Вывод для нас: agent tooling должен иметь inspect/replay/debug поверхности,
  чтобы траектории можно было понять и воспроизвести.

Сжатый принцип: CLI для агента должен возвращать маленький, структурный,
copy-pasteable следующий шаг; если шаг небезопасен или невозможен, CLI должен
честно вернуть dry-run, schema hint или missing input, а не псевдокоманду.

## Контекст переписки

Точные реплики пользователя в этой ветке:

- «найди исследования как строить CLI инструменты для агентов»
- «Проверь наш код, что стоит добавить?»
- «Так ок давай подумаем над багами, сначала дай свой план как ты планируешь
  исправить баги и потом вызови субагентов критиков чтобы посмотри на твои
  предложения»
- «Так стой странно но у нас должны они быть записаны, проверь возможно скил
  свежих глаз сломан мы созадовали агентов»
- «Создай тогда новую папку, туда запиши задачу, как мы хотим улучшить наш
  скрипт. Опиши чётко, почему мы хотим это сделать, откуда мы взяли эти
  исследования. Короче, отдай полностью вот эту нашу переписку, чтобы я с
  новым агентом просто продолжил.»

Ход работы:

Пользователь попросил найти исследования про CLI для агентов. Мы нашли
research-backed рамку: агентный CLI должен быть
структурным, маленьким, предсказуемым, с `--json`, dry-run/confirm, стабильными
ids, коротким stdout и исполняемыми next steps.

Потом пользователь попросил: «Проверь наш код, что стоит добавить?». Мы
проверили `experiments/md-embedding-server`, потому что `_ops/project-graph.md`
определяет эту папку как runtime tooling для `1md-navigator` / `1md-graph`.
Полный тестовый прогон в `experiments/md-embedding-server` прошёл: `235
passed`. Узкий smoke тоже прошёл. Поэтому речь не о падении suite, а о
контрактных багах agent-facing подсказок.

Потом пользователь попросил сначала дать план исправления багов, затем вызвать
субагентов-критиков. План был:

1. Сделать `_envelope.next_step` исполняемым: убрать несуществующие аргументы
   и заменить их реальными CLI flags.
2. Сделать `corpus_state.recommended_action` безопасным: не предлагать
   `confirm: true` без `transaction_id` / `fingerprint`.
3. Добавить контрактные smoke-тесты, которые валидируют generated steps против
   реального catalog/parser.
4. Отложить полноценный lightweight mode для `search-read` в отдельное
   решение, если после исправления ложных подсказок он всё ещё нужен.

В следующей сессии named critics уже были доступны и отработали:
`developer-critic`, `architecture-critic` / Brooks и `trajectory-critic` /
Smith. Их общий verdict: направление правильное, но перед реализацией надо
усилить task-контракт, иначе можно починить два видимых симптома и оставить
неисполняемые подсказки в соседних agent-facing поверхностях.

## Найденные баги

### 1. `_envelope.next_step` предлагает несуществующие flags

Файл: `experiments/md-embedding-server/src/md_cli/envelope.py`.

Факты:

- `_narrow_for_large_reply` предлагает `top: 5` и текст `Try --top 5` для
  `md_search` / `md_search_read`.
- Реальный `md search` / `md search-read` использует `--limit`, не `--top`.
- Для `md_search_read` reason предлагает `--no-body`, но такого flag нет.
- Текущий test file
  `experiments/md-embedding-server/tests/test_envelope_truncation_hint.py`
  закрепляет неправильное поведение: ждёт `top` и `--no-body`.

Почему это важно:

Агент видит `_envelope.next_step`, считает его исполняемым, вызывает шаг и
получает invalid argument. Это ломает главное назначение envelope: помочь
агенту восстановиться после слишком большого ответа.

Ожидаемое исправление:

- Для `md_search` и `md_search_read` использовать `limit`, не `top`.
- Убрать `--no-body` из reason, пока такого режима нет.
- Для `search-read` допустимый безопасный fallback: уменьшить `limit`,
  уменьшить `token_budget` если он есть в реальной сигнатуре, или предложить
  сначала `md search --scope descriptions --limit N`.

### 2. `recommended_action` предлагает небезопасный bare confirm

Файл: `experiments/md-embedding-server/src/navigator/index_status.py`.

Факты:

- `_state_payload` возвращает `recommended_action` вида
  `{"tool": "md_index", "args": {"corpus": ..., "confirm": true}}`.
- Но `experiments/md-embedding-server/docs/cli-conventions.md` говорит:
  `--confirm` должен быть paired with `--transaction-id` для gated tools.
- `experiments/md-embedding-server/src/md_cli/handlers/_generic.py` блокирует
  bare confirm и возвращает `transaction_required`.
- Прямая проверка дала:
  `uv run md index tests/fixtures/sample-corpus --confirm --json` ->
  `{"error":"transaction_required","reason":"Confirm requires --transaction-id or --fingerprint."}`.

Почему это важно:

`md status ... --json` сам предлагает агенту шаг, который следующий вызов
запрещает. Это хуже, чем не дать подсказку: агент думает, что следует
официальному next action.

Ожидаемое исправление:

- В `recommended_action` для index/warmup/rebuild/no-index предлагать
  `dry_run: true`, а не `confirm: true`.
- Runnable confirm разрешён только после dry-run, когда есть `transaction_id`
  или `fingerprint`.
- Обновить golden fixtures / tests, которые ожидают старый bare confirm.

### 3. Нужен contract smoke для generated actions

Сейчас есть тесты поведения, но нет достаточного gate: «всё, что CLI сам
предлагает агенту, можно выполнить или оно явно помечает missing input».

Ожидаемое исправление:

- Проверить все `_envelope.next_step[*].args` против реального catalog/parser.
- Проверить, что generated action не содержит неизвестных args вроде `top` для
  `md_search`.
- Проверить, что `recommended_action.args.confirm is true` невозможен без
  `transaction_id` или `fingerprint`.
- Добавить regression tests на конкретные два бага выше.

### 4. Scoped `status` не должен расширять blast radius

Файл: `experiments/md-embedding-server/src/navigator/index_status.py`.

Факты из developer-critic:

- `md status` поддерживает `--path-include` / `--path-exclude`.
- `md index` тоже поддерживает эти filters.
- Текущий `_state_payload(state, corpus_root)` строит action только по corpus и
  не получает scope.

Почему это важно:

Агент может проверить узкий scope, а recommended action внезапно предложит
dry-run / index всего корпуса. Это не просто неисполняемость, а cost /
blast-radius surprise.

Ожидаемое исправление:

- Передавать в `recommended_action.args` те же `path_include` / `path_exclude`,
  которые были у `status`.
- Regression: `md status CORPUS --path-include keep/* --json` рекомендует
  `md_index` с тем же фильтром и `dry_run: true`, без bare `confirm`.

### 5. `recommended_action` шире, чем прямой `md status`

Файлы: `experiments/md-embedding-server/src/md_cli/runner.py`,
`experiments/md-embedding-server/src/md_cli/corpus_state.py`,
`experiments/md-embedding-server/src/navigator/workflows/orient.py`.

Факты из Brooks / Smith / developer-critic:

- `quick_corpus_state(...)` попадает в `_envelope` многих команд.
- `recommended_action` уже виден в golden payloads не только `md_status`, но и
  `md_search`, `md_edit_context`, `md_profile_sections`, `md_orient` и других.
- `corpus_state` имеет cache; старый bare confirm может пережить прямой fix
  `status`.

Ожидаемое исправление:

- Считать contract surface не `md status`, а все generated actions:
  `_envelope.next_step[*]` и любой вложенный `recommended_action`.
- Санитизировать или инвалидировать cached `corpus_state`, чтобы старые bare
  confirm actions не возвращались из cache.

### 6. `architecture-lock.md` stale по числу tools

Файл: `experiments/md-embedding-server/docs/architecture-lock.md`.

Факты из Brooks / Smith / developer-critic:

- `architecture-lock.md` говорит: `catalog.py` has exactly 29 tool entries.
- Live `catalog.py`, snapshot и tests сейчас ожидают 30 tools.

Ожидаемое исправление:

- До закрытия task синхронизировать lock с текущим catalog/snapshot.
- Лучше не хардкодить число как смысловой invariant; lock должен ссылаться на
  generated snapshot / catalog tests либо явно говорить current count `30`.

### 7. Graph-команды ломаются из вложенной папки с `--scan ../..`

Файлы: `experiments/md-embedding-server/src/navigator/graph_core.py`,
`experiments/md-embedding-server/src/navigator/api.py`,
`experiments/md-embedding-server/src/navigator/graph.py`.

Факты после проверки:

- Из корня проекта `md preflight ... --scan .` проходит clean.
- Из `experiments/md-embedding-server` команда
  `md preflight ../../_ops/plans/... --scan ../.. --json` раньше давала ложные
  `MISSING_TARGET` по ссылкам `_ops/...`.
- Причина: graph root брался из `Path.cwd()`, а не из scan scope, когда scan
  указывает на родительский проект.

Почему это важно:

Skill scripts и локальные tool wrappers часто запускаются из подпапки
инструмента, но сканируют родительский репозиторий. Для агента это обычный
рабочий сценарий, не edge case.

Ожидаемое исправление:

- Если `--scan` указывает на родителя или внешний scope, брать graph root из
  scan scope.
- Relative target сначала разрешать от invocation cwd, затем от graph root.
- Покрыть `preflight`, `deps`, `impact`, `changed` и direct `navigator.graph`
  CLI path.

### 8. `search-read` не должен заливать агенту полный body без лимита

Файл: `experiments/md-embedding-server/src/navigator/api.py`.

Факты после step-back / repo-map / IA-аудита:

- `search-read` — default agent path для “find + read”.
- Интерфейс уже имеет `token_budget`, значит новый `--mode` или `--no-body`
  не нужен для первого безопасного repair.
- Repo-map показывает, что owner поведения — `search_read(...)` в
  `src/navigator/api.py`; envelope только даёт recovery hint после large reply.
- IA-verdict: новый файл/папка не нужны; это поведенческий контракт
  существующего инструмента, не новый knowledge surface.

Ожидаемое исправление:

- При отсутствии `token_budget` применять bounded default.
- Явный `token_budget=0` оставить как unbounded escape hatch.
- Если top section больше бюджета, вернуть усечённый читаемый фрагмент, а не
  пустой результат.
- Отразить это в schema/catalog/tool snapshot и regression test.

## Не делать в этом task

- Не вводить большой новый command layer.
- Не переписывать весь `md` CLI.
- Не чинить custom-agent runtime visibility внутри этой задачи; это отдельный
  runtime/config problem.
- Не добавлять `--no-body` механически, пока не выбран интерфейс lightweight
  `search-read`.
- Не трогать Claude-side surfaces без отдельной явной просьбы.
- Не добавлять `--mode preview|full` для `search-read` в этом task: bounded
  default через существующий `token_budget` закрывает текущую жалобу без
  нового интерфейса.
- Не ограничивать проверку прямым `md status`: это слишком узко для цели.

## Подшаги

- [x] Прочитать live owner files перед правкой:
  `_ops/project-graph.md`,
  `experiments/md-embedding-server/docs/cli-conventions.md`,
  `experiments/md-embedding-server/docs/architecture-lock.md`.
- [x] Сначала добавить failing contract probe/test: собрать generated actions
  из `_envelope.next_step`, вложенных `recommended_action` и golden payloads.
- [x] Проверять generated action через real parser round-trip:
  `action -> catalog tool -> CLI argv -> build_parser().parse_args(argv)`.
- [x] Исправить `src/md_cli/envelope.py`: generated narrowing steps должны
  использовать только реальные CLI args.
- [x] Исправить tests around truncation hints: заменить `top` на `limit`,
  убрать ожидание `--no-body`.
- [x] Исправить `src/navigator/index_status.py`: `recommended_action` должен
  начинаться с `dry_run`, не с bare confirm.
- [x] Сохранить `path_include` / `path_exclude` из scoped `status` в
  recommended `md_index` action.
- [x] Проверить / исправить `src/md_cli/corpus_state.py`: cache не должен
  возвращать старый bare confirm.
- [x] Обновить golden/snapshot expectations, если они содержат старый
  `confirm: true`.
- [x] Добавить agent-contract tests для generated next actions.
- [x] Синхронизировать `docs/architecture-lock.md` с live catalog/snapshot
  count или wording.
- [x] Исправить graph root resolution для запуска из вложенной папки с
  `--scan ../..`.
- [x] Добавить regression test на nested cwd для `preflight`, `deps` и
  `impact`.
- [x] Добавить CLI smoke на все 30 subcommands из вложенной рабочей папки с
  относительными путями.
- [x] Сделать `search-read` bounded по умолчанию через существующий
  `token_budget`.
- [x] Сохранить явный `token_budget=0` как unbounded режим.
- [x] Добавить regression test на oversize top section: truncation вместо
  пустого результата.
- [x] Обновить schema/catalog/snapshot описание `md_search_read`.
- [x] Прогнать targeted tests.
- [x] Прогнать полный `uv run pytest` в `experiments/md-embedding-server`.
- [x] Проверить `git diff --check`.
- [x] Только после pass решить, нужен ли отдельный task на lightweight
  `search-read`.

## Acceptance

- [x] `md search` / `md search-read` truncation next_step больше не содержит
  `top`.
- [x] `md search-read` truncation reason больше не предлагает `--no-body`.
- [x] `md status CORPUS --json` не предлагает bare `confirm: true`.
- [x] `_envelope.corpus_state.recommended_action` нигде не предлагает bare
  `confirm: true`, включая cached path.
- [x] Если action содержит `confirm: true`, рядом есть `transaction_id` или
  `fingerprint`.
- [x] Scoped `md status --path-include/--path-exclude` сохраняет тот же scope в
  recommended `md_index --dry-run`.
- [x] Тесты защищают generated action contract, а не только конкретный текст
  reason.
- [x] Generated actions проходят parser round-trip против текущего `md` CLI.
- [x] Golden payloads не содержат bare confirm в generated actions.
- [x] `architecture-lock.md` не конфликтует с live catalog/snapshot count.
- [x] `md preflight` / `md deps` / `md impact` корректно разрешают repo-root
  links при запуске из `experiments/md-embedding-server` с `--scan ../..`.
- [x] Все 30 CLI subcommands возвращают JSON envelope не только из package root,
  но и из вложенного cwd с относительными путями.
- [x] `md search-read` без `--token-budget` больше не является unbounded body
  dump; oversize section возвращается усечённой, а не пустой.
- [x] `md search-read --token-budget 0` сохраняет старый unbounded escape hatch.
- [x] `uv run pytest` проходит в `experiments/md-embedding-server`.
- [x] Новый агент может продолжить без устного контекста из этого файла.

## Evidence

- `uv run pytest` → `243 passed`.
- `uv run pytest tests/test_corpus_state.py tests/test_generated_actions_contract.py tests/test_envelope_truncation_hint.py tests/test_mutating_handlers.py` → `17 passed`.
- `uv run pytest tests/test_contract_fixes.py tests/test_navigator_public_api.py` → `18 passed`.
- `uv run pytest tests/test_cli_smoke_all_tools.py` → `2 passed`.
- `uv run pytest tests/test_real_world_complaints.py tests/test_search_smoke.py tests/test_schemas.py` → `17 passed`.
- `uv run pytest tests/test_real_world_complaints.py tests/test_search_smoke.py tests/test_schemas.py tests/test_catalog_contract.py tests/test_envelope_golden.py tests/test_mcp_cli_parity.py` → `30 passed`.
- `uv run md tools md_search_read --json` → catalog mentions `token_budget`
  default 3000 and `0 = unbounded`.
- `git diff --check -- experiments/md-embedding-server _ops/plans/md-cli-agent-contract` → pass.
- `rg '"confirm": true|--no-body|Try --top 5|has exactly 29 tool' ...` →
  no matches on production/golden/lock surfaces.
- Manual probes passed:
  `md search`, `md search-read`, `md status`, scoped `md status`, and blocked
  bare `md index --confirm`.
- Nested graph probes passed from `experiments/md-embedding-server`:
  `md preflight ../../_ops/plans/... --scan ../.. --json`,
  `md deps ../../_ops/plans/... --scan ../.. --json`,
  `md impact ../../_ops/PROJECT-ROADMAP.md --scan ../.. --json`, and
  `python -m navigator.graph preflight ../../_ops/plans/... --scan ../.. --json`.

## Проверка

Запускать из `experiments/md-embedding-server`:

```bash
uv run pytest tests/test_generated_actions_contract.py tests/test_envelope_truncation_hint.py tests/test_envelope_golden.py tests/test_mutating_handlers.py
uv run pytest
git diff --check -- experiments/md-embedding-server _ops/plans/md-cli-agent-contract
```

Полезные ручные probes:

```bash
uv run md search tests/fixtures/sample-corpus --query "agent" --json
uv run md search-read tests/fixtures/sample-corpus --query "agent" --json
uv run md status tests/fixtures/sample-corpus --json
uv run md status tests/fixtures/sample-corpus --path-include "*.md" --json
uv run md index tests/fixtures/sample-corpus --confirm --json
```

Ожидание: последний probe должен оставаться blocked как `transaction_required`,
а `status` не должен сам рекомендовать такой blocked call.

## Открытое сомнение

Решение после проверки: отдельный task на lightweight `search-read` сейчас не
создавать. Текущий evidence указывает на более дешёвый repair: bounded default
через существующий `token_budget`, с явным `token_budget=0` для ручного
unbounded чтения.
