# Context Packs

Использовать только пакет для текущего случая. Не раскрывать всё сразу.

## One-shot Browser Check

Нужен минимум:

- цель проверки
- URL, route или dev server
- ожидаемый user path
- какие evidence нужны на выходе: screenshot, snapshot, layout data, short verdict

Не тянуть:

- длинную историю продукта
- лишние альтернативные сценарии
- большие куски кода, если вопрос про rendered result

## Interactive Debug

Нужен минимум:

- что ломается или плавает
- текущая гипотеза или 2-3 competing hypotheses
- какие состояния нужно пройти в одной живой сессии
- какие evidence важны для решения: console, DOM, layout, repeated actions

Не тянуть:

- весь backlog багов
- unrelated file trees
- общую архитектуру, если она не меняет путь проверки

## Script or Test Authoring

Нужен минимум:

- какой user outcome должен быть проверен
- что считать pass/fail
- какой evidence уже есть
- какой уровень артефакта нужен: quick script, reusable helper, formal test

Не тянуть:

- весь framework lore
- неиспользуемые fixture details
- весь existing suite, если меняется один сценарий

## Visual Audit From Live Page

Нужен минимум:

- какая часть экрана или flow важна
- что именно надо понять: spacing, hierarchy, block order, emphasis, density
- desktop/mobile scope
- нужен ли один экран, section crop или before/after pair

Не тянуть:

- общий редизайн продукта
- полную маркетинговую стратегию
- скрытые состояния, если их никто не просил оценивать

## Algorithmic Layout Check

Нужен минимум:

- какие блоки или зоны считать load-bearing
- какая страница и breakpoint
- нужен ли gap analysis, block sizing, order check, visual weight check
- нужен ли просто report или готовый Playwright script

Дальше читать [layout-signals.md](references/layout-signals.md).
