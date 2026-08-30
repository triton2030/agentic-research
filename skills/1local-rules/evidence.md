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

## Коррекция владельца после первой установки

Первая версия была признана переусложнённой после прямого уточнения владельца:
общая логика authoring должна остаться в `1skill-creation`, а `1local-rules`
добавляет только project scope, префикс `2`, две runtime-проекции и
совместимость с глобальными и корневыми проектными инструкциями.

Вторая версия удаляет шесть references и оставляет один outcome-контракт.
Фальсификатором упрощения было уникальное локальное правило внутри удаляемых
references; разбор показал, что admission, form, structural, routing и behavior
proof общие, а локальная часть install/retire полностью выражается критерием
одновременного состояния owner↔Claude↔Codex.

Первый trajectory-review снял лишнее ограничение «может только уточнять»:
оно запрещало новое совместимое project-local правило, хотя владелец запретил
конфликт, а не добавление локального смысла. Кандидат теперь допускает новое
правило только при совместимости с обоими старшими instruction-слоями.

Первый literal-review потребовал явного вызова текущего `$1skill-creation`,
замкнутого снятия трёх поверхностей и точного parity-критерия. Эти находки
приняты: authoring явно завершается при создании или обновлении, одно
запрошенное lifecycle-состояние включает owner↔Claude↔Codex, а `SKILL.md` и
общие ресурсы сравниваются побайтно. UI/runtime metadata оставлена единственной
допустимой platform-дельтой.

Повторный trajectory-review исправил порядок: общий authoring больше не
завершается до добавления локальной дельты. `$1skill-creation` теперь принимает
уже локальный `2*`-кандидат, поэтому scope, имя, routing и proof относятся к
финальной версии, а не к промежуточному обычному скилу.

Требование ещё раз спросить владельца не применяется: более сильная прямая
инструкция владельца требует автономно завершить установку без вопросов
(`_ops/chat-recall/2026-08-30-034608-codex-01a04fb2.md:17`), а строки 18–20
задают функцию, утверждение упрощения и дополнительный conflict-критерий.
Отдельная skill-specific Product Frame не создана: у пакета её не было, живая
функция полностью задана текущими словами владельца, а создание ещё одного
semantic owner-а нарушило бы project-wide P-007/P-008.

Повторный literal-review показал, что compound parity и conflict-proof в main
скрывали активный набор выше двадцати и оставляли размытые границы metadata.
Уникальная operational-дельта вынесена в один `finish.md`: он разрешает пути
из корневых инструкций целевого проекта, применяет одно lifecycle-состояние к
трём поверхностям, проверяет recursive parity или полное отсутствие и
фальсифицирует конфликт со старшими instruction-слоями. Общий authoring по-
прежнему не дублируется.

Clean-executor trial подтвердил thin-delta trajectory, но нашёл возможный
external history path в `1skill-creation/references/goal-context.md`. История
authoring не является активной package surface `2*`; owner и обе проекции
разрешаются только из реестра и корневых инструкций целевого проекта. `sync.md`
делает эту границу явной и запрещает придумывать новый source tree.

Финальный разрешённый literal-review потребовал project registry, точную
portable parity surface и меньший активный набор. Один `finish.md` разделён по
двум независимым локальным обязанностям: `conflict.md` доказывает совместимость,
а `sync.md` разрешает topology по registry/root, синхронизирует только
`SKILL.md` + `references/` + `scripts/` + `assets/` и допускает platform
metadata лишь вне этих поверхностей. При отсутствии owner-контракта новый
source tree не создаётся. После этой механической коррекции новый review-loop
не запускался: лимит двух повторов `check-approve.md` исчерпан.

Финальный clean-executor отделил локальность активного package от допустимой
глобальной authoring-истории и нашёл риск двойной установки. Main теперь
говорит только об активности package в одном целевом проекте, поэтому не
конфликтует с `1skill-creation/references/goal-context.md`. `conflict.md` и
`sync.md` явно исполняют общие installation-обязательства для `2*`, а не
запускают второй install-процесс.

