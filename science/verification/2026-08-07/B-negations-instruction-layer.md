# Инвентарь отрицаний — `1instruction-layer` 50503 симв.

Зафиксирован 2026-08-07 **до** написания сжатой версии.

Механический скан маркеров (`не`, `нельзя`, `кроме`, `только`, `иначе`,
`обязан`, `not`, `never`, `only`, `without`) по семи файлам пакета дал **198**
строк: `SKILL.md` 105, `audit-meaning-criteria.md` 33,
`audit-placement-structure.md` 20, `llm-divergences.md` 13,
`claude-discovery.md` 11, `cli-recipes.md` 9, `language-quality-audit.md` 9.
Сведены в **94** нормативные единицы. Сверка покрытия — поимённо, в конце.

Сокращения источников: `S` = `SKILL.md`, `AM` = `references/audit-meaning-criteria.md`,
`AP` = `references/audit-placement-structure.md`, `CD` = `references/claude-discovery.md`,
`CR` = `references/cli-recipes.md`, `LQ` = `references/language-quality-audit.md`,
`LD` = `references/llm-divergences.md`.

## A. Режим и допуск durable работы

| # | Точная цитата | Источник |
|---|---|---|
| N01 | «`audit` не меняет files; `change` разрешает только scoped repair» — дубли: «findings, evidence и exact proposed repair **без edits**», «В audit mode остановись на evidence-backed proposed repair», «Размещать их в файлах только в change/fix mode», «Правка — только change mode» | `S` Gate 0.1 / «Продукт И Мера»; `CR`; `AM`; `AP` |
| N02 | «Отдели одноразовое условие задачи от правила, которое должно пережить thread» | `S` Gate 0.2 |
| N03 | «Для durable candidate назови основание: stable local fact, recurring correction/failure или hard invariant» | `S` Gate 0.3 |
| N04 | «сильный framing, повтор и уверенность автора не являются evidence» | `S` Gate 0.4 |
| N05 | «Не достраивай её правдоподобным reasoning-ом и не продолжай только потому, что задача допускает красивый ответ» | `S` Gate 0.5 |
| N06 | «отметь только проваленные jobs; не переписывай здоровый слой по инерции» | `S` Gate 0.6 |
| N07 | «нет durable основания или проваленного job → не добавляй правило» | `S` Gate 0 «Результат gate» |
| N08 | «Если ещё выбирается instruction text vs skill/agent/hook/config, остановись: surface decision принадлежит `1skill-architect`» | `S` Gate 0.7 |

## B. Effective chain

| # | Точная цитата | Источник |
|---|---|---|
| N09 | «одна и та же папка может иметь разные chain в Codex, Claude Code или другом runner-е» | `S` Gate 1.1 |
| N10 | «Перечисли только реально загружаемые global → root → relevant subtree instructions; отдели `file exists` от `text reaches this task`» | `S` Gate 1.2; `CD` «Что Грузится Когда» |
| N11 | «только когда они спорны; не переноси привычку одного runtime в другой» | `S` Gate 1.3 |
| N12 | «runtime winner и semantic owner могут оказаться разными фактами» | `S` Gate 1.5 |
| N13 | «Разреши текущий effective winner из loading + precedence, а не из имени файла или уверенности автора» | `S` Gate 1.6 |
| N14 | «Если спорны root/subtree topology, duplicate или placement, прочитай `audit-placement-structure.md` **до** owner-решения» | `S` Gate 1.7 |
| N15 | «Не можешь доказать loading или precedence → назови gap; не выбирай owner из воображаемой chain» | `S` Gate 1 «Результат gate» |

## C. Owner и класс delta

| # | Точная цитата | Источник |
|---|---|---|
| N16 | «назови полный scope наблюдаемого trigger-а, не папку, где текст случайно найден» | `S` Gate 2.1 |
| N17 | «Выбери самый узкий existing owner, который покрывает trigger целиком и загружается до нужного акта» | `S` Gate 2.2 |
| N18 | «Оставь один source of meaning: competing copies удали, перемести или замени pointer-ом» — дубль: «Папочное правило живёт в своей папке, не в корне; корневое — в корне, не размазано по детям», «Один owner + pointer» | `S` Gate 2.3; `AP`; `LQ` |
| N19 | «Короткий refresher допустим только в другом lifecycle moment и продолжает ссылаться на того же owner-а» — дубли: «Допустимо только как **осознанная свежесть** … не как копия в другом слое хранения», «другая папка сама по себе этого не доказывает» | `S` Gate 2.3 / 5.7; `AP`; `LQ` |
| N20 | «proposed rule не должен незаметно присвоить их authority или создать второй способ разрешить тот же конфликт» | `S` Gate 2.4 |
| N21 | «Классифицируй delta как `local fact / owner pointer`, `behavioral rule` или `hard invariant`» | `S` Gate 2.5 |
| N22 | «Если нужная форма требует split/merge/move/new instruction container, остановись до edits: целевой контейнер принадлежит `1ia-audit`» — дубль: «сначала `1ia-audit`, не закрепляй плохую IA текстом» | `S` Gate 2.6 / «Boundaries»; `AP` п. 2 |
| N23 | «Нет одного owner-а или устойчивой delta → delete/no-op, не wording» | `S` Gate 2 «Результат gate» |

