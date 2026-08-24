---
name: 1md-graph
description: >-
  Use after Markdown meaning, links, depends-on edges, names, moves, or semantic
  addresses change and downstream impact needs a verdict. Not for similarity
  search or purely broken paths.
---

# 1md-graph

## Зачем Нужен Этот Скилл

Естественный shortcut — принять перечислимую структуру за смысл: tool нашёл
edge, path и anchor валидны, значит связь «правильная». Это привлекательно,
потому что graph output точен и конечен, а semantic relation скрыта в prose. В
результате модель может приписать target-у чужой смысл, усилить navigation до
`depends-on`, выбрать endpoint по точности locator-а или закрыть source edit,
оставив stale holders.

Skill разрывает shortcut до verdict или mutation:

```text
semantic question | concrete ΔX
→ serialized carrier → attribution atoms
→ независимые Y и X + weaker/null counterframe
→ evidence address | serialized endpoint | relation job
→ concrete X0 → X1 counterfactual
→ atom verdict + отдельный delta impact
→ affected Y → concrete ΔY → следующий reverse hop
```

Корневая добродетель — рассматривать межфайловую связь как проверяемое
утверждение об отношении, а не как доказательство связности. Мера успеха — не
больше edges и не зелёный graph, а только обоснованные reader/authority/
propagation obligations; честный `undetermined` лучше гладкого verdict-а по
недостаточному evidence.

## Attribution Atom — Наблюдаемый Proxy

Один serialized carrier может обслуживать несколько разных утверждений. До
semantic verdict раздели его на attribution atoms; один atom связывает один
holder claim **Yᵢ** с одним target claim **Xᵢ** и одной relation job. Carrier
получает итоговую disposition только после atoms; смешанные atom verdicts не
усредняй до одного гладкого `sound`.

Для каждого atom собери packet:

- question и denominator: какая delta или edge проверяется, что входит и не
  входит в существующий edge set;
- incoming delta — конкретное `X₀ → X₁` либо `not-applicable`;
- serialized carrier — где записана связь, её link/relation type и endpoint;
- holder evidence address — `HOLDER#section` и независимо извлечённый claim
  **Y**, включая scope, modality, authority и lifecycle qualifiers;
- target evidence address — `TARGET#section` либо честное file-level body и
  независимо извлечённый owner-смысл **X** с теми же qualifiers;
- relation job: `authority/definition`, `application/constraint`,
  `support/provenance`, `navigation` или `hard invalidation`;
- attribution одним проверяемым предложением и weaker/null counterframe;
- discriminator: body evidence, которое отличает attribution от counterframe;
- evidence-state: `unread`, `read-sufficient`, `read-insufficient` или
  `read-conflicting`;
- atom verdict: `sound`, `retarget`, `reclassify`, `remove`, `missing`,
  `conflict` или `undetermined`; при `unread` semantic verdict ещё не выносится;
- для конкретной delta отдельный impact-status: `affected`, `unaffected`,
  `undetermined`, `unread` или `not-applicable`, а при `affected` — требуемый
  holder change **ΔY**.

Packet, заполненный именами файлов, snippets или tool rows без X/Y и глагола
отношения, — ритуал, не evidence. Подробный admission test и значения verdicts
живут в [`semantic-edge-audit.md`](references/semantic-edge-audit.md).
Labels packet-а — рабочая рамка аудита, не универсальная metadata schema;
local document contract может уточнять relation jobs и authority.

## Четыре Оператора

### 1. Атомизируй Carrier И Нормализуй Delta

Собери outgoing cross-file links и declared dependencies изменяемого holder-а;
для изменяемого owner/source найди reverse holders. Это candidate channels, не
verdicts. Сначала перепиши входное изменение как конкретное `X₀ → X₁`; без
delta используй `not-applicable`.

Затем выпиши все самостоятельные claims вокруг carrier-а. Если одна строка
`depends-on`, footnote или prose link одновременно заявляет owner, evidence и
constraint, создай несколько atoms. Один carrier, один файл или одна tool row
не являются semantic unit.

### 2. Извлеки Стороны Независимо И Построй Counterframe

