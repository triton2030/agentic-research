# Check round 1 — 2026-08-29

Статус: findings двух независимых clean-window checkers приняты по буквальному
owner evidence или наблюдаемому trace; candidate исправлен, повторная проверка
ещё не выполнена.

## Instruction checker

- Старый активный счёт был неверен: объединённые launch surfaces содержали не
  16/19, а не менее 23/37 независимо исполнимых инструкций. Принято: panel,
  named и Codex Premortem разведены по стадиям; счёт отозван до повторного
  замера.
- Независимые действия стояли в одной строке. Принято: один шаг протокола —
  одна отдельная строка.
- Не хватало буквальных owner quotes и секции `## Протокол поведения`.
  Принято.
- Named mode мог включаться по self-classified trigger. Принято: только явно
  названная пользователем роль.
- Не хватало `Main уже читал`, другого primary source и числового
  `Кругов пройдено`. Принято.
- Были потеряны professional question, граница raw output → canon, grouping
  source/label/severity и запрет final acceptance. Принято.
- Codex recursive-parent loop не был закрыт. Принято: явный skip с gap.
- Не было `agents/openai.yaml`. Принято.
- Два исторических source paths были broken. Принято и исправлено.

## Trajectory checker

- Полный запрет передавать текущий маршрут скрывал объект judgment. Принято:
  route/state передаётся как source-bound факт; rationale/diagnosis/desired
  verdict main остаются запрещены.
- Panel handback и named handback были смешаны. Принято: панель всегда проходит
  synthesis; named product возвращается в native форме.
- `Not for local review` конфликтовал с явным named critic/auditor. Принято:
  исключение в description; unnamed local/framework-gap review исключён.
- Simultaneous launch не переживал ограничение capacity. Принято: bounded
  waves с обязательными terminal reports.
- Numeric two-follow-up stop не отражал прогресс. Принято: stop по отсутствию
  нового evidence step, falsifier или сужения boundary.

## Не принято

- Dynamic roster или optional Premortem. Это не ошибка candidate, а отмена
  буквального owner-bound fixed four решения без нового owner decision/A-B.
- Panel-only scope. Позднее owner evidence сохраняет named exception, а
  isolation/brief одиночного вызова не имеет другого владельца.
