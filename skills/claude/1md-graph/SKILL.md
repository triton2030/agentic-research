---
name: 1md-graph
description: >
  Use when a Markdown link, `depends-on`, or source change needs a semantic
  impact verdict; clean structure can still hide stale holders. Read both
  bodies, classify the relation, and propagate only affected branches.
---

# 1md-graph

## Root Virtue

Каждая межфайловая ссылка — утверждение об отношении, а не доказательство
связности. Skill проверяет **semantic edge**: что окружающий текст приписывает
target-у, действительно ли target этим смыслом владеет или его поддерживает,
нужна ли связь и что она обязует перечитать после изменения.

`md`/graph output может перечислить или проверить структурные связи, но не
выносит semantic verdict. Не говори `file checked`, `graph clean`,
`safe-to-edit` или «пропущенных связей нет».

Когнитивная цепь до verdict:

```text
semantic question | concrete ΔX
→ serialized carrier → attribution atoms
→ независимые Y и X + weaker/null counterframe
→ address | endpoint | relation job
→ concrete X0 → X1 counterfactual
→ atom verdict + impact
→ affected Y → concrete ΔY → next reverse hop
```

## Единица Работы И Результат

Один serialized carrier может нести несколько самостоятельных claims. Сначала
раздели его на attribution atoms; один atom связывает один holder claim **Yᵢ**
с одним target claim **Xᵢ** и одной relation job. Не усредняй смешанные atom
verdicts до file-level `sound`.

Packet одного atom содержит:

- incoming delta `X₀ → X₁` либо `not-applicable`;
- serialized carrier, link/relation type и endpoint;
- `holder#section` и независимо извлечённый **Y** с qualifiers scope, modality,
  authority и lifecycle;
- `target#section` или честный file-level target и независимо извлечённый **X**;
- relation job: `authority/definition`, `application/constraint`,
  `support/provenance`, `navigation` или `hard invalidation`;
- attribution, weaker/null counterframe и различающее их body evidence;
- evidence-state: `unread`, `read-sufficient`, `read-insufficient` или
  `read-conflicting`;
- atom verdict: `sound`, `retarget`, `reclassify`, `remove`, `missing`,
  `conflict` или `undetermined`; при `unread` verdict ещё не вынесен;
- для конкретной delta отдельный impact-status:
  `affected`, `unaffected`, `undetermined`, `unread` или `not-applicable`; при
  `affected` — минимальный требуемый holder change **ΔY**.

Локальный document contract может уточнять relation jobs и authority. Эти
labels — рабочая рамка аудита, не универсальная metadata schema.

## Границы

| Information job | Owner |
|---|---|
| Прочитать известные holder и target sections | `1md-read` |
| Найти candidates на отсутствующую связь | `1md-search` |
| Решить owner, split/merge/move или placement истины | `1ia-audit` |
| Exact refs, path/anchor resolution, counts и live CLI contract | `1cli-tools` |
| Оценить смысл, необходимость, силу и propagation edge | `1md-graph` |
| Применить разрешённый prose/edge repair и проверить Markdown | direct scoped edit + local Markdown checks |

Обычная ссылка без semantic question читается напрямую. Broken path или anchor
остаётся structural defect; его исправление не доказывает, что выбран правильный
target.

## Default Path — Audit Изменённого Neighborhood

1. **Назови question, denominator и delta.** Зафиксируй exact edge question
   либо перепиши изменение как конкретное `X₀ → X₁`. Назови holder/target scope,
   exclusions и existing edge set. Без cross-file meaning обычный edit не
   требует route. Rename/move/delete входит сюда, только если меняет semantic
   address, attribution или propagation; exact refs/counts сначала принадлежат
   `1cli-tools`.
2. **Собери edges, не verdicts.** Для изменяемого holder-а возьми его outgoing
   cross-file links и declared dependencies. Для изменяемого owner/source
   найди reverse holders. Frontmatter, body links, local registries, exact
   search и graph tools — candidate channels; ни один канал сам не доказывает
   полноту или правильность связи.
3. **Атомизируй carrier.** Выпиши самостоятельные claims вокруг каждой
   serialized link/dependency. Один carrier, одна строка tool output или один
   файл не являются semantic unit; owner, evidence и constraint claims могут
   требовать разных atoms.
4. **Извлеки стороны независимо.** Через `1md-read` сначала сформулируй **Y** из
   holder-а без принятия target labels за ответ; отдельно сформулируй **X** из
   target-а без принятия holder intent за authority. Сохрани qualifiers: scope,
   modality, units, state, authority и lifecycle. Bare file link допустим,
   только когда local endpoint dialect его разрешает.
5. **Сформулируй attribution и rival.** Для каждого atom закончи предложение:

   > В `HOLDER#section` утверждение **Y** приписывает
   > `TARGET#section` смысл/владение **X**.

   Затем построй weaker/null counterframe: target связан с темой, но не владеет,
   не поддерживает или не инвалидирует exact Y. Назови body evidence,
   различающее версии. Если обе остаются допустимыми, поставь
   `read-insufficient` + `undetermined`, а не выбирай сильную relation из
   формулировки вопроса. После этого проверь direction, endpoint, relation job,
   necessity и compatibility по
   [`semantic-edge-audit.md`](references/semantic-edge-audit.md).
