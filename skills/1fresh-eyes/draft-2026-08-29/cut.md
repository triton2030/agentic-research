# Cut — draft 2026-08-29

Статус: карта среза для проверки. Не live contract.

## Сохранено

- Телос: лучший следующий ход и альтернатива, а не критика ради критики.
- Decision gate: вопрос на столе, что изменит ответ, конечный результат.
- Панель: `ladder` / `solvent` / `prospector` + cross-family Premortem.
- Named exception: явно выбранный critic, auditor или md-scout без панели, но с тем же isolation contract.
- Non-leading brief, отдельные evidence paths, source verification и synthesis без голосования.
- Terminal barrier, честный stop и полноценный surviving route.

## Поглощено зонтиками

- «Цель / Критерии / Инварианты / Дельта» → Контекст + три цели пользователя.
- Карта известных сбоев → условия чтения одного reference на каждой стадии.
- Gate, состав, isolation, acceptance и synthesis → семь шагов протокола.
- `accepted/rejected/deferred/...`, evidence bar и disagreement rules → короткий `synthesis.md`.
- Send/resume/follow-up matrix → короткий runtime `steering.md`.

## Перемещено

- Panel и named brief templates → отдельные runtime `panel-launch.md` и `named-launch.md`; на одной стадии читается только один из них.
- Codex cross-family prompt остаётся отдельным `premortem.md`: это следующая стадия после трёх native reports, а не часть их запуска.
- Runtime drift/date hypothesis → `refactor-map.md` как validation note, не постоянное behavioral rule.
- Полный inventory и причины каждого среза → `refactor-map.md`.

## Удалено из candidate

- Auditor/md-scout-specific classification из panel synthesis; их native products сохранены одной строкой.
- Примеры domain critics из panel brief: fixed panel уже разведена direction-контрактами ролей.
- Автоматический rerun при одинаковом выводе: failure теперь одинаковые method/evidence/consequence, а не честный consensus.
- Повторное объяснение, что критики и evidence-products не являются panel lenses.
- Human-history `cut.md` из installed Claude package: история остаётся только в repo.

## Не принято

- Panel-only scope: фальсифицирован отсутствием второго owner-а isolation для named roles и прямым owner-решением про named exception.
- Dynamic roster или optional Premortem: внешние прецеденты и Solvent дали гипотезу, но буквальное owner-решение фиксирует четвёрку; A/B нет.
- Перенос non-leading rules в шесть agent definitions: дублирует instruction budget и слабее caller-side gate.
- Новый shared owner: текущая owner-топология асимметрична; refactor не изобретает второй source tree.

## Размер и внимание

- Claude/Codex body: 117/107-ish current lines → 43 draft lines.
- Claude references: 183 current lines → 109 draft lines.
- Codex references: 242 current lines → 140 draft lines.
- Первичная оценка активного набора отозвана после literal checker: launch-файлы содержали ≥23/≥37 инструкций. Новый счёт проверяется повторно по отдельным стадиям в `refactor-map.md`.
