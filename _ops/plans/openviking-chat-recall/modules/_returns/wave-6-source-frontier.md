---
kind: module-return
wave: 6
stage: source-frontier
state: accepted
date: 2026-08-22
---

# Wave 6 — source frontier

## До фиксации

Read-only Luna Max task `01a025bb-e6d4-7c00-94ce-bafd7bb932e1` сравнил
committed `b68b5a2` и current working tree:

| Surface | Holder files | Holders with records | Parsed records | Diagnostics |
| --- | ---: | ---: | ---: | ---: |
| `b68b5a2` | 180 | 179 | 1075 | 33 |
| working tree | 184 | 183 | 1101 | 34 |

Восемь dirty holder paths давали четыре новых files и 26 parsed records.
Проверка 280 локальных commits не нашла commit, byte-matching всему current
corpus; silent `HEAD` fallback был отклонён.

## Принятый snapshot

Root сохранил ровно восемь overlays без редактирования их текста:

- `_ops/chat-recall/2026-08-19-212344-codex-01a01ad4.md`;
- `_ops/chat-recall/2026-08-20-222653-claude-93d2bd06.md`;
- `_ops/chat-recall/2026-08-20-224022-claude-1bc0a881.md`;
- `_ops/chat-recall/2026-08-20-235300-codex-01a02084.md`;
- `_ops/chat-recall/2026-08-20-222728-claude-6a83ff1b.md`;
- `_ops/chat-recall/2026-08-20-222832-codex-01a02036.md`;
- `_ops/chat-recall/2026-08-21-145843-codex-01a023c1.md`;
- `_ops/chat-recall/2026-08-21-150905-codex-01a023c2.md`.

Explicit corpus commit:
`6f98fcccdbf4b4de45ef787239ad101f70d106e2`.

После commit `_ops/chat-recall` clean; denominator — 184 holder files и 1101
parsed records. `--check` завершился exit 0 с 34 diagnostics:
29 `duplicate-session-holder`, 4 `unmarked-approximate`, 1 `invalid-type`.
Последний адрес —
`2026-08-20-222832-codex-01a02036.md:29` / `cr-d12f653a005202ee`.

## Решение

Diagnostics не удаляются и не ремонтируются в source snapshot. F1/F2 должны
зафиксировать их адреса и дать каждому record явный `used`, `rejected` или
`skipped` disposition с причиной. Так сохраняется полный corpus и не выдаётся
структурно сомнительная запись за accepted knowledge.

## Независимая проверка

Nested Luna Max denominator checker не вернулся после трёх bounded waits;
terminal status — `UNKNOWN`. Его self-report не использован. Root повторно
проверил scoped cleanliness, commit SHA, holder count и parser denominator.
