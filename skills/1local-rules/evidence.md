# Evidence рефактора

## Функция и допуск

Продукт — одно проектное правило `2*`, выбранное только там, где cold
instruction route не доставляет неочевидную дельту к конкретному действию.
Папка истории создана, потому что её не было, а refactor-контракт требует
сохранить функцию и снятые смыслы.

След применения принципов: `agentic-research:P-002/P-003` сохраняет
автономность через commander intent и текущий прямой owner-сигнал;
`agentic-research:P-004/P-005` заменяет самоотчёт структурной, routing,
behavior и parity-проверкой; `agentic-research:P-007/P-008` оставляет смысл у
существующего tracked owner-а и не создаёт shared owner либо новую Product
Frame.

## Baseline

- Tracked owner: `skills/claude/1local-rules/SKILL.md`, 136 строк, 12 381 байт.
- Installed Claude расходится с tracked owner после незаписанной замены
  `1skill-routing` на несуществующий `1skill-creation/references/routing.md`.
- Installed Codex имеет тот же мёртвый route и отдельную runtime-формулировку;
  его `agents/openai.yaml` содержит русское `short_description`, хотя текущий
  owner-критерий требует короткие English description surfaces.
- В рабочем дереве до этого рефактора target owner не был изменён; посторонние
  изменения не трогаются.

## Проверка кандидата

- Первый независимый раунд нашёл четыре дефекта: creation-only trigger,
  двусмысленное «редактируй owner один раз», неопределённую platform delta и
  скрытый активный набор не менее 46 единиц.
- Второй раунд нашёл незамкнутый переход между режимами, неполное retirement,
  конфликт stop после rollback и активные наборы 22–29 единиц.
- Финальная раскройка имеет шесть самостоятельных режимов; консервативные
  активные наборы по `cut.md` равны 19–20.
- `quick_validate.py` проходит; все внутренние ссылки существуют; main и
  reference descriptions имеют 89–146 символов и написаны по-английски.
- Чистый treatment probe прошёл admission, structural, routing и behavior;
  неприменимые references не читал и остановился до запрещённой ему записи.
- Matched comparator: без скила агент потерял префикс `2`, придумал
  непроверенный Python-валидатор и остановил установку; с финальным кандидатом
  выпустил минимальный `2social-publish`, сохранил owner/mirrors, различил
  use/skip/near-miss и показал наблюдаемую дельту решения.

## Установка

- Точный кандидат записан сначала в `skills/claude/1local-rules/`, затем в
  `/Users/triton/.claude/skills/1local-rules/` и
  `/Users/triton/.codex/skills/1local-rules/`; отсутствующий второй tracked
  source tree не создан.
- `quick_validate.py` прошёл на tracked owner-е и обеих установленных копиях.
- `SKILL.md` и шесть references имеют одинаковый SHA-256 во всех четырёх
  поверхностях candidate↔owner↔Claude↔Codex; внутренних битых ссылок нет.
- Мёртвые ссылки на `1skill-routing` и `references/routing.md` отсутствуют.
- Codex `agents/openai.yaml` сохранил runtime metadata; `short_description`
  заменён на 36-символьный English trigger surface.