## D. Steering cell

| # | Точная цитата | Источник |
|---|---|---|
| N24 | «До wording собери одну **steering cell**» | `S` «Развилка До Wording» |
| N25 | «`MUST`, длинное rationale или self-check не чинят этот causal gap сами по себе» — дубль: «Do not compensate with generic “be proactive”, “be careful”, MUST or a longer self-check stack» | `S` «Развилка До Wording»; `LD` «Do Not» |
| N26 | «описывай поведение, не скрытое состояние» — дубль: «не подменяй его скрытым состоянием или поздним объяснением агента» | `S` «Развилка До Wording»; `S` Gate 3.4 |
| N27 | «Cell — authoring scaffold, не обязательный формат целевой инструкции… в целевой текст попадают только load-bearing trigger, rule, owner/source, exception и stop» | `S` «Развилка До Wording» |
| N28 | «Если развилку и изменившийся акт назвать нельзя, durable delta пока не доказана» — дубль: «Акты не различаются → durable steering delta не доказана» | `S` «Развилка До Wording»; `S` Gate 3 «Результат gate» |
| N29 | «Прогони этот момент через реально загружаемую old/default chain, не добавляя proposed rule задним числом» | `S` Gate 3.3 |
| N30 | «разница видна до финального самоотчёта» | `S` Gate 3.1 |
| N31 | «пример иллюстрирует правило, но не создаёт его» — дубль: «example не создаёт случайный mandate», «Descriptive „обычно“, example, comment или section placement исполняются как обязательное правило» | `S` Gate 3.7 / 5.9; `LQ` «Accidental mandate / Hyrum» |
| N32 | «несколько независимых изменений означают несколько repairs или слишком широкий scope» | `S` Gate 3.8 |
| N33 | «используй `audit-meaning-criteria.md` как conditional depth, а не копируй его protocol сюда» — дубль: «Это router, а не второй runbook `md`», «Не дублируй его commands и verdict rules здесь» | `S` Gate 3.9; `CR` |

## E. Control и выбор repair

| # | Точная цитата | Источник |
|---|---|---|
| N34 | «Дорогой или необратимый invariant должен опираться на permission, hook, validator, test или approval у runtime owner-а» — дубли: «Чем дороже или необратимее пропуск, тем слабее prose как control», «instruction оставляет route/объяснение, не изображает enforcement», «дорогой/необратимый инвариант держи структурным механизмом … не только прозой», «Hard invariant → runtime enforcement, prose только объясняет» | `S` «Продукт И Мера», Gate 4.1–4.2; `AM` п. 6; `CD` «Placement Rules» |
| N35 | «`MUST` / `NEVER` / `CRITICAL` стоят на preference, которое runtime не обеспечивает… сильное слово только для hard invariant + enforcement handoff» | `LQ` «Risk-word overclaim» |
| N36 | «`CLAUDE.md` — context, не enforced configuration» | `CD` |
| N37 | «сравни repairs по причине провала» — семь именованных вариантов `keep` / `delete` / `narrow scope` / `move to owner` / `replace with pointer` / `rewrite exact wording` / `handoff to enforcement`, каждый со своим условием | `S` Gate 4.3 |
| N38 | «Выбери один primary repair. Supporting edits допустимы только для удаления созданных им duplicates или broken routes, не для попутной уборки» — дубль: «Выбери один repair», «Рекомендуй один repair» | `S` Gate 4.4; `LQ`; `AP` |
| N39 | «Procedure добавляй только когда order, lifecycle moment, completeness или хрупкость сами являются контрактом; иначе оставь outcome/decision rule» — дубли: «Последовательность добавляй только когда order/completeness сами являются invariant», «number only the invariant sequence» | `S` Gate 4.5; `AM` п. 4; `LD` |
| N40 | «Не можешь отличить выбранный repair от меньшего → используй меньший» | `S` Gate 4 «Результат gate» |

## F. Wording exact delta

