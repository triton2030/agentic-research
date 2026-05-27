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
  - Agent-facing output schema -> `src/navigator/schemas.py` и
    `src/md_cli/envelope.py`.
  - Developer gates -> `README.md`.
- Не редактируй legacy `src/navigator/cli.py` для установленной команды `md`,
  если задача явно не про legacy CLI. Package entry point:
  `md_cli.main:main`.

## Локальные Контракты

- `src/navigator/*` не импортирует `md_cli`.
- `md_cli.handlers.*` остаются тонкими: возвращают `ToolResult`, не печатают
  JSON, не вызывают `sys.exit` и не оборачивают envelopes.
- `md_cli.runner` владеет envelope wrapping и JSON printing.
- Добавление или изменение публичной команды `md` требует осознанно обновить
  catalog contract: `src/md_cli/catalog.py`, handler, public API target,
  selftest smoke command и frozen snapshots/docs, если они входят в scope.
- Mutating или cost-bearing операции используют существующие dry-run/confirm и
  transaction patterns; не создавай параллельный safety-механизм.

## Проверки

Default gates живут в `README.md`. Если пользователь явно просит пропустить
тесты, не изображай test pass, но прямо скажи, что изменение не проверено, и
держи правку достаточно маленькой для ручной проверки в работе.
