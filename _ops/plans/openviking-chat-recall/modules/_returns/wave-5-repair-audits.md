---
kind: module-return
wave: 5
state: acceptance-harness-repair
candidate: f2ca3005bf6d70eb028c66a2e353c24344d3bf25
---

# Return — Wave 5 repair audits

## Candidate chain

`ae3bd56` → `581e85c` → `e74bbf0` → `a192882` → `5fd8f94` →
`f2ca300`.

Root clean-worktree run на `581e85c` дал 13/13 PASS, но две независимые
приёмки не приняли G0.

## Technical audit of 581e85c

PASS: exact experiment-only scope, stale-owned deletion, unrelated-file
survival, byte-identical regeneration, line/timestamp/record drift rejection и
отсутствие static nested-agent handles в receipts.

FAIL: generated-root marker мог пройти через symlinked ancestor и удалить
external sentinel. Repair `e74bbf0` добавил resolved containment и adversarial
test. Root run в настоящем detached Git clone на `a192882`: 14/14 PASS, включая
symlink sentinel.

## Semantic audit of 581e85c

PASS: stable-derived claim, facts-not-history boundary, scout/main-reader
boundary, historical evolution supersession и no-gold abstain mechanism.

Required corrections:

- `wiki-language-route`: `contested` не поддержан одной conditional pilot
  записью; статус должен быть `uncertain` и claim подавлен в default Wiki;
- prior subagent claim поддерживал discovery fan-out 20–30 files, но не summary,
  на которое main может опираться;
- no-gold absence нельзя расширять дальше checked frozen addresses.

Repair `a192882` применил все три ограничения и удалил language page из default
Wiki. Root затем обнаружил, что suppressed claim всё ещё назывался unsupported
title `Subagents should read and summarize source files`. Repair `5fd8f94`
заменил title на source-supported `Earlier broad subagent reading proposal` и
добавил falsifying test. Root run в настоящем detached clone: 14/14 PASS.

Nested acceptance затем доказал ещё один blocker: validator принимал
`contested` по одному source record. Repair `f2ca300` требует минимум два
distinct in-bundle `conflict_source_record_ids`, отклоняет missing, dangling и
out-of-claim IDs и явно оставляет semantic opposition во внешнем audit.
Root worktree и clean detached clone: 16/16 PASS; исходная one-sided mutation
получает `ProbeError`. Независимый follow-up подтвердил prior FAIL закрытым.

Blind holder arm `01a02587-f16a-7a82-9fd7-c75281594395` и Wiki arm
`01a02587-f765-7ae3-8382-7d64283388ed` запустили nested Luna Max readers и
вернули пять packets каждый. Independent matched grader не принял G0: общий
five-case session нарушил per-case budgets/reporting, а v1 не разделил
arm-specific expectations. Verdict —
[wave-5-matched-grader](wave-5-matched-grader.md).

## Gate

G0 остаётся закрытым до case-isolated matched rerun по operational amendment,
не меняющей frozen semantic criteria. Writer self-report, локальный green test
и safe abstention сами по себе gate не закрывают.