| # | Точная цитата | Источник |
|---|---|---|
| N41 | «Начни с observable trigger/scope, а не с желаемого характера агента» | `S` Gate 5.1 |
| N42 | «запрет без preferred continuation оставляет прежнюю траекторию доступной» | `S` Gate 5.2 |
| N43 | «Переведи „осознай / будь внимателен / учти“ в наблюдаемый source check, artifact, comparison, target act или outcome» | `S` Gate 5.3 |
| N44 | «поставь load-bearing check в point of action — рядом с командой, phase boundary или решением, которое он должен изменить» | `S` Gate 5.4 |
| N45 | «exception не должен молча становиться вторым default-ом» | `S` Gate 5.5 |
| N46 | «Назови evidence и stop, по которым future agent не объявит completion по пересказу правила» — дубль: «Критерий без сверки осыпается… явный `Проверка И Stop`» | `S` Gate 5.6; `AM` п. 6 |
| N47 | «Используй pointer по умолчанию» — дубли: «rare depth переноси в project-owned cold owner только с условным pointer», «Hot-path сверху, редкое — в project-owned cold surface по ссылке» | `S` Gate 5.7; `AP` |
| N48 | «Добавь rationale, только если без causal link правило выглядит произвольным… Добавь contrastive example, только если boundary иначе не распознаётся» | `S` Gate 5.8 |
| N49 | «router ориентирует, а не погружает; outcome-rule не репетирует ceremony» — дубль: «Ориентируй, не погружай: указатель к owner-у вместо предзагрузки знаний зоны» | `S` Gate 5.9; `AM` Design Mode п. 3 |
| N50 | «Проведи delete-first pass: убери generic caution, повторы, obsolete scaffolding и строки, удаление которых не меняет следующий act или evidence» | `S` Gate 5.10 |
| N51 | «Если спорны introspective slogan, literal scope, negative vacuum, Hyrum, frame capture или accidental mandate, прочитай `language-quality-audit.md` **до** финального wording» | `S` Gate 5.11 |
| N52 | «Rule называет один instance, хотя observed obligation относится к классу… не надеяться на молчаливое обобщение» | `LQ` «Literal scope» |
| N53 | «Текст копирует пользовательскую рамку и защищает симптом, а не recurring mechanism… не сохранять случайную формулировку как canon» | `LQ` «Frame capture / sycophancy» |
| N54 | «line count сам finding не доказывает» | `LQ` «Lost-in-the-middle» |

## G. Bypass и доказательство

| # | Точная цитата | Источник |
|---|---|---|
| N55 | «До вердикта назови самый правдоподобный способ выполнить новую форму, сохранив старое решение» | `S` Gate 6.1 |
| N56 | «Если bypass проходит, вернись к недостающему operator-у или point of action; не лечи его ещё одним `MUST` либо полем отчёта» | `S` Gate 6.2 |
| N57 | «заранее назови expected old first act, expected proposed first act и observable scoring» | `S` Gate 6.3 |
| N58 | «не меняй одновременно case, model, settings и правило» — дубль: «Do not change effort, tools and prompt wording together when attribution matters» | `S` Gate 6.4; `LD` «Do Not» |
| N59 | «Для малой low-risk правки counterfactual walkthrough — design-time proxy. Для material/global/risky surface используй чистый cold-start with/without» | `S` Gate 6.5 |
| N60 | «один удачный run доказывает возможность, не probability shift» | `S` Gate 6.6 |
| N61 | «Self-report, пересказ правила, lint и заполненный output template не являются behavioral evidence» — дубли: «Способность пересказать правило, гладкость wording и заполненный шаблон доказывают только видимость текста, не steering», «validation не выдаёт text compliance за changed behavior» | `S` Gate 6.7, «Продукт И Мера», «Вывод И Стоп» |
| N62 | «Same-model critique, debate или второй проход… не становятся независимой проверкой без external verifier/tool, live owner evidence либо наблюдаемого outcome» | `S` Gate 6.7 |
| N63 | «не превращай недатированную интуицию в постоянное свойство модели» — дубль: «model-specific claim либо подтверждён релевантной записью `llm-divergences.md`, либо сформулирован как model-agnostic wording risk» | `S` Gate 6.8; `LQ` |
| N64 | «маршрутизируй его через `cli-recipes.md`, не дублируя чужой runbook» | `S` Gate 6.9 |
| N65 | «Недоступен behavioral run → назови gap; не повышай design-time proxy до доказательства эффективности» | `S` Gate 6 «Результат gate», «Вывод И Стоп» |

## H. Controller

