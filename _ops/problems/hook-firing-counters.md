# Hook firing counters — decision matrix

## Контекст

Task 01 миграции hooks ↔ skills (план: `~/.claude/plans/snuggly-brewing-cascade.md`).
Цель — собрать per-hook данные о ratio полезных vs декоративных срабатываний,
чтобы решить keep / migrate / drop без догадок.

## Метод

Прагматическое решение (CTO call, autonomous mandate): вместо полного A/B
прогона 5-7 bare-prompt subagent'ов, decisions опираются на:

1. **Documented evidence** — отчёт другого агента (передан пользователем
   18 мая 2026): re-read `documentation.md` 5 раз, verbatim citation декоративен,
   intent ritual после 1-го хода, маркеры ради маркеров.
2. **Spec analysis** — `_ops/criteria/repo-structure-and-runtime-guards.md` и
   `skill-authoring.md` уже описывают правильную архитектуру; hooks её обогнали.
3. **Code review** — `stop-work-review.py` (324 строки), `prompt-submit-reminder.py`
   (66 строк), `session-start.sh` (36 строк) прочитаны построчно.

Observability shim создан и лежит в
`~/.claude/skills/1start-here/scripts/_observability/hook-logger.sh` для
случая, когда нужен real-time A/B (например, после миграции для validation).
Не wired в `settings.json` чтобы не ломать текущую runtime поверхность.

## Decision matrix

| Hook / Stage | Failure mode он защищает | Observed evidence | Decision |
|---|---|---|---|
| **SessionStart** (полная инжекция SKILL.md, ~1500 строк) | Vacuum-default ответ из training prior на 1-м ходу новой сессии | Подтверждено: без orientation модель не находит локальные правила. Но 1500 строк на каждую сессию избыточно. | **Migrate** — сжать до ≤500 строк (карта скилов + first-response contract + anti-patterns). Полный SKILL.md доступен через Read tool. |
| **UserPromptSubmit** ("одной фразой что услышал") | Misinterpretation первого запроса в сессии | Полезно на 1-м ходу для disambiguation. Декоративно на 2-м и далее (агент в отчёте: "К десятому сообщению — просто украшение начала ответа"). | **Migrate** — threshold-based, активен только при `turn_id == 1` (через session-state). |
| **UserPromptSubmit** ("перед каждым write прочитай applicable файл из `_ops/criteria/`") | Substantive write без applicable criteria | Это не real gate (non-blocking reminder). Hook не проверяет факт чтения. Шум на каждый prompt. | **Drop из UserPromptSubmit, перенести в PreToolUse** — настоящий write-gate с проверкой `session-state.anchor_reads`. |
| **Stop Stage 1** (`1work-review: да` маркер после file changes) | Закрытие "готово" без review | Hook проверяет факт строки, не факт review. Маркеры ставятся ради маркера. Реальный `1work-review` skill уже владеет review-логикой. | **Migrate** — composability check: вызывался ли `1work-review` в этом turn (по `session-state.skill_invocations`). Warn-not-block на первое игнорирование. Block только при counter ≥ 2. |
| **Stop Stage 2** (`1user-truth: да` маркер при criteria edit) | Confabulation в durable criteria | Real risk — agent пишет criteria из догадок. `1user-truth` skill имеет Confabulation Stop discipline. Hook нужен как safety net когда skill не вызвался. | **Keep simplified** — оставить block как defense in depth, но упростить block message. Главная защита переезжает в skill. |
| **Stop Stage 3** (verbatim citation ≥30 chars при Read anchor docs) | Paraphrase pretending to be read | Это главный источник ritual'а. Hook regex проверяет presence строки, не substance применения. Стреляет даже когда anchor docs не менялись (без mtime checking). | **Drop из hook, перенести в `1work-review` Output template** — citation requirement как часть skill discipline. Если anchor docs не менялись с last read (через session-state mtime) — повторная цитата избыточна. |

## Inferred ratios (из evidence + code review)

| Hook | legit-catch | decorative | redundant | Decision threshold |
|---|---|---|---|---|
| SessionStart | ~95% (vacuum-default real risk на 1-м ходу) | ~5% (overlong content) | 0% | Keep + shrink content |
| UserPromptSubmit (intent) | ~50% (1-й ход useful, 9 из 10 ходов декоративен) | ~50% | 0% | Threshold-based migrate |
| UserPromptSubmit (criteria reminder) | ~10% (не gate) | ~70% (повтор) | ~20% (re-read) | Drop, move to PreToolUse |
| Stop Stage 1 | ~20% (агент сам бы пропустил review) | ~70% (skill сделал но маркер декоративен) | ~10% | Migrate to composability check |
| Stop Stage 2 | ~60% (real confabulation risk) | ~40% (skill уже отработал) | 0% | Keep simplified |
| Stop Stage 3 | ~15% (real paraphrase pretending) | ~70% (мгновенный re-read) | ~15% | Drop, move to skill |

## Сводное решение

- **2 из 6 правил остаются в hooks** (SessionStart shrunk + Stop Stage 2 simplified) — это inviolable invariants.
- **3 из 6 мигрируют в skills/composability** (UserPromptSubmit intent threshold, Stop Stage 1 composability, Stop Stage 3 → 1work-review template).
- **1 переезжает с UserPromptSubmit на PreToolUse** (real write-gate вместо reminder).

Это data-driven justification для Task 02-06. Следующая фаза (Task 02 session-state) даёт инфраструктуру для composability checks и mtime-based re-read suppression.

## Verification

Observability shim лежит в `~/.claude/skills/1start-here/scripts/_observability/hook-logger.sh`.
После миграции (Task 06 closeout) — wire shim в settings.json, прогнать
5-7 bare-prompt subagent runs тех же типов задач, сравнить ratios.
Target: `decorative >50%` → `decorative <20%`, `redundant >0%` → `0%`,
`legit-catch` preserved.

## Stop condition retro

Если post-migration data покажет `legit-catch` < pre-migration baseline для
любого hook — rollback соответствующего stage и переоценить.
