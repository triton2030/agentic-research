# Финальное evidence — 1plan-map

## Проверки и решения

- Волна 1: принято чтение всех Frames/Principles, `1use-principles`, ссылки на
  продуктовую правду в эпиках и explicit epic-file owner.
- Fresh Eyes: глобальная последовательность снята; accepted map решает свой
  concurrency/order contract. Условный `1index` шов сохранён как уже
  утверждённая функция.
- Волна 2: принято возвращать невыводимую продуктовую развилку в `1planning` и
  сверять human-visible state с task-файлами.

## Trigger

- use: «Создай следующий эпик проекта» → `1plan-map`;
- skip: «Реши, стоит ли начинать задачу» → `1planning`;
- near-miss: «Создай автономный task-файл» → `1plan-task`.

Frontmatter и `agents/openai.yaml` дают тот же выбор.

## Active set

Консервативный статический recount: общий route около `35`, максимум `40` при
одновременной активации sequential и `1index` условий. Mixed-run держал только
реально применимые решения и прошёл family peak `18`; self-replay финальной
дельты даёт `20`. Статический остаток оправдан четырьмя topology invariants,
чтением всей продуктовой правды и двумя редкими условными швами; он не спрятан
в references или длинных строках.

## Falsifiers финальной дельты

- две равно допустимые топологии → до durable write возвращена развилка;
- defer изменил dashboard-visible state → evidence передано `1plan-map`;
- параллельная подготовка разрешена картой → не помечена конфликтом.

## Exact candidate

SHA-256 package fingerprint:
`6bfa2a50f039e53e260d489f880c5d5917750991940f28d076c685eb28b94b95`.