| # | Точная цитата | Источник |
|---|---|---|
| N66 | «Каждый gate должен породить свой наблюдаемый результат до следующего. Пропустить gate можно только когда его результат уже прямо подтверждён текущим evidence; гладкий финальный текст не заменяет промежуточное различение» | `S` «Controller» |
| N67 | «Не смешивай три разных failure-а instruction hierarchy… Успех позднего шага не доказывает предыдущий» | `S` «Controller» |
| N68 | «сделай clean re-anchor: отбрось зависящие от них выводы и draft… а не исправляй скомпрометированное рассуждение на месте» | `S` «Controller» |
| N69 | «Рабочие результаты — decision traces, не требование раскрывать приватную chain-of-thought. Не публикуй их как длинную анкету, если пользователь не просил audit report» | `S` «Controller» |
| N70 | «Найденная слабость LLM сама по себе не заслуживает нового prose-rule: классифицируй mitigation… и добавляй её только в принадлежащую точку» | `S` «Controller» |
| N71 | «этот controller владеет методом мышления; references владеют только условной глубиной» | `S` «Controller» |
| N72 | «Контрастивная демонстрация механизма, не правило проекта» | `S` (блок после Gate 6) |

## I. Triggered Repository Rules

| # | Точная цитата | Источник |
|---|---|---|
| N73 | «допустимая instruction surface, если правило устойчиво, нужно только в редкий наблюдаемый момент и root может надёжно маршрутизировать этот момент» | `S` «Triggered Repository Rules» |
| N74 | «Always-on invariant остаётся в effective `AGENTS.md`; path-local правило — в subtree `AGENTS.md`» | `S` TRR |
| N75 | «Root содержит только `observable trigger → exact RULE`; procedure и rationale живут в одном RULE» | `S` TRR |
| N76 | «Его steering cell реконструируется при authoring, но не сериализуется целиком без необходимости» | `S` TRR |
| N77 | «RULE без root route — orphan; копия его procedure в root — competing owner» | `S` TRR |
| N78 | «Читай RULE только после совпадения trigger, не загружай всю папку заранее» | `S` TRR |
| N79 | «жанр project-local `2*` — `1local-rules`» | `S` TRR / «Boundaries» |

## J. Границы, universalization, локальные нормы references

| # | Точная цитата | Источник |
|---|---|---|
| N80 | «project scope/done/stop → `1goal`; task contract → `1planning`» | `S` «Boundaries» |
| N81 | «`depends-on`, holders, anchors, cycles, broken links → `1md-graph`» — дубль: «структурную зависимость папки от папки (`depends-on`) объявляй и проверяй через `1md-graph`» | `S` «Boundaries»; `AM` п. 3 |
| N82 | «Остановись до edits, container/graph/runtime mutation или внешней записи, если текущий intent их не разрешает» | `S` «Вывод И Стоп» |
| N83 | «Не навязывай чужому repo конкретные README/GOAL/`_ops` conventions» — дубли: «Runtime facts ниже не превращают одну repo convention в глобальный invariant», «не превращай в универсальный Markdown law», «не навязывай `_ops` layout чужому repo», «Это вариант совместного owner-а, не глобальный закон» | `AP` пп. 3–4; `CD`; `AM` п. 5 |
| N84 | «„Звучит плохо“ — вкус, не finding» — дубль: «stylistic taste не является finding» | `AP` «Findings»; `LQ` |
| N85 | «секции существуют только когда меняют решение» / «Hot-path сверху» | `AP` «Что проверяет» п. 3 |
| N86 | «прими его results только как candidates до чтения bodies» | `AP` п. 3; `CR` |
| N87 | «Closeout — только после edits… Не требуй `md` в repo, где он не является live owner tool» — дубль: «после edit всегда достаточен direct diff/read; другой closeout запускает только owner задетого semantic/graph/exact-CLI риска» | `AP` пп. 5–6; `CR` |
| N88 | «Imports помогают поддерживать owner structure, но не экономят launch context… Split ради файловой красоты не является progressive disclosure» | `CD` |
| N89 | «Claude Code читает `CLAUDE.md`, не `AGENTS.md` напрямую» | `CD` |
| N90 | «Не приписывай превышению выдуманный failure mechanism вроде „skill точно не найдётся“» | `CD` |
| N91 | «Прочитай зону, не угадывай… 2-4 пункта, не список всего… Каждый критерий — outcome-истина, проверяемая, не процедура» | `AM` пп. 1–2, «Findings» |
| N92 | «Probes — evals, не контент: их текст никогда не вставляется в инструкцию» — дубль: «Probe без ответа = недостающая delta или неверный owner, не повод вставить ответ текстом» | `AM` Design Mode пп. 2, 5 |
| N93 | «„Новая зона — читать нечего“ не бывает» / «Subtree file не ориентирует агента до своей загрузки» | `AM` Design Mode пп. 1, 4 |
| N94 | «Use this reference only after a trace, correction or representative eval shows a concrete failure» — дубли: «never run as a generic checklist», «No observed failure means no model-specific rule», «label it a hypothesis and repair only the observed gap», «If the delta does not change the observed behavior, remove it rather than stacking another instruction», «Do not infer a family-wide trait from one trace», «Promote a repeated model-specific finding only to the current model owner» | `LD` |

