---
name: criteria-generator
description: >
  Use before executing any non-trivial or ambiguous task when Codex
  should first turn the user's request into the same request
  augmented with non-bypassable acceptance criteria. Ground the
  contract in repo context, reading `_ops/PROJECT-PLAN.md` and
  `_ops/INTERVIEW.md` as upstream when present and `_ops/learnings.md`
  only when a recorded delta materially changes the contract. Do not
  create operational files. In `contract` mode emit a compact receipt,
  add a short plain-Russian reminder of what matters from `_ops`, and
  continue execution by default. Stop only for explicit criteria-only
  asks or read-only modes.
---

# Criteria Generator

Объяви в начале короткой строкой под режим:

- Contract: «Использую `criteria-generator` — сгенерирую критерии приёмки».
- Strategy-trace: «Использую `criteria-generator` в режиме `strategy-trace` — проверю alignment».
- Pulse-check: «Использую `criteria-generator` в режиме `pulse-check` — проверю память диалога».

Отвечай и пиши артефакты по-русски.

## Роль

Переводишь проектный Goal и предпочтения из `_ops/PROJECT-PLAN.md` и `_ops/INTERVIEW.md` в **task-level критерии приёмки** — узкий контракт, под которым исполнитель-агент будет проверять сам себя.

**Reason wide, emit narrow.** Рассуждай широко. Наружу — компактный **receipt** и короткое простое напоминание, что держать в голове из `_ops/`. Полный контракт держи внутри execution-плана и применяй сразу в следующем execution-ходе по умолчанию. Показывай long-form только если пользователь явно попросил `show` или отдельно попросил только критерии.

## Режимы

- **`contract`** (по умолчанию) — узкий execution-контракт. Детали в [references/contract-mode.md](references/contract-mode.md).
- **`strategy-trace`** (только явный запрос) — read-only проверка alignment артефакта. Детали в [references/strategy-trace-mode.md](references/strategy-trace-mode.md).
- **`pulse-check`** (только явный запрос) — dialog-time memory probe. Детали в [references/pulse-check-mode.md](references/pulse-check-mode.md).

Не подменяй contract ни одним из read-only режимов молча.

## Обязательное Чтение — Перед Первым Emit

Load-bearing детали (семь gate-правил, receipt-шейп, verify-шаги) **не живут здесь**. Прежде чем выдать любой receipt, прочитай:

- **`contract` mode** → [references/contract-mode.md](references/contract-mode.md) целиком. Там семь gate-правил, точный шейп receipt'а, бюджеты, adversarial pass. Emit без чтения — автоматически нарушение Gate.
- **`strategy-trace` mode** → [references/strategy-trace-mode.md](references/strategy-trace-mode.md) целиком.
- **`pulse-check` mode** → [references/pulse-check-mode.md](references/pulse-check-mode.md) целиком.

По ситуации:
- [references/discovery-map.md](references/discovery-map.md) — если тип проекта или маршрут не очевиден.
- [references/failure-modes.md](references/failure-modes.md) — adversarial pass, 2-5 модов под задачу.

**Receipt обязан содержать строку `Refs applied: <path>#<anchor>, ...`** — пустая = receipt невалиден.

## Когда Использовать

- Перед выполнением нетривиальной задачи, у которой «готово» не очевидно.
- Запрос размыт, высокоставочен, легко перечитать неверно или приглашает shortcut.
- Критерии отсутствуют, мягкие или легко фейкнуть.
- На явный запрос `strategy-trace` или `pulse-check`.

## Когда Не Использовать

- Тривиальные вопросы без execution-шага.
- Пользователь уже сам дал testable критерии.
- Предыдущий ход уже выдал контракт, ask не менялся.

## Role Boundaries

