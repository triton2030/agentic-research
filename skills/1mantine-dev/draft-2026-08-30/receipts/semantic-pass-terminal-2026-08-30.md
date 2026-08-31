# Terminal receipt — semantic pass 2026-08-30

## Статус

`TERMINAL_BLOCKER`: текущий candidate семантически ведёт к Mantine public-first
решению, но strict exact approval остановлен budget- и routing-находками. Ничего
не устанавливалось; official/live packages не менялись.

## Точный candidate

Проверенный runtime-пакет состоит ровно из `SKILL.md` и двух references:

| Файл | SHA-256 |
| --- | --- |
| `SKILL.md` | `606a0f1642921a131d2637579673d0b8ad6b6cfa051acfed8639bbc1ac7bdc8e` |
| `references/audit.md` | `13888088edea825e6d059daecea3538c9dc9e541d5a1a947e5775058b3099574` |
| `references/last-year.md` | `076413cfb3406b39ffe906daa4f2b276dabb0940c1d5d3cbc496017ffaba0ba5` |

Aggregate hash (sorted relative path + NUL + bytes + NUL):
`ded2627360a6ad97f4bb574f29d8344520474215551c2a4bdf516ccf40e3fb0c`.

Изменённый runtime scope: `SKILL.md`, `references/audit.md`,
`references/last-year.md`. Предыдущие frozen hashes этого прохода:
`8a1ff7e5d455ab500515314492f90e97660d08bca409d6860cd721cada7497f1` и
`559d30780673f885f69a5eecbce1423c881cdb307e652b3166b0621d1277dcec`.

## Exact checks

- Independent literal checker: **FAIL**, единственная budget-находка — карта
  `map.md:15-25` не отражает буквальный пересчёт. Наблюдаемые единицы:
  `SKILL.md 19`, `references/audit.md 22`, `references/last-year.md 22`;
  active sets: `core 19`, `version gate 41`, `audit gate 41`. Это превышает
  лимит 20 при одновременном body + выбранном reference. Остальные проверки
  прошли: trigger-only English description, Russian body/references,
  `cohort: unknown`, task/cohort handoff, literal audit behaviors, internal
  links и official URL HTTP 200, no runtime authoring/check route.
- Independent trajectory checker: **semantic PASS / strict UNKNOWN**. Сохраняются
  core + два conditional gates и нет procedural bureaucracy, но не доказаны
  official-docs/types lookup на обычном core-пути и strict per-unit harm map;
  external projection parity в этом окне не переисследовалась.
- `qv-skill skills/1mantine-dev/draft-2026-08-30`: pass.
- `md check --paths skills/1mantine-dev --json`: 19 targets, 0 issues.
- `git diff --check -- skills/1mantine-dev`: pass.
- `python3 skills/shared/sync_simple_projections.py 1skill-creation --check`:
  pass; effective baseline fingerprint остаётся
  `9bf11f64b436d313d979cba822b684f502e8e40e5f15a12f78cbd914ca29a518`.
- Current live parity read-only check: Codex and Claude
  `/Users/triton/.codex/skills/1mantine-dev/SKILL.md` и
  `/Users/triton/.claude/skills/1mantine-dev/SKILL.md` обе имеют hash
  `91354c6f5ad37ce14b5459e12cbf27d653c01e7b1bea681ab024931ceec8da54`.

## Смысловой delta

Удалены или поглощены `window`/`confirmation`, повторные scope/candidates/
decision таблицы и authoring/check ceremony; runtime оставлен как intent,
cohort stop и два условных gate. Оставшаяся сложность оправдана двумя
конкретными вредами: stale/чужой-major API и незамеченная official capability
или custom residue. Но буквальный active-set счёт показывает, что даже эта
форма пока не укладывается в 20 одновременно применимых единиц.

## Gaps и needs

1. **Budget:** нужно семантически убрать или поглотить обязательства до
   `active set <=20`; одни числа в `map.md` менять нельзя.
2. **Routing:** в `SKILL.md:22` явно закрепить `last-year.md` перед `audit.md`,
   если version uncertainty и review встречаются вместе.
3. **Official source:** обычный core должен требовать current official Mantine
   docs, сверенные с installed public API, иначе stale same-major handle может
   быть выбран из памяти.
4. **Map evidence:** после следующего candidate пересчитать map и привязать
   harm к сохранённым rule families; старые `reviews-terminal.md` и receipts
   остаются историческим evidence, не closure для этого hash.

Needs: новый bounded semantic repair и ещё один exact two-check cycle; install
остаётся запрещён до exact approval владельца.
