# Реальный write-gate перед Edit/Write

## Цель

Заменить лёгкое напоминание о criteria из UserPromptSubmit на реальный structural gate. PreToolUse-hook блокирует Edit/Write/MultiEdit если в session-state нет prior Read из applicable criteria для целевого пути.

## Применимые критерии и инструкции

* [\_ops/criteria/repo-structure-and-runtime-guards.md](/broken/pages/QwzQ0cLtKIkYIVyLwG1X) — новый structural control surface, runtime guardrail.
* [\_ops/criteria/skill-authoring.md](/broken/pages/kqzBNg5rfgUwBptEqmGD) — UserPromptSubmit как reminder, PreToolUse как gate.
* [\_ops/criteria/instruction-layer.md](/broken/pages/gm24WNIfQ3REVOMpf3f9) — placement.

## Контекст

Требует session-state из Task 02 и миграции hooks из Task 03. Восстанавливает retired `criteria-gate.py` (10kb, retired 2026-05-12 — вероятно как noisy) с новой session-state-aware логикой.

## Подшаги

1. Изучить retired criteria-gate. EN: Read `~/.claude/skills/1start-here/scripts/_retired/criteria-gate.py`. Document why it was retired by reading git log and inline comments — likely noisy or false-positive prone. Capture those failure modes to avoid them in rewrite.
2. Спроектировать applicable-mapping. EN: Design simple mapping from cwd + target path to applicable criteria. Use criteria file frontmatter description for matching. Fail-open if no match — log warning, do not block.
3. Переписать `criteria-gate.py` с session-state. EN: Implement PreToolUse hook with session-state-aware logic: read `session-state.anchor_reads`, check if any applicable criteria has at least one entry in current session. Block only if absent and applicable criteria is determinable. Block message references specific path.
4. Wire в settings.json. EN: Add PreToolUse entry to `~/.claude/settings.json` triggering on Edit, Write, MultiEdit. Validate JSON structure after edit using `python3 -c 'import json; json.load(open(...))'`.
5. Tests через subagent. EN: Run two bare-prompt subagent tests — (a) "обнови `1planning` SKILL.md" without prior Read of references → expect block with specific applicable path, (b) same task with prior Read of applicable criteria → expect pass.

## Готово

* [ ] `criteria-gate.py` живёт в `scripts/` (не `_retired/`).
* [ ] `settings.json` PreToolUse wired и JSON валиден.
* [ ] Applicable-mapping documented в reference doc.
* [ ] Subagent test (a) blocks с конкретным путём.
* [ ] Subagent test (b) проходит.

## Красные линии

* [ ] Не делать fail-closed на ambiguous mapping — false-positives ломают workflow.
* [ ] Не дублировать UserPromptSubmit reminder в block message.
* [ ] Не блокировать tool calls на ошибках самого hook (fail-open).

## Stop rule

Если false-positive rate >20% (legit edits блокируются) на 10 test задачах — отключить PreToolUse, переоценить mapping или вернуть в `_retired/` с задокументированной причиной.

## Проверка

1. `cat ~/.claude/settings.json | jq '.hooks.PreToolUse'` Ожидаемо: entry для Edit/Write/MultiEdit с `criteria-gate.py`.
2. Subagent "обнови `~/.claude/skills/1planning/SKILL.md`" без prior Read. Ожидаемо: PreToolUse block с конкретным путём applicable criteria.
3. Subagent с prior Read applicable criteria. Ожидаемо: проходит без блока.

## Handoff

После закрытия → Task 05 усиливает trigger surface skills — после миграции hooks они должны срабатывать ещё надёжнее, чтобы PreToolUse был последней страховкой, а не первой линией.