## Сверка покрытия

Ситуация из `B-battery-instruction-layer.md`, которая ловит единицу, либо честная
пометка «не покрыта».

| Единица | Ловится | Единица | Ловится |
|---|---|---|---|
| N01 | B01 | N48 | не покрыта |
| N02 | B01 | N49 | не покрыта |
| N03 | B01 | N50 | не покрыта |
| N04 | B05 | N51 | не покрыта |
| N05 | B05 | N52 | не покрыта |
| N06 | B06 | N53 | не покрыта |
| N07 | B06 | N54 | не покрыта |
| N08 | B08 | N55 | B10 |
| N09 | B05 | N56 | B10 |
| N10 | B05 | N57 | не покрыта |
| N11 | не покрыта | N58 | не покрыта |
| N12 | не покрыта | N59 | B12 |
| N13 | B05 | N60 | B11 |
| N14 | не покрыта | N61 | B11 |
| N15 | B05 | N62 | не покрыта |
| N16 | не покрыта | N63 | не покрыта |
| N17 | B15 | N64 | не покрыта |
| N18 | B09 | N65 | B12 |
| N19 | B09 | N66 | B01 |
| N20 | B15 | N67 | не покрыта |
| N21 | не покрыта | N68 | B14 |
| N22 | B07 | N69 | не покрыта |
| N23 | B06 | N70 | не покрыта |
| N24 | B04 | N71 | не покрыта |
| N25 | B04, B10 | N72 | не покрыта |
| N26 | B04 | N73 | B15 |
| N27 | не покрыта | N74 | не покрыта |
| N28 | B04 | N75 | B15 |
| N29 | B04 | N76 | не покрыта |
| N30 | B11 | N77 | B15 |
| N31 | не покрыта | N78 | не покрыта |
| N32 | не покрыта | N79 | не покрыта |
| N33 | не покрыта | N80 | B02 |
| N34 | B03 | N81 | не покрыта |
| N35 | B03 | N82 | B07 |
| N36 | B03 | N83 | не покрыта |
| N37 | B03, B06 (крайние варианты `handoff` и `keep`; пять средних — нет) | N84 | B06 |
| N38 | не покрыта | N85 | B15 |
| N39 | не покрыта | N86 | не покрыта |
| N40 | не покрыта | N87 | не покрыта |
| N41 | B13 | N88 | не покрыта |
| N42 | B13 | N89 | не покрыта |
| N43 | B04 | N90 | не покрыта |
| N44 | B10 | N91 | не покрыта |
| N45 | не покрыта | N92 | не покрыта |
| N46 | B11 | N93 | не покрыта |
| N47 | B15 | N94 | не покрыта |

### Итог

- Единиц инвентаря: **94**
- Покрыто хотя бы одной ситуацией: **49**
- **Не покрыта: 45**

### Что означают 45 непокрытых

Батарея из 15 ситуаций покрывает несущий хребет `SKILL.md` — допуск, chain,
steering cell, control, bypass, доказательство — и почти не достаёт до локальных
норм шести `references/`. Из 45 непокрытых 13 принадлежат только references
(`LQ` 3, `CD` 3, `AM` 3, `AP`/`CR` 2, `LD` 1, плюс общий anti-universalization
N83), остальные 32 — мелкая грануляция gate-ов `SKILL.md`: одиночные пункты
Gate 3–6 и половина `Triggered Repository Rules`.

Это ограничение измерителя, а не разрешение резать: потеря непокрытой единицы
батареей **не будет видна**. Для references-норм при разрезе применяется
умолчание протокола — без прогона строка считается несущей.

### Прогноз, записанный заранее

Наибольший риск потери при сжатии — единицы, встречающиеся ровно один раз и не
покрытые батареей: N11, N12, N16, N21, N27, N32, N38, N40, N45, N48, N50, N54,
N57, N62, N67, N69, N72, N76, N78, N86, N90. Ожидаю, что первыми уйдут условные
маршруты к references (N11, N14, N33, N51, N64) — они выглядят как ссылочный шум,
а несут момент чтения.