Предустановочный Retrieval нашёл более позднее решение владельца о clean-room
рефакторе вместо построчного сокращения
(`_ops/chat-recall/2026-08-30-130004-codex-01a051ac.md:16-17`). Оно не меняет
функцию `1local-rules` и подтверждает выбранную форму: прежний процесс удалён,
а новый контракт пересобран из функции и прямых критериев владельца.

## Установка второй версии

- Tracked owner: `skills/claude/1local-rules/`; installed projections:
  `/Users/triton/.claude/skills/1local-rules/` и
  `/Users/triton/.codex/skills/1local-rules/`.
- Portable shape во всех трёх поверхностях: `SKILL.md`,
  `references/conflict.md`, `references/sync.md`; шесть references первой
  версии отсутствуют.
- `quick_validate.py` прошёл на tracked owner, draft и обеих installed
  projections; внутренних битых ссылок нет.
- Recursive owner↔Claude parity и owner↔Codex portable parity прошли побайтно;
  единственная Codex-дельта — runtime-owned `agents/openai.yaml`.
- Codex metadata приведена к новой функции: «Локальные скилы», короткий English
  trigger и default prompt с `$1skill-creation`, префиксом `2`, conflict-check
  и owner↔Claude↔Codex sync.
- Проверенные старшие инструкции: `/Users/triton/.codex/AGENTS.md`,
  `/Users/triton/.claude/CLAUDE.md` и корневой `AGENTS.md` этого проекта.
  Новый пакет не ослабляет их: он требует их прочитать и считать конфликт
  блокирующим.
- Fresh Eyes завершился `panel_incomplete`: обязательный Opus/Premortem bridge
  недоступен в текущей среде, а подмена другой модельной семьи запрещена.
  Literal, trajectory и clean-executor проверки завершены отдельно; полный
  четырёхлинзовый отчёт не заявляется.

## Коррекция раскладки после установки

Владелец прямо указал, что в теле достаточно места для критичных подробностей
(`_ops/chat-recall/2026-08-30-034608-codex-01a04fb2.md:21`). Два обязательных
reference-перехода не давали progressive disclosure: каждый install, update и
retire всё равно требовал оба файла. Их содержание перенесено в один
самодостаточный `SKILL.md`; функция, portable parity surface, registry/root
lookup, conflict gate, retirement и evidence contract сохранены.

Первый аудит однофайловой версии нашёл circular producer order, риск двойной
установки, conflict gate на снятии, неразрешённое расхождение registry/root и
пропуск portable agent-role files. Clean executor независимо подтвердил первые
два дефекта. Body теперь передаёт `$1skill-creation` ограничения кандидата,
останавливает общий маршрут на утверждённом кандидате, заменяет его generic
install одной local-установкой, не блокирует retire конфликтом, fail-closed
обрабатывает topology disagreement и синхронизирует portable `agents/` content
кроме явно runtime-owned metadata.

Второй trajectory-review и clean-executor не нашли path escape, duplicate
install, conflict, parity или retire-дефектов. Второй literal-review нашёл одну
несогласованную квитанцию: retire пропускал conflict gate, но output требовал
conflict result. Финальный output разделён: create/update возвращают conflict +
parity evidence, retire — absence evidence; после лимита двух повторов новый
review-loop не запускался.

Текущая однофайловая версия установлена из tracked owner в Claude и Codex.
`quick_validate.py` прошёл на owner и обеих installed projections. Recursive
owner↔Claude parity и owner↔Codex portable parity прошли побайтно; portable
shape во всех трёх поверхностях состоит только из `SKILL.md`, старые
`references/conflict.md` и `references/sync.md` отсутствуют. Единственная
Codex-дельта — сохранённый runtime-owned `agents/openai.yaml`. Предыдущие
installed packages сохранены в `/tmp/1local-rules-install-backup.wU8Len`.
