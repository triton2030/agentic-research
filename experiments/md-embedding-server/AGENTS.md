# md-embedding-server Instructions

Эта подпапка — runtime-инструмент для глобальных skills `1md-navigator` и
`1md-graph`. Установленный `md` CLI считай агентной поверхностью; `src/navigator/`
— библиотечный слой, а `src/md_cli/` владеет dispatch, envelope wrapping,
transactions и JSON output.

## Перед Работой

- Перед содержательной работой в этой подпапке, если в repo есть uncommitted
  changes, сначала сделай backup commit и push текущего локального состояния.
  Потом продолжай от checkpoint, чтобы новые правки были отделимы.
- Читай минимальную owner-поверхность, которая может изменить маршрут:
  - CLI/catalog/envelope changes -> `docs/architecture-lock.md`,
    `docs/cli-conventions.md`, `src/md_cli/catalog.py`.
  - Library behavior -> целевой модуль в `src/navigator/` и public wrapper в
    `src/navigator/api.py`.
  - Public API / graph wrapper changes -> `docs/navigator-public-api.md`,
    `docs/architecture-lock.md`, `tests/test_navigator_public_api.py`.
  - Agent-facing output schema -> `src/navigator/schemas.py` и
    `src/md_cli/envelope.py`.
  - Developer gates -> `README.md`.
- Не редактируй legacy `src/navigator/cli.py` для установленной команды `md`,
  если задача явно не про legacy CLI. Package entry point:
  `md_cli.main:main`.

## Локальные Контракты

- `src/navigator/*` не импортирует `md_cli`.
- `src/navigator/api.py` — callable facade для `md_cli` catalog. Graph-facing
  wrappers (`scan/check/health/cycles/deps/impact/preflight/changed/init/strip`)
  строят `argparse.Namespace` через shared helpers (`_graph_args`,
  `_graph_docs`, `_graph_scan_docs`) и не передают `SimpleNamespace` в
  `load_docs` / `changed_markdown_paths`.
- `md_cli.handlers.*` остаются тонкими: возвращают `ToolResult`, не печатают
  JSON, не вызывают `sys.exit` и не оборачивают envelopes.
- `md_cli.runner` владеет envelope wrapping и JSON printing.
- Добавление или изменение публичной команды `md` требует осознанно обновить
  catalog contract: `src/md_cli/catalog.py`, handler, public API target,
  selftest smoke command и frozen snapshots/docs, если они входят в scope.
- Mutating или cost-bearing операции используют существующие dry-run/confirm и
  transaction patterns; не создавай параллельный safety-механизм.

## `md walk`

- `md walk` — focused reading поверх wikilinks, не semantic search и не
  `read-related`. Его используют после того, как уже выбран конкретный
  Markdown-файл и heading anchor.
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
