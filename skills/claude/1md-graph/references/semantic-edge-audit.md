---
description: "Admission test and verdicts for semantic correctness, necessity, strength and delta impact of one cross-file Markdown edge."
---

# Semantic Edge Audit

Contents: Unit · Relation jobs · Evidence · Admission test · Verdicts ·
Delta impact · Conflicts and cycles · Stop.

## Unit

Аудируй не URL отдельно, а связь вместе с несущим её утверждением:

```text
holder: HOLDER#section
holder statement: ...
target: TARGET#section | file-level
relation job: ...
attribution: holder claims target owns/supports/constrains ...
```

`holder` содержит link или dependency declaration. `target` — адресуемый
источник, которому holder приписывает смысл. Для hard edge target является
upstream source; reverse traversal находит holders, которые надо перечитать при
его изменении.

## Relation Jobs

Выбери information job до verdict:

- `authority/definition` — target владеет термином, правилом, ролью или
  инвариантом;
- `application/constraint` — holder применяет или сужает контракт target-а;
- `support/provenance` — target подтверждает, объясняет происхождение или
  evidence boundary;
- `navigation` — связь помогает reader-у, но её изменение не инвалидирует
  holder;
- `hard invalidation` — изменение X в target делает Y в holder ложным или
  misleading.

Это не обязательный frontmatter enum. Local corpus contract сильнее и может
назвать relation иначе; смысловая работа должна оставаться различимой.

## Evidence

Перед verdict прочитай:

1. holder section целиком, включая предложение до и после link;
2. exact target section и его owner/authority contract;
3. только те upstream/downstream sections, которые способны изменить verdict.

Heading, description, link label, metadata key, similarity и graph direction
выбирают чтение, но не заменяют body evidence. Local `source-of-truth-for`,
Rule IDs или contract markers полезны как addressable signals, а не
универсальная authority schema.

Если target — bare file:

- artifact-wide attribution может быть sound;
- section-specific attribution без section address требует `retarget` либо
  доказательства, что local contract считает whole-file target стабильным.

## Admission Test

Проверь шесть вопросов.

### 1. Attribution fit

Закрой конструкцию:

> В `HOLDER#section` конкретный **Y** приписывает `TARGET#section`
> смысл, authority, support или constraint **X**.

Target body действительно утверждает X в том же смысле и при тех же
ограничениях. Тематическая близость не проходит тест.

### 2. Direction

Holder применяет, цитирует, ограничивает или навигирует к target. Если target
на самом деле делегирует X holder-у, relation развёрнут или ownership спорен.

### 3. Endpoint precision

Target file и section должны быть минимальным стабильным owner address.
Ссылка на соседний heading, общий файл вместо точного section или устаревший
owner — `retarget`, даже когда path/anchor технически существует.

### 4. Necessity

Назови information job, которая исчезнет после удаления edge:

- owner/definition станет неадресуемым;
- evidence/provenance перестанет быть проверяемым;
- dependency не попадёт в propagation review;
- составная мысль потеряет обязательный reader path.

Если ни одна job не исчезает, edge декоративный, дублирующий или stale.
Optional navigation может оставаться sound только с честным navigation intent.

### 5. Strength

Hard edge требует X/Y invalidation:

> Если в target материально изменится X, Y в holder станет ложным или
> misleading.

Не проходит — downgrade до подходящей prose/navigation relation. Обратный
случай тоже material: holder фактически зависит от target, но хранит лишь
необязательную prose-ссылку — `reclassify` в hard relation по local contract.

### 6. Consistency

Bodies совместимы по term meaning, scope, units, state, authority и lifecycle.
Clear owner + stale consumer — обычный repair. Два конкурирующих owner-а или
несовместимые инварианты — `conflict`.

## Edge Verdicts

- `sound` — endpoint, attribution, direction, necessity и strength согласованы;
- `retarget` — relation нужна, но должна вести к другому file/section;
- `reclassify` — relation job или сила неверна;
- `remove` — decorative, duplicate, stale или misleading edge без
  самостоятельной information job;
- `missing` — конкретный holder Y использует target X, но обязательной
  addressable relation нет;
- `conflict` — linked bodies или owner claims несовместимы, и локальный repair
  edge-а не разрешает authority;
- `unread` — evidence ещё не прочитано; это очередь, не verdict.

Для каждого verdict сохрани attribution и body addresses. Batch verdict по
file names, snippets или graph rows недопустим.

## Delta Impact

Edge verdict и impact-status независимы:

- `affected` — эта delta target-а изменяет Y holder-а;
- `unaffected` — edge остаётся sound, но delta не касается применяемого X;
- `unread` — impact не проверен;
- `not-applicable` — edge audit идёт без конкретной delta.

Рекурсируй reverse graph только через `affected`. `unaffected` останавливает
ветвь с объяснением применяемого контракта.

## Conflicts And Cycles

Для спорной пары заполни:

```text
A owns:
A attributes to B:
B owns:
B attributes to A:
shared invariant:
```

Один invariant заявлен обоими, либо каждый делегирует его другому, —
`conflict` и handoff `1ia-audit`.

SCC сам по себе не verdict. Если каждое edge связывает разные, совместимые
инварианты, cohort может быть sound и требует совместного review. Если local
contract явно запрещает cycles, structural blocker действует независимо от
semantic verdict.

## Stop

Стоп, когда denominator существующих edges назван, обе стороны каждого
selected edge прочитаны, verdict и при наличии delta impact-status записаны,
`unread` передан, а conflict получил owner handoff.

Не распространяй этот stop на непросмотренный corpus или open-world missing
edges.
