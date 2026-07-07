# Память сессии для hooks и skills

## Цель

Создать shared structure `~/.claude/state/session-{session_id}.json`, доступную и hooks-скриптам, и skills. Это разрывает re-read loops (через mtime-сравнение) и привязывает маркеры work-review / user-truth к substance (skill пишет `applied_criteria`, hook читает).

## Применимые критерии и инструкции

* [\_ops/criteria/repo-structure-and-runtime-guards.md](/broken/pages/QwzQ0cLtKIkYIVyLwG1X) — runtime guards, new structural control surface.
* [\_ops/criteria/skill-authoring.md](/broken/pages/kqzBNg5rfgUwBptEqmGD) — minimal owner surface.
* [\_ops/criteria/instruction-layer.md](/broken/pages/gm24WNIfQ3REVOMpf3f9) — placement structural controls.
* [\_ops/criteria/planning-surface-ownership.md](/broken/pages/9GO59w2TG2ISeQAwN0zx) — task structure.
* `AGENTS.md`, `CLAUDE.md` (root) — repo-wide write rules.

## Контекст

После закрытия Task 01 ясно из counter-таблицы, какие hooks мигрируются. Session-state — фундамент Task 03 и Task 04: без него миграция работает только частично.

## Подшаги

1. Спроектировать JSON schema. EN: Define schema fields — session\_id, started\_at, cwd, anchor\_reads (map of path → list of read events with turn\_id, ts, mtime\_at\_read), file\_changes (list), markers\_seen, applied\_criteria, skill\_invocations, skipped\_review\_count, turn\_id, last\_turn\_completed\_at.
2. Написать `session-state.py` CLI. EN: Implement Python CLI with subcommands read, write, append, gc. Use atomic file writes (write to temp + rename) for concurrent-safe access. Resolve session\_id from environment variable CLAUDE\_SESSION\_ID or from stdin payload field.
3. Написать reference schema. EN: Create `~/.claude/skills/1start-here/references/session-state-schema.md` documenting schema, writer protocol (who writes what), reader protocol, GC rules, example workflow.
4. Wire GC в SessionStart. EN: Modify `session-start.sh` to call `session-state.py gc` on each new session start. Remove sessions older than 14 days.
5. Smoke tests. EN: Write a small bash script that exercises — write event A, write event B, read and verify order, verify mtime preserved, run GC on a fake old session and verify removal.

## Готово

* [ ] CLI `~/.claude/skills/1start-here/scripts/session-state.py` работает.
* [ ] Schema reference создан и документирует все поля.
* [ ] GC запускается из `session-start.sh`.
* [ ] Smoke-tests проходят.
* [ ] Существующие hooks могут читать state (не модифицируя поведение).

## Красные линии

* [ ] Не добавлять >10 полей в schema.
* [ ] Не делать сложную мутацию — только append events + read latest by key.
* [ ] Не блокировать hooks при ошибках state (fail-open silently).

## Stop rule

Если CLI добавляет >100ms latency к hook firing — упростить или переоценить (возможно нужен binary cache вместо JSON, или per-key shard).

## Проверка

1. `python3 ~/.claude/skills/1start-here/scripts/session-state.py write --key anchor_reads --value '{"path":"x","turn_id":1,"mtime":123}'` Ожидаемо: запись в `~/.claude/state/session-{id}.json`.
2. `python3 ~/.claude/skills/1start-here/scripts/session-state.py read --key anchor_reads` Ожидаемо: возвращает записанное событие.
3. `time python3 ~/.claude/skills/1start-here/scripts/session-state.py read --key anchor_reads` Ожидаемо: real time < 100ms.

## Handoff

После закрытия → Task 03 (миграция hooks) использует CLI для проверки `skill_invocations` и `applied_criteria`. Task 04 (PreToolUse write-gate) использует `anchor_reads` для проверки prior Read.
