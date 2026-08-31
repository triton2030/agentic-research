# Карта перекройки — 1mantine-dev, 2026-08-30

Текущий live-текст состоит из датированной версии Mantine delta. Рефактор не
возвращает прежний handbook: он переводит изменяемые факты во второй уровень,
а в тело возвращает недостающий выбор поведения.

| Старые указания | Обслуживаемая цель | Решение |
| --- | --- | --- |
| Новые API и patch releases последних 12 месяцев | не пропустить свежую возможность | `draft-2026-08-30/references/last-year.md` пересобирает official release-index на каждом вызове; статический список снят после обнаружения попадающего в окно `v8.2.8` |
| Ловушки v7→v8 и v8→v9 | не использовать API чужого мажора | подробный пересказ снят; exact migration всегда читается в официальном guide целевого мажора |
| Одинаковая resolved-версия `@mantine/*` | не собрать несовместимую когорту | сохранено в первом шаге тела |
| Peer dependencies, package CSS и import order | не получить runtime-сбой после правильного JSX | проверяются audit-режимом против установленной когорты и официальной страницы пакета |
| Tailwind layer order | не проиграть cascade | снят как always-on detail; проверяется только при реальном Tailwind/CSS-layer взаимодействии |
| Каталог переименований и удалений | не писать по памяти | заменён обязательным маршрутом current docs + installed types; список в prompt не притворяется вечной истиной |

## Поглощённые указания прежней большой версии

- Public component before raw markup, low-level `Combobox`, wrapper или custom
  CSS поглощён главным выбором body и audit-сравнением custom residue.
- `Stack` / `Group` / `Flex` before repeated layout CSS поглощён строкой
  высокоэффективных Mantine handles.
- Forms, Styles API, theme placement, hooks, managers, portals, SSR,
  accessibility и package styles поглощены обязательными audit-фасетами.
- Старая placement-лестница схлопнута до границы: Mantine владеет UI-механизмом,
  а feature, workflow, data, schema и permissions остаются приложению.
- Большая failure table не переносится: current official page and props are
  the source, а audit требует наблюдаемую проверку затронутого слоя.

## Новые ограничения и цена строгости

| Добавка | Дефолт → механизм → изменяемое решение → вред без неё → цена |
| --- | --- |
| current official docs + installed cohort | память другого мажора выглядит достаточной → source gate → API выбирается по установленной версии → compile/runtime ошибка → один точный lookup |
| public mechanism first | raw JSX/CSS/state привычнее → перечень high-leverage handles → сначала проверяется Mantine → дубли кода и поведения → custom путь требует названного пробела |
| audit artifact | мысленная сверка выглядит завершением → адресуемая строка на механизм → custom residue становится видимым → обход библиотеки проходит незаметно → короткая таблица перед финалом |
| readability exception | вызванный скилл может превратить Mantine в самоцель → сравнение совокупной сложности → читаемый локальный custom остаётся допустим → wrapper spaghetti → решение обязано назвать сравнивавшийся public API и цену |

`1readable-code` не меняется: его tracked owner уже владеет общей стратегической
читаемостью, а этот черновик владеет только Mantine-специфичным выбором.

## Хронология reference-состава

В 2026-08-11 владелец выбрал `help-center-map.md` и `placement.md`.

В 2026-08-22 более позднее решение сократило `1mantine-dev` до дельты новых
обновлений, поэтому прежняя пара перестала быть действующим составом.

В 2026-08-30 владелец отдельно добавил audit updates к official-docs-first
функции. Финальный черновик поэтому содержит только `audit.md` и
`last-year.md`; live-пакет не меняется до одобрения точной версии.

## Коррекция простоты — 2026-08-30

Позднее owner-критерий потребовал не переусложнять процесс: поле, стадия,
reference или процедура остаются только при названном counterfactual harm.
Поэтому version `window` и `confirmation` схлопнуты в один условный gate, а
audit `scope`, `candidates` и `decision` — в один cold-path audit. Их
предотвращаемые вреды сохранены: stale или чужой-major API и пропущенная
component capability/custom residue соответственно.

Повторяющиеся handoff-таблицы и authoring/check-церемония поглощены
self-contained version delta, явным `audit_input` и внешним маршрутом
`1skill-creation`; переносить этот маршрут в runtime нельзя, потому что он
раздувает active set и отвлекает от UI-решения.

## Коррекция цели — 2026-08-31

Владелец прямо указал, что в runtime пропущен обязательный раздел цели
(`_ops/chat-recall/2026-08-30-170320-codex-01a0528c.md:21`). В тело возвращены
две зонтичные цели: official Mantine должен давать полное, короткое и понятное
решение, но не становится самоцелью при большей совокупной сложности. Порядок и
два conditional reference не менялись.
