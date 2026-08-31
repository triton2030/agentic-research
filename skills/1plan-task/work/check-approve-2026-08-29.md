# Check-approve — 1plan-task — 2026-08-29

## Цикл 1

Проверен полный русский черновик вместе с product frame, cut, refactor map и
соседями семьи. Независимые окна: literal checker `/root/check_literal`,
trajectory checker `/root/check_trajectory`; clean executor —
`/root/clean_executor`; внешний совет — `claude-opus-5`, session
`7fc9d0ba-3bbd-47c7-a1b9-81d39df72afe`.

Opus изменил решение:

- hard `N/20` заменён сигналом упаковки и честной неделимостью;
- task mirror получил явного владельца общего словаря и снимка в map-family;
- «оркестратор + исполнители» заменён одним ответственным агентом и bounded
  helpers без task-authority.

Проверки дополнительно изменили решение:

- один writer теперь означает одного текущего writer-а с явной
  последовательной передачей после reread/fresh-reader gate;
- пять полей заменены смысловой границей автономной цели внутри принятого
  эпика, границы и authority;
- `3–7` стало эвристикой, а точный budget записывается только близко/выше
  ориентира;
- contract, context, work, lifecycle, handoff и retention стали
  самостоятельными стадиями;
- provenance записывается как `несущее требование → точный источник`, а
  несколько критичных строк разрешены вместе с адресом.

Clean executor сохранил одну атомарную signing-key rotation при 33 активных
единицах: split разрушал единого rollback/evidence-owner. Он восстановил
человеческий map-fragment и автономный task-prompt с шестью rollout-gates.
Это direct evidence против буквального деления по числу. Единственная реальная
неопределённость probe: в настоящем проекте task-снимок требует чтения полного
эпика, а не резюме карты.

Цепочки новых жёстких ограничений `default → механизм → вред → цена` записаны
в [карте рефактора](refactor-map-2026-08-29.md#цена-строгости).

## Цикл 2

Точная portable-версия `f60d9d63…` прошла финальный барьер:

- содержательные references получили локальные `## Цель`; router остался
  служебным;
- новый task собирается одним пакетом в памяти и один раз записывается целым;
  shaping/report, state/semantic lifecycle и continuation/closure разделены;
- duplicate-check по существующим task-файлам возвращён после clean-run:
  локальная цель не заменяет невыводимую retrieval-механику;
- task вне исполнимого frontier получает только доказанный `🔒/⏳/🛑`; здоровый
  live task вне frontier означает invalid map и no-write до ремонта;
- literal checker: максимум `20`, русский текст/links/descriptions — PASS;
- trajectory checker: autonomous task prompt, один writer и composition-only
  snapshot + live state gate — PASS;
- clean executor: complete write, duplicate guard, lifecycle stop и writer
  separation — PASS.

Hard lines оставлены для placement, schema, snapshot, duplicate retrieval,
state/frontier gate, handoff, прибора и consumer acceptance; цель, границу и
обычную адаптацию ведёт commander intent.