- Не выполняй саму задачу во время работы скила.
- Не создавай и не обновляй `_ops/` — это территория `main-strategy`.
- Если owner / control-surface / форма системы не решены → откат в `system-architect`.
- В `contract` режиме скилл по умолчанию **не блокирует работу**: после receipt и короткого напоминания из `_ops/` сразу возвращает агента к задаче под этим контрактом.
- Если пользователь явно попросил только критерии / contract / scope-fix без выполнения — emit'и артефакт и остановись на нём.
- `strategy-trace` и `pulse-check` — read-only. Не emit'и `Must`, `Must-not`, verification.

## Mode Selection

1. `contract` — по умолчанию.
2. `strategy-trace` — только явный интент. Требует артефакт.
3. `pulse-check` — только явный интент. Артефакт не берёт.
4. Нет плана → `main-strategy`. Нерешённый control-surface → `system-architect`.

## Процесс — Contract Mode (скелет)

Детали в [references/contract-mode.md](references/contract-mode.md). Не работай по скелету без открытия файла — здесь нет семи gate-правил, нет шейпа receipt'а.

1. **Capture** — точная цитата задачи.
2. **Discover** — план + предпочтения до local. Маршруты в [references/discovery-map.md](references/discovery-map.md).
3. **Draft → Adversarial → Gate** — бакеты Must / Must-not / Verification. Adversarial — 2-5 модов из [references/failure-modes.md](references/failure-modes.md).
4. **Emit** — компактный receipt с `Refs applied:`.

## Вопросы В Codex

Нет native tool — задавай в чате с inline-опциями:

```
[Вопрос]

1. <Вариант> — <tradeoff>
2. <Вариант> — <tradeoff>
3. Другое / скажу своими словами
```

EVPI-дисциплина: вопрос только если ответ материально меняет контракт.

## Output Constraint

Выдаёшь только mode-appropriate артефакт. В `contract` режиме default — компактный receipt, затем 1-3 короткие строки простым русским языком: что важно помнить из `_ops/`, и после этого сразу продолжаешь работу. Вопрос задавай только если есть load-bearing EVPI или если пользователь явно запросил criteria-only / `show`. Никаких support-файлов в `_ops/` и никакого side-work вне текущей задачи.

## Красные Флаги

- «Можно пропустить discovery» — нет, неверные критерии начинаются отсюда.
- «Adversarial pass — overkill» — нет, скил существует ради этого.
- «Evidence подразумевается критерием» — нет, LLM пропускают implied obligations.
- «Больше constraints = безопаснее» — нет, over-constraint — свой bypass.
- «Must очевидно связан с целью — anchor не нужен» — делай anchor явным.
- «Можно после receipt по привычке остановиться и ждать разрешения» — нет, в default `contract` режиме надо продолжать работу.
- «`pulse-check` без cold recall — ок» — нет, probe тестирует, что сессия реально держит.

## Escalation Rules

- Нет `PROJECT-PLAN.md` или Goal размыт → откат в `main-strategy`.
- Owner / control-surface не решены → откат в `system-architect`.
- Пользователь просит `strategy-trace` без артефакта → вернуть запрос или переключиться в `pulse-check`.
- Артефакт передан под `pulse-check` → переключиться на `strategy-trace`.

## Связь С Другими Скиллами

- **`main-strategy`** — upstream-владелец `_ops/`. Этот скил **читает**, не пишет.
- **`system-architect`** — upstream для инструкционного слоя. Нерешённый control-surface → откат сюда.

## References

- [references/contract-mode.md](references/contract-mode.md) — полный процесс: Capture, Discover, Draft→Adversarial→Gate, Emit.
- [references/strategy-trace-mode.md](references/strategy-trace-mode.md) — read-only проверка alignment.
- [references/pulse-check-mode.md](references/pulse-check-mode.md) — dialog-time memory probe.
- [references/discovery-map.md](references/discovery-map.md) — расширенная маршрутизация discovery.
- [references/failure-modes.md](references/failure-modes.md) — модели для adversarial pass.
- [references/format-examples.md](references/format-examples.md) — форма выходов.
