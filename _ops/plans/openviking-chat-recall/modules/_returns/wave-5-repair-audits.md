---
kind: module-return
wave: 5
state: repair-under-final-reverification
candidate: a1928822cbadfa43a298bb65c15c082fb080aa03
---

# Return — Wave 5 repair audits

## Candidate chain

`ae3bd56` → `581e85c` → `e74bbf0` → `a192882`.

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
Wiki. Это root-inspected state; независимый final semantic verdict ещё ожидается.

## Gate

G0 остаётся закрытым до terminal nested Luna Max acceptance по final candidate.
Writer self-report и локальный green test сами по себе gate не закрывают.
