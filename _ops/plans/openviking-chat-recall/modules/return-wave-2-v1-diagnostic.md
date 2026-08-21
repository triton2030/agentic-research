---
kind: module-return
волна: 2
variant: diagnostic-v1
состояние: failed
записано: 2026-08-21
---

# Return — diagnostic Wiki v1

## Scope

Две blind Luna Max руки получили только exact locked вопросы 9 и 11. Wiki arm
видел только семь diagnostic pages; source arm — selection и доступные holders.
Plan, gold, receipt, Graphiti и ответы другой руки им не показывались.

Threads:

- Wiki: `01a023e9-f36e-7471-86f5-d9ae99828de2`, 139.6 секунды.
- Source: `01a023e9-f36c-71c1-b216-f5fb84e1310e`, 149.1 секунды.

Обе руки превысили заданные 120 секунд, поэтому efficiency verdict неизвестен.

## Question 9 — OpenViking outcome

Source arm ответил `current`: превратить повторяющиеся цитаты в долгосрочную
библиотеку документов по OpenViking; статический старый архив, derived Wiki,
неизменяемые holders, pilot до full backfill. Evidence —
`_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.

Wiki arm после шести page reads ответил `historical`: улучшить retrieval script,
обогнать shell search, сохранить лёгкость и использовать session-context только
как route. Он прямо признал gap: Wiki не предъявила строку, что выбран OpenViking
или что это текущая политика.

Verdict: Wiki v1 не нашла текущий outcome, присутствующий в pilot source, и
подменила его старой задачей. Hard failure.

## Question 11 — no-gold control

Обе руки дали `abstain`: exact stock system prompt и русская compile config не
были выбраны владельцем в разрешённых evidence. Calibration pass.

## Structural check

- 7 Markdown pages, 70 `viking://` source-link occurrences.
- Pages используют слова `recurring`, `repeated`, `earliest`, но ни одна не
  сообщает exact count distinct source records вместе с earliest/latest/current.
- Отдельной страницы про OpenViking knowledge-library outcome нет.

## Coverage caveat

Clean source-arm worktree не содержал untracked holder
`2026-08-20-222832-codex-01a02036.md`, хотя он входит в frozen inventory writer-а.
Для вопросов 9 и 11 это не меняет gold, но не позволяет расширять verdict на
другие вопросы или весь corpus.

## Causal limit

V1 не проверил exact approved compile reason. Runtime request требовал лишь
`cover recurrence/change`, тогда как plan требовал операцию: count distinct
records, earliest/latest, current formulation и contradictions. Поэтому v1
доказывает дефект текущего output, но ещё не предел OpenViking. Writer получил
узкий v2 rerun с exact reason, тем же corpus и отдельным target.
