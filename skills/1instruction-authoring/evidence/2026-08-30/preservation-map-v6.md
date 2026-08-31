# Карта сохранения и простоты `candidate-v6`

## Граница

- Baseline: полный read-only пакет
  `skills/shared/1instruction-authoring/portable/**`, 10 файлов.
- Candidate: `../../versions/v6/**`, 4 файла.
- Owner correction: `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:33`.
- Official owner, projections и live не изменяются до unconditional exact approval.

## Сохранённая функция

| Baseline-функция | Адрес `candidate-v6` | Как сохранена |
| --- | --- | --- |
| Межзонная правда достигает первого зависимого решения | `SKILL.md:8-18` | Стала commander intent вместо отдельного intent-протокола. |
| Допустим локальный невыводимый hard line | `SKILL.md:16-18,31-33` | Не требует выдумывать внешнего владельца. |
| Один смысл имеет одного владельца | `SKILL.md:16-18,29-30` | Изменяемая правда остаётся у канонического владельца; instruction только маршрутизирует. |
| `no-change` требует доказательства, неизвестное не становится правилом | `SKILL.md:22-28` | Реальный путь, а не текст/ссылка/самоотчёт, и независимый clean scout заменяют admission-бюрократию. |
| Узкая своевременная поверхность вместо общего preload | `SKILL.md:29-30` | Placement-table удалена; граница решения сохранена. |
| Сначала цель/контекст, затем только невыводимые hard lines | `SKILL.md:31-33` | Межзонные связи, CLI/API/schema, safety/authority, critical order и falsifying acceptance сохранены одним allowlist. |
| Полные однозначные формулировки | `SKILL.md:33` | Wording-режим поглощён одной наблюдаемой границей. |
| Active-path budget не режет функцию и не маскируется файлами | `references/verification.md:18-20` | Проверяется на реальном пути; механическое дробление прямо запрещено. |
| Причинная matched pair и прямое evidence | `references/verification.md:21-26` | Изолированные деревья, blind target/skip/alternative trial и observable trace сохранены. |
| Negative, lawful alternative и long-trajectory falsifiers | `references/verification.md:21-29` | Вред соседнему пути и непроверенное удержание не получают `pass`. |
| Exact approval, tracked owner first, only existing projections/live, parity | `references/verification.md:30-33` | Authority и runtime schema сохранены в единственной проверочной стадии. |
| Независимый поиск владельцев и внешних потребителей | `agents/zone-scout.md:7-33` | Сохранены bounded input, отсутствие подсказанного ребра, coverage, stop и read-only boundary. |
| Codex runtime metadata | `platforms/codex/agents/openai.yaml` | Сохранены display name, trigger-only short description, default prompt и implicit policy. |

## Что удалено или поглощено

- `intent.md`, `placement.md`, `assembly.md` и `wording.md` удалены как runtime
  стадии: их результат выводится из commander intent и пяти границ решений в
  `SKILL.md`.
- `budget.md`, `probe.md` и `finish.md` поглощены одним
  `references/verification.md`: это один post-candidate момент, а не три продукта
  пользователя.
- `zones.md` удалён как orchestration bureaucracy; условие разведки осталось в
  root, а самостоятельный clean scout содержит только невыводимую delta роли.
- Перечни поверхностей, слов-заполнителей, файлов поиска и промежуточных status
  artifacts удалены: компетентный агент выводит их из цели и текущего проекта.
- Пяти- и восьмистадийные candidate-версии оставлены только как history evidence;
  их дробление не является runtime-решением active-load проблемы.

## Оставшаяся сложность и counterfactual harm

| Остаток | Вред при удалении |
| --- | --- |
| Шесть decision boundaries в `SKILL.md` | Агент пишет до восстановления владельца, сохраняет вредный `no-change`, смешивает локальный gap с межзонной разведкой, дублирует truth, вырезает точный hard line либо записывает непроверенный кандидат. |
| Один `verification.md` | Правдоподобный текст получает ложный pass, active overload остаётся скрытым или candidate записывается без exact authority/parity. |
| Один `zone-scout.md` | Автор сам подтверждает подсказанное межзонное ребро, пропускает внешнего потребителя либо расширяет scope чтения. |
| `openai.yaml` | Codex теряет существующую UI/runtime-поверхность пакета. |

Других самостоятельных reference-файлов или процедур нет.

## Active-set audit после цикла 1

Единица — самостоятельно выполнимая или нарушимая граница решения, а не каждое
существительное в описании артефакта.

| Реальный режим | Активные единицы | Состав |
| --- | ---: | --- |
| Обычный authoring | 15 | Полный root содержит 16 единиц; на authoring-пути применимы 15. |
| Clean scout | 15 | Самостоятельный agent contract содержит 16 единиц; в clean scout-контексте применимы 15. |
| Verification | 20 active | `verification.md` — 21 full; active path = persistent root 5 + применимый reference 15. |
| Install-only continuation | 11 | Evidence уже материализовано в verification artifact; активны authority и runtime-schema gates. |
| Codex invocation | 4 full / 1 active | UI metadata содержит четыре значения; `default_prompt` только вызывает скил и завершается до authoring. |

В verification count входят сохраняющийся root-intent и применимые единицы
reference, а не только содержимое одного файла. Counts должен подтвердить
последний literal checker и clean-run; они не получены дроблением одного момента
по reference-файлам.
