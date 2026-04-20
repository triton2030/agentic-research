# Live Flow

Использовать после выбора `$playwright`.

## Цель

Сделать один чистый browser-pass и получить evidence без лишней интерактивной тяжести.

## Ход

1. Сформулировать проверку в одном предложении.
2. Зафиксировать scope:
   desktop/mobile, route, section, flow.
3. Вызвать официальный `$playwright`.
4. Сначала собрать evidence:
   screenshot, snapshot, DOM/layout facts, visible states.
5. Только после evidence делать краткий вывод или переводить задачу в script/test.

## Хорошо Подходит Для

- smoke verification
- one-page checks
- short flow reproduction
- evidence capture for later review
- authoring a focused Playwright script after one clean pass

## Плохо Подходит Для

- длинного пошагового исследования с множеством развилок
- многократного повторения гипотез на одной сессии
- случаев, где page state нужно долго держать живым

## Output Shape

Минимум на выходе:

- что проверяли
- какой evidence реально собрали
- что это значит
- нужен ли следующий шаг: stop, deeper interactive pass, visual audit, script authoring