6. **Проверь concrete counterfactual.** Для hard relation назови допустимое
   `X₀ → X₁`, exact фрагмент Y, который станет false/misleading, и требуемый
   `ΔY`. Фраза «если X materially изменится» без этих трёх частей тест не
   проходит. Edge quality и текущий delta impact остаются независимыми.
7. **Перебазируй propagation.** Для `affected` atom выведи минимальный `ΔY` и
   только его передай как incoming delta следующему reverse hop. Не переноси
   исходный `ΔX` или file-level label. `unaffected` останавливает branch;
   `undetermined`/`unread` останавливает mutation и требует handoff. SCC веди
   worklist-ом до fixpoint. `depends-on` создаёт review obligation, не
   automatic update.
8. **Ищи missing edge только от seed.** Когда конкретный owner claim, ID,
   consumer behavior или обнаруженный разрыв делает отсутствие material,
   используй
   [`missing-edge-discovery.md`](references/missing-edge-discovery.md).
   Open-world поиск без seed и denominator запрещён.
9. **Разреши конфликт на правильном слое.** Ясный owner + stale holder =
   `affected` или `retarget`. Два владельца одного инварианта, несовместимые
   claims или непонятная authority = `conflict` и handoff `1ia-audit`; не
   придумывай reciprocal edge как лечение.
10. **Применяй только разрешённый verdict.** При write-intent исправь exact
   holder/target edge и затронутый смысл, затем выполни local Markdown и
   structural checks. Owner, container или placement change остаётся у
   `1ia-audit`.

## Relation Strength

`depends-on` — hard invalidation edge. Он требует concrete perturbation:

> Если `TARGET#section` изменится из **X₀** в **X₁**, какой exact **Y** станет
> ложным или misleading и во что он должен измениться (**ΔY**)?

Не можешь назвать X/Y, body addresses, допустимое `X₀ → X₁` и `ΔY` — hard edge
не доказан. Полезная ссылка может остаться `navigation`, `support` или
`provenance`.

Cycle не является автоматическим semantic defect. SCC читается как одна review
cohort; `conflict` возникает, только если edges не проходят attribution/owner
test. Local contract, который явно требует DAG, сильнее этого default.

## Tool Evidence

Используй live project commands только как дешёвый способ перечислить edges,
проверить paths/anchors или получить reverse candidates. Перед schema-dependent
разбором читай `md tools <cmd> --json`; exact mechanics принадлежат
`1cli-tools` и установленному runtime.

| Нужен inventory | Команда |
|---|---|
| Outgoing declared edges изменяемого holder-а | `md deps FILE --json` |
| Reverse holders изменяемого owner/source | `md impact FILE --json` |
| Propagation worklist перед rename/move/delete | `md preflight FILE --json` |
| Broken paths и anchors после правки | `md check --paths SCOPE --json` |
| Cycle cohort как одна review-группа | `md cycles --json` |
| Holder-neighborhood перед незнакомой правкой | `md edit-context FILE --json` |
| Heading-level contract impact | `md section-blast-radius FILE CORPUS --query "..." --json` |

Каждая строка этих ответов несёт `reason` — какое поле или ссылка её породили
(`declares depends-on: X`, `body wikilink to X at #anchor`, `reached through Y
at depth 2`). Это классифицирует **carrier/link type**, но не semantic relation
job или strength, и лишь сужает последующее чтение. Сама фраза holder-а всё ещё
читается через `1md-read`. Rows без прочитанного holder statement остаются
candidates, а не verdicts.

Tool list обязан сохранять link type, holder context и exact fragment. Если
этого нет, он не является достаточным denominator для semantic audit.

## Corpus Mode

Полный или sampled аудит bounded cohort использует те же edge verdicts, но
другой denominator и stop. Открывай
[`corpus-edge-audit.md`](references/corpus-edge-audit.md) только для явного
corpus-wide вопроса; не превращай edit-time ход в кампанию.

## Stop

Стоп для существующего edge set, когда каждый carrier разложен на atoms, каждый
atom получил evidence-state, прочитанный atom — verdict, а
`unread`/`undetermined` — owner/handoff; для каждой `affected`-ветви выведен и
закрыт конкретный `ΔY`.

Missing-edge route закрывается только записью seed, searched scope, channels,
прочитанных candidates и непросеянного остатка. Пустой search означает
`no candidate in this probe`, не отсутствие связи.

Финальный claim: **`semantic edge review status for <scope>`** с отдельными atom
verdicts, carrier dispositions, impacts, `unread`/`undetermined`, handoffs,
structural checks и open remainder. Это не verdict о качестве, истинности или
полноте файлов целиком.
