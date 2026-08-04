---
name: 1md-graph
description: >
  Use when the semantic relation behind a cross-file Markdown link or
  `depends-on` is being added, removed or disputed, or a source change may
  invalidate reverse holders: structural graph output can hide wrong
  ownership, relation strength or stale propagation.
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
graph candidate
→ attribution Y → X по прочитанным bodies
→ evidence address | serialized endpoint | relation job
→ X/Y counterfactual
→ edge verdict + отдельный delta impact
→ только affected reverse branches
```

Корневая добродетель — рассматривать межфайловую связь как проверяемое
утверждение об отношении, а не как доказательство связности. Мера успеха — не
больше edges и не зелёный graph, а только обоснованные reader/authority/
propagation obligations; честный `unread` лучше гладкого verdict-а по proxy.

## Edge Packet — Наблюдаемый Proxy

До semantic verdict или правки собери один packet на одну связь:

- question и denominator: какая delta или edge проверяется, что входит и не
  входит в существующий edge set;
- holder evidence address — `HOLDER#section` и конкретный claim **Y**;
- target evidence address — `TARGET#section` либо честное file-level body и
  owner-смысл **X**;
- serialized edge — carrier, записанный relation/link type и endpoint; для
  missing edge — разрешённый local dialect либо `unread`;
- relation job: `authority/definition`, `application/constraint`,
  `support/provenance`, `navigation` или `hard invalidation`;
- attribution одним проверяемым предложением;
- прочитанное body evidence с обеих сторон;
- edge verdict: `sound`, `retarget`, `reclassify`, `remove`, `missing`,
  `conflict` или `unread`;
- для конкретной delta отдельный impact-status: `affected`, `unaffected`,
  `unread` или `not-applicable`.

Packet, заполненный именами файлов, snippets или tool rows без X/Y и глагола
отношения, — ритуал, не evidence. Подробный admission test и значения verdicts
живут в [`semantic-edge-audit.md`](references/semantic-edge-audit.md).
Labels packet-а — рабочая рамка аудита, не универсальная metadata schema;
local document contract может уточнять relation jobs и authority.

## Три Оператора

### 1. Преврати Candidate В Утверждение

Собери outgoing cross-file links и declared dependencies изменяемого holder-а;
для изменяемого owner/source найди reverse holders. Это candidate channels, не
verdicts. Через bounded reading прочитай holder statement и exact target body,
затем закончи фразу:

> В `HOLDER#section` утверждение **Y** приписывает
> `TARGET#section` смысл, authority, support или constraint **X**.

Голая команда «прочитай обе стороны» обходится, если решение всё ещё принято по
heading, label, similarity или graph direction. Если предложение нельзя
закрыть конкретными X/Y, связь остаётся `unread`; не подменяй target похожим
heading по догадке.

### 2. Раздели Три Независимые Оси

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

### 3. Проверь Контрфактуал До Propagation

Для `depends-on` назови hard invalidation test:

> Если в `TARGET#section` материально изменится **X**, конкретный **Y** в
> `HOLDER#section` станет ложным или misleading.

Нет адресуемых X/Y или counterfactual не проходит — это не hard edge. Полезная
связь может остаться `navigation`, `support/provenance` либо другой разрешённой
local relation. `Reclassify` в hard invalidation допустим только после X/Y-test
и чтения local relation/endpoint contract.

Отделяй качество edge от воздействия текущей delta. `Sound` edge может быть
`unaffected`; неверный edge требует собственного verdict независимо от delta.
Следующий reverse hop раскрывай только у `affected`-ветвей. `depends-on`
создаёт обязательство review, не автоматического update.

## Контрастивные Сцены

> **Default.** Target имеет точный section locator, а local graph contract
> разрешает только file-level `depends-on`. Модель видит более точный address и
> предлагает `retarget` на fragment. **Controller.** Section — evidence address,
> file — serialized endpoint; если X/Y-test пройден, file-level edge остаётся
> `sound`.

> **Антипример.** «Прочитал оба файла; `md check` зелёный; edge sound» выглядит
> аккуратно, но не содержит Y → X и не проверяет relation job. Structural green
> не меняет semantic status: verdict всё ещё `unread`.

> **Перенос.** Holder ссылается на исследование как evidence для одного тезиса.
> Тематическая близость не делает ссылку hard dependency всего файла. Сначала
> сформулируй support claim Y → X; повышай силу только если конкретное изменение
> X действительно сделает Y ложным или misleading.

## Audit Изменённого Neighborhood

1. **Зафиксируй вопрос и denominator.** Назови semantic delta либо exact edge
   question, holder/target scope, exclusions и существующий edge set. Обычный
   prose edit без cross-file meaning этого route не требует. Rename/move/delete
   входит только при изменении semantic address, attribution или propagation.
2. **Собери candidates.** Используй frontmatter, body links, local registries,
   exact search и graph tools как inventory channels. Denominator обязан
   сохранять carrier, holder context, relation type и фактический endpoint
   dialect.
3. **Прогони каждый selected edge через три оператора.** Не выдавай batch
   verdict по filenames или graph rows. Ясный owner + stale holder meaning даёт
   `affected`; неверный endpoint — `retarget`. Два owner-а одного инварианта
   или несовместимые claims дают `conflict`, а не reciprocal edge.
4. **Закрой propagation.** Каждому direct holder дай `affected`, `unaffected`
   или `unread` с body evidence; рекурсируй только `affected` branches.
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

Для существующего edge set остановись, когда каждый edge в denominator получил
verdict либо `unread` с owner/handoff, а каждая `affected`-ветвь закрыта или
явно передана. Missing-edge route дополнительно фиксирует seed, searched scope,
channels, прочитанных candidates и open remainder.

Финальный claim: **`semantic edge review status for <scope>`** с отдельными
verdicts, delta impacts, `unread`, handoffs, structural checks и open remainder.
Это не verdict о качестве, истинности или полноте файлов целиком.