Через bounded reading прочитай holder statement и exact target body. Сначала
сформулируй **Y** из holder-а без принятия target labels за ответ; отдельно
сформулируй **X** из target-а без принятия holder intent за authority. Сохрани
qualifiers: scope, modality, units, state, authority и lifecycle. Затем закончи
фразу:

> В `HOLDER#section` утверждение **Y** приписывает
> `TARGET#section` смысл, authority, support или constraint **X**.

До verdict построй правдоподобный weaker/null counterframe: target тематически
связан, но не владеет, не поддерживает или не инвалидирует этот exact Y. Назови
body evidence, которое различает две версии. Если обе остаются допустимыми,
evidence-state — `read-insufficient`, verdict — `undetermined`; не подменяй
target похожим heading и не выбирай более сильную связь по формулировке вопроса.

### 3. Раздели Оси И Проверь Конкретный Counterfactual

Проверяй отдельно:

1. **Evidence address** — какие точные bodies доказывают attribution.
2. **Serialized endpoint** — как relation разрешено записывать в local corpus.
3. **Relation job/strength** — какую information или invalidation job выполняет
   связь.

Точная target section не требует section fragment в edge: local contract может
сериализовать sound dependency file-level. И наоборот, точный fragment не
делает relation необходимой или hard. Если endpoint dialect либо relation class
не прочитаны, mutation по этим осям запрещена и статус остаётся `unread`.

Неимпликации: locator ≠ prose link; locator consumer ≠ hard dependency;
direct-read job ≠ invalidation; marker ≠ missing graph edge.

Для `depends-on` задай допустимое конкретное изменение `X₀ → X₁`, которое
сохраняет роль target-а, но меняет проверяемый predicate:

> Если `TARGET#section` изменится из **X₀** в **X₁**, какой exact фрагмент **Y**
> станет ложным или misleading и во что он должен измениться (**ΔY**)?

Фраза «если X materially изменится» без `X₀`, `X₁` и наблюдаемого `ΔY` позволяет
подтвердить любую желаемую силу и тест не проходит. Нет адресуемых X/Y или
counterfactual не различает hard и weaker relation — это не доказанный hard
edge. `Reclassify` допустим только после этого теста и чтения local
relation/endpoint contract.

### 4. Перебазируй Delta На Каждом Hop

Отделяй качество edge от воздействия текущей delta. `Sound` edge может быть
`unaffected`; неверный edge требует собственного verdict независимо от delta.
Для `affected` atom выведи минимальный требуемый holder change **ΔY**. Только
его, а не имя изменённого файла и не исходную **ΔX**, передавай как incoming
delta следующему reverse hop. Если `ΔY` не назван, propagation не доказан.
`unaffected` останавливает branch; `undetermined`/`unread` останавливает mutation
и создаёт handoff. SCC обрабатывай worklist-ом до fixpoint, когда новый
конкретный delta больше не появляется. `depends-on` создаёт обязательство
review, не автоматического update.

## Контрастивные Сцены

> **Default.** Target имеет точный section locator, а local graph contract
> разрешает только file-level `depends-on`. Модель видит более точный address и
> предлагает `retarget` на fragment. **Controller.** Section — evidence address,
> file — serialized endpoint; если X/Y-test пройден, file-level edge остаётся
> `sound`.

> **Антипример.** «Прочитал оба файла; `md check` зелёный; edge sound» выглядит
> аккуратно, но не содержит Y → X и не проверяет relation job. Structural green
> не меняет semantic status: если bodies правда прочитаны, это
> `read-insufficient` + `undetermined`; если нет — `unread` без verdict.

> **Перенос.** Holder ссылается на исследование как evidence для одного тезиса.
> Тематическая близость не делает ссылку hard dependency всего файла. Сначала
> сформулируй support claim Y → X; повышай силу только если конкретное изменение
> X действительно сделает Y ложным или misleading.

> **Составной carrier.** Один `depends-on` сопровождает два claims: лимит
> вопросов и обязательную группировку по темам. Изменение `10 → 5` затрагивает
> только первый atom. Выведи `ΔY: "до 10" → "до 5"`, передай его следующему
> holder-у и останови topic-ветвь; file-level `affected` не оправдывает
> переписывание обоих claims.

## Audit Изменённого Neighborhood

