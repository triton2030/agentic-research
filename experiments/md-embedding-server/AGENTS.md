# md-embedding-server Instructions

Эта подпапка — runtime-инструмент для глобальных skills `1md-navigator` и
`1md-graph`. Установленный `md` CLI считай агентной поверхностью; `src/navigator/`
— библиотечный слой, а `src/md_cli/` владеет dispatch, envelope wrapping,
transactions и JSON output.

## Перед Работой

- Грязное git-дерево здесь нормально: не требуй backup commit/push и не
  привязывай runtime проверки к GitHub. Работай с текущим содержимым файлов и
  не откатывай чужие правки.
- Читай минимальную owner-поверхность, которая может изменить маршрут:
  - CLI/catalog/envelope changes -> `docs/architecture-lock.md`,
    `docs/cli-conventions.md`, `src/md_cli/catalog.py`.
  - Library behavior -> целевой модуль в `src/navigator/` и public adapter в
    `src/navigator/api_*.py` / facade `src/navigator/api.py`.
  - Public API / graph wrapper changes -> `docs/navigator-public-api.md`,
    `docs/architecture-lock.md`, `tests/test_navigator_public_api.py`.
  - Agent-facing output schema -> `src/navigator/schemas.py` и
    `src/md_cli/envelope.py`.
  - Developer gates -> `README.md`.
- Установленная команда `md` имеет единственный entry point
  `md_cli.main:main` (`src/md_cli/main.py`); библиотечное поведение живёт в
  `src/navigator/`, обёрнутое domain-адаптерами `src/navigator/api*.py`.

## Локальные Контракты

- `src/navigator/*` не импортирует `md_cli`.
- `src/navigator/api.py` — thin callable facade для `md_cli` catalog.
  Domain adapters живут в `src/navigator/api_graph.py`, `api_search.py`,
  `api_audit.py` и `api_profile.py`. Graph-facing wrappers
  (`scan/check/health/cycles/deps/impact/preflight/init/strip`) строят
  `GraphArgs` (dataclass из `graph_core.py`) через shared helpers (`_graph_args`,
  `_graph_docs`, `_graph_scan_docs`) в `api_graph.py`; graph-примитивы берут из
  `graph_core` / `graph_reports` (legacy `navigator.graph` удалён). Profile-backed
  workflow commands stay as thin
  `navigator.workflows` aliases; profile/query/refactor DB ownership lives in
  `api_profile.py`, not in workflow modules.
- `src/navigator/markdown_io.py` — единственный владелец Markdown/link
  parsing и heading-bounded section reading. `pick.py` выбирает ids/token
  budget, но не владеет границами секций. `graph_edges.py` может строить
  graph-specific edges, но не держит второй wikilink/markdown-link parser.
- `src/navigator/audit.py` — audit detection/payload owner. CLI adapter,
  Markdown render и severity-policy живут в `audit_cli.py`,
  `audit_render.py`, `audit_severity.py`; не раздувай `audit.py` обратно за
  1000 строк.
- `md_cli.handlers.*` остаются тонкими: возвращают `ToolResult`, не печатают
  JSON, не вызывают `sys.exit` и не оборачивают envelopes.
- `md_cli.runner` владеет envelope wrapping и JSON printing.
- Добавление или изменение публичной команды `md` требует осознанно обновить
  catalog contract: `src/md_cli/catalog.py`, handler, public API target,
  selftest smoke command и frozen snapshots/docs, если они входят в scope.
- Agent-facing reading/audit commands follow the context ladder: normal output
  is a bounded map/preview tagged `view:"map"`; full bodies or evidence require
  explicit `--expanded` / `read_next`, and everything hidden stays reachable
  there (no dead ends). The single agent-view projection lives in
  `md_cli.envelope.project_payload` (drops `rowid`/`content_hash`, relativizes
  non-anchor paths, collapses `map_only`/`content_included` → `view`). Tools
  shape rows; `read_next` is one payload-level channel, not per-item.
  `--compact` / `map_only` / `content_included` are retired.
- Mutating или cost-bearing операции используют существующие dry-run/confirm и
  transaction patterns; не создавай параллельный safety-механизм.

## `md coherence-audit` и `md walk`

- `md coherence-audit` — post-edit reader/audit для выбранного Markdown-файла
  или heading. Он игнорирует frontmatter, сохраняет inline `[[...#...]]`
  ссылки на месте и вставляет раскрытый heading-bounded блок сразу после
  каждой такой ссылки. Bare wikilinks без `#anchor` не раскрываются.
- Каноническая команда:
  `md coherence-audit PATH --scan ROOT --depth 2 --token-budget 6000 --json`.
- Если меняешь семантику `coherence-audit`, обнови вместе
  `src/navigator/coherence_audit.py`, `src/navigator/api.py`,
  `src/md_cli/catalog.py`, selftest smoke command, snapshots/docs, `1md-reader`
  и пример на реальном corpus.

- `md walk` — focused reading поверх wikilinks, не semantic search и не
  `read-related`. Это legacy chain-reader: его используют после того, как уже
  выбран конкретный Markdown-файл и heading anchor, когда нужна цепочка первой
  якорной ссылки, а не inline coherence audit.
- Каноническая команда:
  `md walk PATH --anchor "HEADING" --scan ROOT --depth 3 --token-budget 3000 --json`.
- Алгоритм читает только тело текущей heading-bounded секции, берёт первую
  anchored wikilink в порядке текста и идёт по ней дальше. Same-file anchors
  `[[#Heading]]` считаются обычным следующим блоком.
- Bare wikilinks без `#anchor` не раскрываются: tool пропускает их и считает в
  `stats.skipped_bare_wikilinks`. `no_anchored_outlink` означает конец цепочки
  или недостаточно точные ссылки, а не доказательство, что темы нет.
- Output держит два слоя: `chain` для структурного разбора и `text` как один
  attributed packet с маркерами источника. Не убирай source markers без замены
  на другой явный attribution.
- Если меняешь семантику `md walk`, обнови вместе `src/navigator/walk.py`,
  `src/md_cli/catalog.py`, selftest smoke command, snapshots/docs и ручной
  пример на реальном corpus. Не добавляй embeddings в `walk`: сходство блоков
  остаётся задачей `search-read` / future separate signal.

## Проверки

Default gates живут в `README.md`. Если пользователь явно просит пропустить
тесты, не изображай test pass, но прямо скажи, что изменение не проверено, и
держи правку достаточно маленькой для ручной проверки в работе.
