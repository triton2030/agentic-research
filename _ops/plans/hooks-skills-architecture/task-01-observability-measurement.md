# Task 01 — Логи срабатывания хуков

## Цель

Перевести ощущения о перегрузке hooks ("декоративно", "5 раз перечитал
documentation.md", "маркер ради маркера") в данные, на которых можно
принять решение per hook: оставить, мигрировать в skill, снять.

Это первая задача миграции hooks ↔ skills. Без данных следующие фазы
(session state, миграция, write-gate, усиление skills, canon-update)
работают на гипотезе, а не на ratio legit-catch vs decorative.

## Применимые критерии и инструкции

- [_ops/criteria/repo-structure-and-runtime-guards.md](../../criteria/repo-structure-and-runtime-guards.md) — UserPromptSubmit как light reminder, runtime guards rules.
- [_ops/criteria/skill-authoring.md](../../criteria/skill-authoring.md) — UserPromptSubmit лёгкое напоминание, `1work-review` проверяет факт применения после правок.
- [_ops/criteria/planning-surface-ownership.md](../../criteria/planning-surface-ownership.md) — task structure, `_ops/plans/**` только по явному запросу.
- [_ops/criteria/ops-findings-layer.md](../../criteria/ops-findings-layer.md) — где живут отчёты о находках.
- `AGENTS.md`, `CLAUDE.md` (root) — repo-wide write rules и task-level anchor правило.

## Контекст

План миграции: [/Users/triton/.claude/plans/snuggly-brewing-cascade.md](../../../../../.claude/plans/snuggly-brewing-cascade.md).

Текущие hooks (глобальные, `~/.claude/settings.json`):
- **SessionStart** → `~/.claude/skills/1start-here/scripts/session-start.sh` (инжектит ~1500 строк SKILL.md в каждую сессию).
- **UserPromptSubmit** → `~/.claude/skills/1start-here/scripts/prompt-submit-reminder.py` (intent-grounding directive + criteria reminder).
- **Stop** → `~/.claude/skills/1start-here/scripts/stop-work-review.py` (3-stage: work-review marker, user-truth marker для criteria, verbatim citation для anchor docs).

## Подшаги

1. Спроектировать формат event-лога.
   EN: Define JSONL schema: `{ts, session_id, turn_id, hook, decision, marker_seen, files_read, files_changed, anchor_reads, verbatim_quote_found, turn_outcome}`. One line per hook firing.

2. Собрать observability shim.
   EN: Wrap the three hook scripts so each firing appends one line to `~/.claude/state/hook-events.jsonl` before delegating to the original script. Behavior of hooks unchanged — only observability added.

3. Прогнать baseline через bare-prompt subagents.
   EN: Run 5-7 representative bare-prompt subagent tasks (criteria edit, code fix, conversational exchange, review request, multi-edit refactor, no-change discussion, sed bulk replace). Save transcripts under `~/.claude/state/baseline-runs/`.

4. Классифицировать срабатывания.
   EN: Tag each hook firing in the log: `decorative-marker` (marker without substance), `redundant-reread` (criteria already in session context), `paraphrase-instead-of-read` (anchor doc referenced without read), `legit-catch-of-skipped-review` (review would have been skipped without hook), `intent-grounding-useful` (helped first-turn disambiguation), `intent-grounding-decorative` (later turn).

5. Свести в counter-таблицу per hook.
   EN: For each hook compute: total firings, legit-catch %, decorative %, redundant %. Decision rule: `legit-catch <20%` → migrate-or-drop candidate, `>50%` → keep with conditional firing.

6. Записать находку через `1findings`.
   EN: Write classification + decision matrix to `_ops/findings/hook-firing-counters.md` using `1findings` skill (Evidence + Current tension + Owner gap format).

## Готово

- [ ] Shim прозрачно дописывает events в `~/.claude/state/hook-events.jsonl`, поведение текущих hooks не изменилось.
- [ ] 5+ типовых задач прогнаны bare-prompt subagent'ами, transcripts сохранены.
- [ ] Каждое событие классифицировано по таксономии failure-classes.
- [ ] Counter-таблица per hook записана в `_ops/findings/hook-firing-counters.md`.
- [ ] Decision per hook (keep / migrate / drop) принято на данных, не теоретически.

## Красные линии

- [ ] Не менять поведение hooks в этой фазе — shim только наблюдает.
- [ ] Не удалять и не снимать hooks до анализа данных.
- [ ] Не строить session-state в этой задаче (это Task 02) — текущий shim пишет в append-only лог.

## Stop rule

Если все три hooks показывают `legit-catch >70%` в реальных runs — гипотеза о
перегруженности неверна. Миграция останавливается. Через `1step-back`
переоценивается фрейм: возможно проблема была не в hooks, а в conversation
style или task type.

## Проверка

1. `jq 'select(.hook=="Stop")' ~/.claude/state/hook-events.jsonl | head`
   Ожидаемо: события Stop hook с классификацией, ts, session_id, turn_id.

2. `cat /Users/triton/Documents/GitHub/agentic-research/_ops/findings/hook-firing-counters.md`
   Ожидаемо: таблица per hook с legit/decorative/redundant ratios и decision.

3. Manual review одного baseline transcript:
   - Можно ли по логам восстановить, какие hooks стреляли и почему?
   - Совпадает ли классификация с реальным субъективным впечатлением "это было полезно / шумно"?

## Handoff

После закрытия задачи:
- Если decisions требуют session-state → Task 02 (session state design).
- Если все hooks помечены keep-as-is → миграция останавливается, остальные task-files этой папки архивируются.
- Если часть hooks migrate → Task 03 (per-hook migration) использует counter-таблицу как input.
