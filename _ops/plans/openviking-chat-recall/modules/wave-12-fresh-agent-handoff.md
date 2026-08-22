---
kind: module-card
wave: 12
state: planned
role: fresh-agent-route-and-completion-auditor
system-owner: root
fresh-reader-model: gpt-5.6-luna
fresh-reader-thinking: max
completion-auditor: claude-opus-5
---

# Модуль — fresh-agent route, rebuild handoff и completion audit

[parent: task.md](../task.md) · веха 5 · gate: Wave 11 verdict

## Contribution

Превратить accepted или rejected experiment в честный рабочий маршрут для
следующей чистой сессии и проверить весь заявленный done-state по evidence.

## Route contract

- Текущее дистиллированное знание: L0 → L1 → нужные L2 pages.
- Exact words, recurrence count, first/latest и chronology: immutable holders.
- Provenance: source-quote addresses в L2 плюс полный holder/later-check route.
- Упомянутые в Wiki project files не являются knowledge source и не открываются
  без отдельного текущего project-canon вопроса.
- No-gold, unresolved conflict или неполная coverage: abstain/UNKNOWN.
- Если Wave 11 FAIL, holders остаются default; Wiki помечается rejected/candidate
  с сохранённым evidence, а не продвигается молча.

## Ownership

- Один handoff writer пишет короткую agent route и exact rebuild/runbook в
  experiment-owned docs; он не меняет global skill или root instruction.
- Fresh Luna Max agent в clean session выполняет locked tasks только по handoff.
- Независимый Opus completion auditor read-only раскладывает все критерии task.md на
  PASS/FAIL/UNKNOWN и не исправляет результат.
- Root один обновляет task/status, observations и final verdict после returns.

Root отдельно запускает bounded navigation и rebuild recovery probes; их
self-report не заменяет Opus acceptance matrix.

## Fresh-session checks

- новый agent без истории находит current knowledge через L0/L1/L2;
- на exact/history вопрос сам маршрутизируется к holder, а не пересказывает Wiki;
- не использует project corpus для дополнения ответа на вопрос о remembered
  owner knowledge и не возвращает superseded Wiki content;
- rebuild из frozen commit выполняется одной записанной командой и совпадает с
  accepted digests/declared semantic nondeterminism;
- сломанный digest, missing provider gate или unresolved claim fail closed;
- agent может назвать source route и границу того, чего Wiki не доказывает.

## Completion gate

Done допустимо только когда:

- все пять milestones task.md имеют direct evidence;
- full snapshot coverage exhaustive;
- accepted route прошёл matched blind comparator и fresh-session test;
- private source leakage, destructive cleanup и secret risks закрыты;
- каждый material criterion имеет PASS, hard FAIL отсутствует, material UNKNOWN
  отсутствует.

## Return

Handoff writer: commit SHA, exact route/runbook paths и validation. Fresh agent:
task answers, reads/tokens/time/sources/gaps. Auditor: atomic acceptance matrix и
blockers. Root публикует итог, оставшиеся риски и observation candidates для
будущего reusable converter.

## Prohibitions

Не объявлять full Wiki готовой по plan, writer report, existence artifacts или
узкому sample; не расширять experiment до global tool без отдельного решения.