1. **Зафиксируй вопрос и denominator.** Назови semantic delta либо exact edge
   question, holder/target scope, exclusions и существующий edge set. Обычный
   prose edit без cross-file meaning этого route не требует. Rename/move/delete
   входит только при изменении semantic address, attribution или propagation.
2. **Собери candidates.** Используй frontmatter, body links, local registries,
   exact search и graph tools как inventory channels. Denominator обязан
   сохранять carrier, holder context, relation type и фактический endpoint
   dialect.
3. **Прогони каждый selected carrier через четыре оператора.** Не выдавай batch
   verdict по filenames или graph rows. Сначала atom verdicts и evidence-state,
   затем carrier disposition. Ясный owner + stale holder meaning даёт
   `affected`; неверный endpoint — `retarget`. Два owner-а одного инварианта
   или несовместимые claims дают `conflict`, а не reciprocal edge.
4. **Закрой propagation.** Каждому direct atom дай `affected`, `unaffected`,
   `undetermined` или `unread` с body evidence. Для `affected` выведи `ΔY` и
   рекурсируй только с этим новым delta; в SCC продолжай до fixpoint.
5. **При write-intent примени только разрешённый verdict.** Исправь exact edge
   и затронутый holder meaning, затем запусти local structural checks. Не меняй
   owner, container, placement или endpoint dialect в рамках этого контракта.

## Условные Routes

- Для seeded missing relation открой
  [`missing-edge-discovery.md`](references/missing-edge-discovery.md). Open-world
  поиск без seed и denominator не даёт claim о полноте; empty search означает
  только `no candidate in this probe`.
- Для явного corpus-wide или cohort-wide вопроса открой
  [`corpus-edge-audit.md`](references/corpus-edge-audit.md). Не превращай
  edit-time neighborhood в кампанию.

## Tool Evidence

Используй live project commands только для перечисления candidates,
paths/anchors и reverse holders. Перед schema-dependent разбором читай
`md tools <cmd> --json`; live runtime сильнее remembered syntax.

| Нужен inventory | Команда |
|---|---|
| Outgoing declared edges изменяемого holder-а | `md deps FILE --json` |
| Reverse holders изменяемого owner/source | `md impact FILE --json` |
| Propagation worklist перед rename/move/delete | `md preflight FILE --json` |
| Broken paths и anchors после правки | `md check --paths SCOPE --json` |
| Cycle cohort как одна review-группа | `md cycles --json` |
| Holder-neighborhood перед незнакомой правкой | `md edit-context FILE --json` |
| Heading-level contract impact | `md section-blast-radius FILE CORPUS --query "..." --json` |

Каждая строка ответа несёт `reason` — какое поле или ссылка её породили
(`declares depends-on: X`, `body wikilink to X at #anchor`, `reached through Y
at depth 2`). Это даёт endpoint class и link type и сужает последующее чтение,
но attribution им не заменяется: фраза holder-а читается отдельно через
`1md-read`.

Tool inventory недостаточен для denominator, если теряет реально записанный
endpoint class, link type или holder context. Structural path/anchor checks и
cycles остаются отдельным evidence layer: они не выносят semantic verdict и не
разрешают фразы `file checked`, `graph clean`, `safe-to-edit` или «пропущенных
связей нет».

Cycle не является автоматическим semantic defect. SCC читается как review
cohort; blocker возникает отдельно, если local contract требует DAG либо edges
не проходят attribution/owner test.

## Граница И Stop

Skill владеет смыслом, необходимостью, силой и propagation конкретной
Markdown-связи. Он не назначает semantic owner-а, не меняет document topology и
не превращает locator/addressability в edge. Pure path/anchor repair без
semantic question не получает здесь relation verdict.

Для существующего edge set остановись, когда каждый carrier разложен на
проверяемые atoms, каждый atom получил evidence-state, прочитанный atom —
verdict, а `unread`/`undetermined` — owner/handoff; для каждой
`affected`-ветви выведен и закрыт конкретный `ΔY`. Missing-edge route
дополнительно фиксирует seed, searched scope, channels, прочитанных candidates
и open remainder.

Финальный claim: **`semantic edge review status for <scope>`** с отдельными
atom verdicts, carrier dispositions, delta impacts, `unread`/`undetermined`,
handoffs, structural checks и open remainder. Это не verdict о качестве,
истинности или полноте файлов целиком.
