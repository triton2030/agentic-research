---
name: 1instruction-layer
description: >
  Use when durable `AGENTS.md`, `CLAUDE.md` or path rules need writing/audit:
  effective chain, owner, scope, wording. One-off→prompt;
  shape→`1ia-audit`; graph→`1md-graph`.
---

# Слой Инструкций

## Результат И Режим

Оставь минимальную instruction delta, которая понятна cold-start модели, живёт у
правильного owner-а и не конкурирует с effective instruction chain.

- **Audit/review/diagnose:** findings, evidence и exact proposed repair без edits.
- **Change/fix:** scoped repair и проверка изменённого контракта.

Instruction prose направляет выбор, но не является enforcement. Дорогой или
необратимый invariant должен опираться на permission, hook, validator, test или
approval у runtime owner-а.

## Default Path

1. **Durability + surface.** Одноразовое условие оставь в prompt/thread. В
   durable layer поднимай стабильный local fact, recurring correction/failure
   или hard invariant. Если ещё выбирается text vs skill/agent/hook/config,
   передай surface decision в `1skill-architect`.
2. **Effective chain.** Прочитай реально загружаемые global → root → relevant
   subtree instructions и живых owners. Не выводи chain из имени файла или
   привычки другого runtime.
3. **Owner + class.** Назови effective winner при конфликте и выбери один owner:
   global, root, subtree/path-scoped, inline pointer или существующий owner link.
   Классифицируй delta как `local fact / owner pointer`, `behavioral rule` или
   `hard invariant`; нет устойчивой дельты → delete no-op/sediment.
4. **Один repair.** `keep`, `delete`, `narrow scope`, `move to owner`, `replace
   with pointer`, `rewrite exact wording` или `handoff to enforcement`.
   Procedure добавляй только когда order, lifecycle moment, completeness или
   хрупкость сами являются контрактом.
5. **Exact wording + proof.** Сделай наблюдаемыми только значимые scope/moment,
   outcome, owner/source, exception/escalation, evidence и stop. В audit mode
   покажи exact proposed text/delete/move; в change mode проверь direct
   read/diff, effective chain и smallest project-owned evidence.

## Conditional References

- Claude Code loading, imports, path rules или skill metadata спорны →
  [`references/claude-discovery.md`](references/claude-discovery.md).
- Root/subtree topology, duplicate или placement требуют deep audit →
  [`references/audit-placement-structure.md`](references/audit-placement-structure.md).
- Нужно извлечь load-bearing meaning и success criteria зоны или спроектировать
  root/subtree instruction и её routing от representative future cold-start задач →
  [`references/audit-meaning-criteria.md`](references/audit-meaning-criteria.md).
- Literal scope, Hyrum, frame capture или wording quality спорны →
  [`references/language-quality-audit.md`](references/language-quality-audit.md).
- Наблюдается named model-specific failure → релевантная запись в
  [`references/llm-divergences.md`](references/llm-divergences.md).
- Repair требует evidence beyond прочитанных instruction files →
  [`references/cli-recipes.md`](references/cli-recipes.md).

## Boundaries

- split/merge/move/new instruction container → `1ia-audit`;
- `depends-on`, holders, anchors, cycles, broken links → `1md-graph`;
- skill/agent/hook selection, trigger/collision → `1skill-architect`;
- project scope/done/stop → `1goal`; task contract → `1planning`;
- permissions/hooks/settings/enforcement → live runtime owner.

## Вывод И Стоп

```text
Mode + durability: <audit|change; one-off|durable>
Effective chain + owner: <loaded sources, precedence, chosen owner>
Class + evidence: <fact|rule|invariant; observed delta>
Repair + exact wording: <proposed or applied instruction delta>
Validation + risk: <smallest proof; only unresolved risk>
```

Готово, когда effective chain и owner подтверждены, exact repair соответствует
mode, соседние owners не конкурируют, а validation доказывает изменённый слой.
Остановись до edits, container/graph/runtime mutation или внешней записи, если
текущий intent их не разрешает.
