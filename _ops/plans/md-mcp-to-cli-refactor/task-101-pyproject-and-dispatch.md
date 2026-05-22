# Bootstrap Python package + entry `md` + lazy dispatch

## Цель
Скелет `md_cli/` package с argparse-based dispatch, ленивой загрузкой модулей по subcommand, `pyproject.toml` под `uv tool install`. Никаких tool-handlers ещё нет — только инфраструктура диспатча и `md --version`, `md --help` работают.

Anchored in: `_ops/PROJECT-ROADMAP.md#md-mcp-to-cli-refactor`

## Применимые инструкции
- `AGENTS.md` (root)
- `experiments/md-embedding-server/AGENTS.md` (subtree, если есть)

## Зависимости
- task-001 закрыт (canonical signatures зафиксированы — нужен для argparse skeleton)
- task-002 закрыт (framework verdict — argparse vs Typer vs catalog-driven — определён)

## Architectural anchor (code locality)

**Весь код живёт в `experiments/md-embedding-server/`**. Skill folders НЕ получают никаких scripts/Python files. Это invariant: tool — stable, skills — disposable. Пользователь должен иметь возможность удалять/переименовывать skills без поломки CLI.

## Подшаги

- [ ] Решить layout. Рекомендуется:
  ```
  experiments/md-embedding-server/
  ├── pyproject.toml                  # NEW
  ├── src/
  │   ├── navigator/                  # moved from scripts/navigator/
  │   └── md_cli/                     # NEW
  │       ├── __init__.py
  │       ├── __main__.py             # entry point
  │       ├── main.py                 # argparse + lazy dispatch
  │       └── handlers/               # one module per subcommand (lazy import)
  ├── scripts/
  │   ├── md_navigator.py             # kept temporarily для backward use в Phase 1
  │   ├── md_graph.py                 # kept temporarily
  │   └── sync-skill-docs.py
  └── tests/
  ```

- [ ] Написать `pyproject.toml`:
  - `[project]` name = `md-tools`, version = `0.7.0` (bump from MCP's 0.6.1)
  - `[project.scripts]` `md = "md_cli.main:main"`
  - `[tool.uv]` или `[tool.hatch]` build config (выбрать build backend)
  - `[project.dependencies]` — минимум: `networkx`, `requests`, `pyyaml`, etc. (re-use existing deps)
  - Python `>=3.11`

- [ ] Перенести `scripts/navigator/` → `src/navigator/` (git mv, сохранить историю).
  - Обновить imports в `scripts/md_navigator.py` и `scripts/md_graph.py` (audit Implementation #10):
    - Эти entry points используют PEP 723 shebang `#!/usr/bin/env -S uv run --script` + `sys.path.insert(0, str(Path(__file__).resolve().parent))` + `from navigator.cli import main`
    - После move в `src/`, sys.path patch неверен. Обновить `sys.path.insert` to `Path(__file__).resolve().parent.parent / "src"` so `from navigator.cli import main` works
  - Проверить что `scripts/run-tests.sh` + Python tests ещё работают
  - Verify `scripts/md_navigator.py --help` работает (backward compat для Phase 1-4)

- [ ] Создать `src/md_cli/main.py` — dispatch с lazy import (audit Implementation #2):
  - Two-level dispatch:
    - **Top-level parser** строится из `catalog.py` ТОЛЬКО с именами + одна help-строка (`description.when` first sentence). Не загружает handler modules.
    - **`md --help`** показывает 29 subcommand names + краткие descriptions без import любого handler.
    - **`md <subcommand>`** → import handler module ТОЛЬКО когда subcommand выбран; handler регистрирует свой полноценный argparse subparser; `md <subcommand> --help` показывает full args.
  - Test: `python3 -c "from md_cli.main import main; import sys; sys.argv=['md','--help']; main()"; print('networkx in modules:', 'networkx' in sys.modules)` → False
  - Это NON-trivial argparse pattern; possibly use Click groups или Typer (per task-002 verdict)

- [ ] Создать `src/md_cli/handlers/__init__.py` пустой. Handlers сами добавляются в Phase 2.

- [ ] Добавить базовые универсальные flags на root parser:
  - `--version`
  - `--help` (auto)
  - `--json` (передаётся в subcommands)
  - `--corpus PATH` (если applicable, по convention — positional, не flag, но some tools его share)

- [ ] Установить локально editable:
  - `uv tool install --editable experiments/md-embedding-server/`
  - Проверить `md --version` → "0.7.0"
  - Проверить `md --help` показывает все 29 subcommands в списке (даже без handlers)

- [ ] Добавить в `experiments/md-embedding-server/tests/test_md_cli_dispatch.py`:
  - test: `md --version` returns 0 с правильной версией
  - test: `md --help` mentions все 29 tool names
  - test: `md nonexistent_tool` returns exit code 2 (argparse error)
  - test: lazy import — `md status` не загружает `networkx` (проверить через `sys.modules` после dispatch)

## Готово
- [ ] `experiments/md-embedding-server/pyproject.toml` существует, валиден (`uv tree` не падает)
- [ ] `src/navigator/` существует, старые тесты в `tests/` зелёные после move
- [ ] `src/md_cli/main.py` существует, argparse dispatch работает
- [ ] `uv tool install --editable` ставит `md` в PATH
- [ ] `md --version` → `0.7.0`
- [ ] `md --help` показывает 29 subcommand names
- [ ] `test_md_cli_dispatch.py` — все тесты зелёные
- [ ] Lazy import проверен: `md status` не impl-ит NetworkX до handler load

## Красные линии
- [ ] Не реализовывать ни одного tool handler в этой задаче. Только skeleton.
- [ ] Не удалять старые `scripts/md_navigator.py` / `md_graph.py` — нужны для Phase 1/2 backward operations.
- [ ] Не модифицировать `navigator/` внутренности — только переместить и поправить imports.

## Проверка
1. `cd experiments/md-embedding-server && uv tool install --editable .`
2. `md --version` → выводит `md-tools 0.7.0`
3. `md --help` → раздел subcommands перечисляет 29 имён
4. `cd experiments/md-embedding-server && uv run --frozen pytest tests/test_md_cli_dispatch.py -v` → all green
5. `python3 -c "import sys; from md_cli.main import main; sys.argv=['md','status','--help']; main()"` — не подгружает `networkx` (`'networkx' not in sys.modules`)
