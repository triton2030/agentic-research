# Hermes Advanced Usage

Читай только для ветки, выбранной в основном `SKILL.md`. Во всех командах brief
передаётся через stdin; не интерполируй его в shell argument.

Contents: Session И Runtime Override; Toolsets И Nested Agents; Writes И
Worktree; Hermes-Native Возможности; Data И Failure Boundary.

```bash
HERMES_ADVISOR="${CODEX_HOME:-$HOME/.codex}/skills/1hermes/scripts/hermes_advisor.py"
```

## Runtime Override

Чтобы сменить runtime, начни fresh run:

```bash
python3 "$HERMES_ADVISOR" --cwd "$PWD" \
  --model MODEL --provider PROVIDER --reasoning LEVEL <<'HERMES_BRIEF'
<самодостаточный brief>
HERMES_BRIEF
```

Если указан только `--model`, Hermes выбирает provider из live catalog. Не
используй top-level `hermes -z ... --reasoning ...`: oneshot adapter не
доказывает effort в session evidence. Wrapper передаёт brief через
`hermes chat --query-file ... -Q` и проверяет фактический reasoning.

## Toolsets И Декомпозиция

Default `file,web` не даёт terminal/code/delegation. Любой execution-capable,
generative, stateful, composite или неизвестный toolset требует явного
`--allow-execution-tools`:

```bash
python3 "$HERMES_ADVISOR" --cwd "$PWD" \
  --allow-write --toolsets file,terminal,web --allow-execution-tools <<'HERMES_BRIEF'
<brief, явно ограничивающий команды и side effects>
HERMES_BRIEF
```

Если выбранный execution/delegation toolset позволяет Hermes вызывать других
агентов, потребность, бюджет и метод декомпозиции задай в brief или основном
skill. Wrapper не программирует число агентов и не интерпретирует их трассу.
Он лишь fail-closed обрабатывает неизвестные/composite toolsets и permissions.
`HERMES_WRITE_SAFE_ROOT` ограничивает `write_file`/`patch`, но не terminal;
execution-tools включай только когда пользователь разрешил их side effects.

## Writes И Worktree

`--allow-write` — обычный рабочий режим, а не исключение: агент Hermes правит
файлы там же, где это сделал бы ты, и отдельного разрешения владельца на каждый
такой run не требуется. Для свежей изолированной coding-задачи добавь
`--worktree` — правки уходят в отдельное дерево и вливаются после проверки;
`--worktree` без `--allow-write` отвергается:

```bash
python3 "$HERMES_ADVISOR" --cwd "$PWD" \
  --allow-write --worktree \
  --toolsets file,web <<'HERMES_BRIEF'
<точный write scope, tests и stop>
HERMES_BRIEF
```

Wrapper создаёт exact Git worktree сам, передаёт его как `cwd` и
`HERMES_WRITE_SAFE_ROOT`, а после принятого runtime/result сам создаёт локальный
commit. Модели terminal для сохранения результата не нужен. Без
`refs/remotes/*`, без file delta, при нечитаемом Git evidence или не-clean tree
run не принимается; push запрещён. Dirty partial result после runtime failure
сохраняется с recovery path, пустое дерево удаляется. После run проверь diff и
tests, затем интегрируй результат.

## Hermes-Native Возможности

- Browser/X research: сначала проверь `hermes tools list`, затем добавь только
  нужные `browser` и/или `x_search`.
- Большой цикл tool calls с промежуточной фильтрацией: добавь
  `code_execution --allow-execution-tools`; для одного tool call это лишнее.
- Hermes skill: передай повторяемый `--skill NAME`.
- Проверка на эхо: добавь `--isolated`, чтобы снять project rules, identity,
  memory и preloaded skills. `--skill` вместе с ним отвергается, потому что
  изоляция снимает и skill context.
- Exact runtime остаётся default. `--allow-fallback` используй только когда
  continuity важнее model identity; всегда покажи фактический `resolved`.
- MoA: используй `--model PRESET --provider moa` только по явному запросу на
  ensemble и после `hermes moa list`. Disabled preset выполняет лишь aggregator.
  MoA умножает model calls/cost, а session metadata не доказывает успех каждого
  reference slot.

Kanban, cron, messaging и `computer_use` — отдельные persistent/stateful
surfaces. Не включай и не настраивай их как побочный эффект advisor turn.

## Data И Failure Boundary

Hermes отправляет prompt и прочитанные материалы выбранному provider-у и хранит
session локально. Не подставляй API keys, base URLs или fallback providers для
восстановления без отдельного разрешения.

Не печатай сырой session export: он содержит system prompt, messages и
reasoning traces. Requested flags не доказывают runtime; принимай только
session-backed `resolved` evidence из wrapper JSON.
