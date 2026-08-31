# Карта candidate — 1mantine-dev, 2026-08-30

## Функция

Увести Mantine-задачу от generic React/CSS prior к текущему официальному public
contract установленной когорты, оставив обычный путь коротким.

## Runtime-файлы и единицы

Счёт различает только независимо нарушимые требования; окончательные значения и
активные наборы подтверждаются буквальной проверкой замороженных байтов.

| Runtime-файл | Единиц | Counterfactual harm при полном снятии |
| --- | ---: | --- |
| [`SKILL.md`](SKILL.md) | 23 | Без commander's intent generic prior снова обходит Mantine, а public-механизм становится самоцелью. |
| [`references/audit.md`](references/audit.md) | 33 | Неназванная public capability, неполное coverage или custom residue остаётся незамеченной. |
| [`references/last-year.md`](references/last-year.md) | 28 | Stale release или чужой major выглядит совместимым, а подтверждённая delta теряется до audit. |

## Режимы

| Режим | Вход | Выход | Активный набор |
| --- | --- | --- | ---: |
| core | task packet + one exact resolved version for all affected `@mantine/*` | verified public handle или readable local residue | 23 |
| version gate | immutable self-contained `{packet, cohort}` + version uncertainty | same `{packet, cohort, result}` with delta/address, `none` или `unknown` | 51 |
| audit gate | immutable `audit_input = {packet, cohort}` with literal `packet.required_behaviors` | full official candidate set first, then coverage/evidence table | 56 |

Version и audit — условные gates, а не микростадии: обычный `Button + useForm`
не открывает их без собственной uncertainty.

## Trigger cases

- use: «Добавь кнопку и форму на Mantine»;
- use: «Проверь, почему Mantine Select закрывается»;
- use: «Обнови Mantine до девятой версии»;
- skip: «Исправь CSS карточки без Mantine».

## Границы

`1readable-code` владеет общей стратегической ценой будущего кода.

`1mantine-dev` владеет current Mantine public contract и редким readable-local
custom-исключением.

## Поглощено

`window`/`confirmation`, отдельные `scope`/`candidates`/`decision`, повторный
handoff boilerplate и authoring/check route убраны из runtime. Они не меняли
решение сами; сохраняются только их реальные защиты — exact cohort от stale API,
version result от потерянной delta и exhaustive audit от пропущенной capability
или custom-замены.

## Честный residual

Восстановленные функции намеренно не сжаты до ориентира в 20 единиц.
Независимые candidate discovery, official addresses, coverage evidence, exact
cohort и version-result handoff предотвращают разные доказанные owner-вреды;
это наблюдаемый когнитивный риск, а не автоматический blocker и не новые стадии
или references. Обычный `Button + useForm` не открывает gates без собственной
uncertainty.
