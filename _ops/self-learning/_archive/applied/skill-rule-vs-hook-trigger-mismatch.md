# Skill Rule Vs Hook Trigger Mismatch

## Observation

Skill body articulates rule с явным scope («triggers только на sensitive
surface X, Y, Z»), но Stop hook fires на более широком scope (any
substantive write accumulated). Модель следует skill rule literally,
hook ловит как violation. Конфликт между **skill-level discipline** и
**hook-level structural enforcement** — оба правильные по своей логике,
но не aligned.

Pattern: **rule-hook scope drift**. Skill rule пытается быть точным
(«review только на sensitive surface»), а hook грубее («≥3 files OR
sensitive»). Модель использует skill rule как guide → пропускает review
для non-sensitive writes → hook triggers.

Это особенно скользко после **autonomous-write conventions** (1self-learning,
1findings): skill explicitly говорит «без спроса, прямо находу», но
каждый такой write добавляется в hook accumulated counter. Cumulative
count перешагивает порог даже на legitimate autonomous writes.

## Counter

- 2026-05-21 [Claude Opus 4.7]: после `1work-review: да` маркера сделал
  Write нового self-learning файла (`edit-gate-requires-read-tool.md`).
  Per just-promoted 1work-review rule «review до next substantive action
  на sensitive surface (_ops/criteria/, GOAL, ROADMAP, AGENTS, CLAUDE,
  ~/.claude/)» — `_ops/self-learning/` не в списке, review не нужен.
  Но Stop hook сработал на «второй ход подряд с substantive write без
  review». Pattern ironic — fired immediately после rule expansion.

## Possible upgrade

Два пути выровнять:

1. **Расширить sensitive list в 1work-review rule** — добавить
   `_ops/self-learning/` (или `_ops/` целиком). Минус: review-trigger
   becomes broader, конфликтует с «autonomous-write без overhead» духом
   self-learning/findings.

2. **Сузить hook trigger** — Stop hook должен исключать `_ops/self-learning/`
   и `_ops/findings/` из accumulated counter, потому что эти surfaces
   explicitly autonomous-write per их skill bodies. Hook owns sensitive
   list синхронно с skill rule.

3. **Документировать exception в skill** — добавить в 1work-review note:
   «autonomous-write surfaces (`_ops/self-learning/`, `_ops/findings/`)
   exempt от review-trigger; их handoff line — sufficient closure».

Третий путь — наименее infrastructure-heavy. Skill body документирует
exception, hook остаётся как есть (false-positive trigger, но rare).

Связано с `optional-instruction-skip.md` (skill rule + hook trigger
divergence), но fokus другой: тут не tone, а **scope alignment** между
skill rule и hook enforcement.
