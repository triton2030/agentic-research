---
name: 1md-graph
description: >
  Use when change/review asks whether a Markdown `depends-on` or prose link is
  semantically correct, necessary, missing or invalidated. Audit both bodies and
  reverse propagation. Follow known link→1md-read; unknown meaning→1md-search;
  exact refs→1cli-tools; owner/shape→1ia-audit.
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

## Единица Работы И Результат

Один edge packet содержит:

- `holder#section` и конкретное утверждение вокруг ссылки;
- `target#section` или честный file-level target;
- relation job: `authority/definition`, `application/constraint`,
  `support/provenance`, `navigation` или `hard invalidation`;
- attribution: какой смысл holder приписывает target-у;
- прочитанное body evidence с обеих сторон;
- edge verdict: `sound`, `retarget`, `reclassify`, `remove`, `missing`,
  `conflict` или `unread`;
- для конкретной delta отдельный impact-status:
  `affected`, `unaffected`, `unread` или `not-applicable`.

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
| Применить разрешённый prose/edge repair и проверить Markdown | direct scoped edit + `1md-lint` |

Обычная ссылка без semantic question читается напрямую. Broken path или anchor
остаётся structural defect; его исправление не доказывает, что выбран правильный
target.

## Default Path — Audit Изменённого Neighborhood

1. **Назови claim и denominator.** Зафиксируй semantic delta либо точный edge
   audit question. Назови holder/target scope, exclusions и что считается
   существующим edge set. Без cross-file meaning обычный edit не требует этого
   маршрута. Rename/move/delete входит сюда, только если меняет semantic address,
   owner attribution или propagation; exact broken refs/counts сначала
   принадлежат `1cli-tools`.
2. **Собери edges, не verdicts.** Для изменяемого holder-а возьми его outgoing
   cross-file links и declared dependencies. Для изменяемого owner/source
   найди reverse holders. Frontmatter, body links, local registries, exact
   search и graph tools — candidate channels; ни один канал сам не доказывает
   полноту или правильность связи.
3. **Прочитай обе стороны.** Через `1md-read` раскрой holder statement и точный
   target section. Bare file link допустим только когда attribution
   artifact-wide; section-level claim требует section-level evidence. Не
   подменяй broken или слабый target похожим heading по догадке.
4. **Сформулируй attribution.** Одно проверяемое предложение:

   > В `HOLDER#section` утверждение **Y** приписывает
   > `TARGET#section` смысл/владение **X**.

   Затем проверь direction, endpoint, relation job, необходимость и
   совместимость bodies по
   [`semantic-edge-audit.md`](references/semantic-edge-audit.md).
5. **Отдели edge quality от delta impact.** `sound` edge может быть
   `unaffected` конкретной редакционной delta; неверный edge требует
   `retarget/reclassify/remove` независимо от текущей правки.
6. **Пройди propagation.** Для substantive change target-а каждому прямому
   holder-у дай `affected`, `unaffected` или `unread` с body evidence.
   Раскрывай следующий reverse hop только у `affected`-ветвей. `depends-on`
   создаёт обязательство review, не автоматического update.
7. **Ищи missing edge только от seed.** Когда конкретный owner claim, ID,
   consumer behavior или обнаруженный разрыв делает отсутствие material,
   используй
   [`missing-edge-discovery.md`](references/missing-edge-discovery.md).
   Open-world поиск без seed и denominator запрещён.
8. **Разреши конфликт на правильном слое.** Ясный owner + stale holder =
   `affected` или `retarget`. Два владельца одного инварианта, несовместимые
   claims или непонятная authority = `conflict` и handoff `1ia-audit`; не
   придумывай reciprocal edge как лечение.
9. **Применяй только разрешённый verdict.** При write-intent исправь exact
   holder/target edge и затронутый смысл, затем используй `1md-lint` и local
   structural checks. Owner, container или placement change остаётся у
   `1ia-audit`.

## Relation Strength

`depends-on` — hard invalidation edge:

> Если в `TARGET#section` материально изменится **X**, конкретный **Y** в
> `HOLDER#section` станет ложным или misleading.

Не можешь назвать X/Y и body addresses — это не hard edge. Полезная ссылка
может остаться `navigation`, `support` или `provenance`.

Cycle не является автоматическим semantic defect. SCC читается как одна review
cohort; `conflict` возникает, только если edges не проходят attribution/owner
test. Local contract, который явно требует DAG, сильнее этого default.

## Tool Evidence

Используй live project commands только как дешёвый способ перечислить edges,
проверить paths/anchors или получить reverse candidates. Перед schema-dependent
разбором читай `md tools <cmd> --json`; exact mechanics принадлежат
`1cli-tools` и установленному runtime.

Tool list обязан сохранять link type, holder context и exact fragment. Если
этого нет, он не является достаточным denominator для semantic audit.

## Corpus Mode

Полный или sampled аудит bounded cohort использует те же edge verdicts, но
другой denominator и stop. Открывай
[`corpus-edge-audit.md`](references/corpus-edge-audit.md) только для явного
corpus-wide вопроса; не превращай edit-time ход в кампанию.

## Stop

Стоп для существующего edge set, когда каждый edge в названном denominator
получил verdict или `unread` с owner/handoff, а каждая `affected`-ветвь закрыта
или явно передана.

Missing-edge route закрывается только записью seed, searched scope, channels,
прочитанных candidates и непросеянного остатка. Пустой search означает
`no candidate in this probe`, не отсутствие связи.

Финальный claim: **`semantic edge review status for <scope>`** с отдельными
reviewed verdicts, `unread`, handoffs, structural checks и open remainder. Это
не verdict о качестве, истинности или полноте файлов целиком.
