---
description: "Admission test and verdicts for semantic correctness, necessity, strength and delta impact of one cross-file Markdown edge."
---

# Semantic Edge Audit

Contents: Unit · Relation jobs · Evidence · Admission test · Non-implications ·
Verdicts · Delta impact · Conflicts and cycles · Stop.

## Unit

Аудируй не URL отдельно, а связь вместе с несущим её утверждением:

```text
holder evidence: HOLDER#section
holder statement: ...
target evidence: TARGET#section | honest file-level body
serialized edge: <carrier + type + endpoint> | absent
endpoint dialect: <allowed local forms> | unread
relation job: ...
attribution: holder claims target owns/supports/constrains ...
```

Evidence addresses показывают, какие bodies прочитаны для X/Y. Serialized edge
показывает, где и как relation реально записана. Эти адреса могут иметь разную
granularity: для hard edge точный upstream X может жить в section, а local
contract — сериализовать dependency file-level. Reverse traversal следует
serialized hard edges, не всем reader locators.

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
3. local graph contract для relation class и допустимых serialized endpoints;
4. только те upstream/downstream sections, которые способны изменить verdict.

Heading, description, link label, metadata key, similarity и graph direction
выбирают чтение, но не заменяют body evidence. Local `source-of-truth-for`,
Rule IDs или contract markers полезны как addressable signals, а не
универсальная authority schema.

Section-level evidence не требует section fragment в самой ссылке или
dependency. Проверяй независимо:

- достаточно ли точен evidence address для attribution и X/Y;
- является ли serialized endpoint минимальным стабильным endpoint, разрешённым
  local graph contract.

File-level endpoint может быть sound при section-specific evidence; fragment,
stable ID или composite locator также может быть sound, если этот dialect
разрешён. Если local endpoint contract не прочитан, endpoint verdict остаётся
`unread`: не повышай granularity по догадке.

## Admission Test

Проверь шесть вопросов.

### 1. Attribution fit

Закрой конструкцию:

> В holder evidence address конкретный **Y** приписывает target evidence address
> смысл, authority, support или constraint **X**.

Target body действительно утверждает X в том же смысле и при тех же
ограничениях. Тематическая близость не проходит тест.

### 2. Direction

Holder применяет, цитирует, ограничивает или навигирует к target. Если target
на самом деле делегирует X holder-у, relation развёрнут или ownership спорен.

### 3. Serialized endpoint fit

Endpoint должен обозначать правильного semantic owner-а и быть минимальным
стабильным endpoint внутри разрешённого local dialect. Более granular не значит
лучше: точный evidence section и file-level dependency совместимы.

`Retarget` нужен, когда записанный endpoint ведёт к неверному owner-у, устарел
или нарушает local endpoint contract. Он не означает автоматически «дописать
`#section`». Непрочитанный dialect не разрешает mutation.

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
случай тоже material только после двух проверок: X/Y-test пройден и local graph
contract допускает hard relation с выбранным serialized endpoint. Иначе не
`reclassify`, а `unread` либо сохранение более слабой relation.

### 6. Consistency

Bodies совместимы по term meaning, scope, units, state, authority и lifecycle.
Clear owner + stale consumer — обычный repair. Два конкурирующих owner-а или
несовместимые инварианты — `conflict`.

## Non-implications

- locator не является prose link;
- locator consumer не является hard dependency;
- direct-read job не доказывает invalidation;
- marker не доказывает missing graph edge.

Не создавай locator или marker только ради уточнения graph edge. Addressability
admission и edge admission — разные решения локального corpus-а.

## Edge Verdicts

- `sound` — evidence, endpoint dialect, attribution, direction, necessity и
  strength согласованы;
- `retarget` — relation нужна, но serialized endpoint должен обозначать другого
  owner-а или другую разрешённую local endpoint form;
- `reclassify` — relation job или сила неверна, а local contract разрешает
  новую class;
- `remove` — decorative, duplicate, stale или misleading edge без
  самостоятельной information job;
- `missing` — конкретный holder Y использует target X, но нужной relation job
  нет; locator, marker или direct-read address сам по себе этого не доказывает;
- `conflict` — linked bodies или owner claims несовместимы, и локальный repair
  edge-а не разрешает authority;
- `unread` — body evidence или local relation/endpoint contract ещё не
  прочитаны; это очередь, не verdict.

Для каждого verdict сохрани attribution, evidence addresses и serialized edge
отдельно. Batch verdict по file names, snippets или graph rows недопустим.

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
