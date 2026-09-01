---
description: "Admission test and verdicts for semantic correctness, necessity, strength and delta impact of one cross-file Markdown edge."
---

# Semantic Edge Audit

Contents: Unit · Relation jobs · Evidence · Admission test · Non-implications ·
Verdicts · Delta impact · Conflicts and cycles · Stop.

## Unit

Аудируй не URL и не carrier отдельно, а каждый attribution atom. Один
serialized carrier может нести несколько claims с разными target meanings,
jobs и impacts; сначала раздели их, затем выноси atom verdicts и только потом
carrier disposition.

```text
semantic question: ...
incoming delta: X0 → X1 | not-applicable
serialized carrier: <location + link/relation type + endpoint> | absent
holder evidence: HOLDER#section
holder claim Y: ... <scope/modality/authority/lifecycle>
target evidence: TARGET#section | honest file-level body
target claim X: ... <scope/modality/authority/lifecycle>
endpoint dialect: <allowed local forms> | unread
relation job: ...
attribution: holder claims target owns/supports/constrains ...
weaker/null counterframe: ...
discriminator evidence: ...
evidence-state: unread | read-sufficient | read-insufficient | read-conflicting
atom verdict: ...
impact: ...
outgoing holder delta: ΔY | none | undetermined
```

Evidence addresses показывают прочитанные bodies; serialized carrier — где и
как relation записана. Они могут иметь разную granularity: exact upstream X
может жить в section, а local contract — сериализовать dependency file-level.
Reverse traversal следует serialized hard edges, не всем reader locators.

Mixed carrier сообщается как mixed: atom verdicts и impacts остаются видимыми.
Не превращай один `affected` atom в разрешение менять все claims файла.

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

Извлекай стороны независимо: сначала Y из holder body без принятия target label
за ответ, затем X из target body без принятия holder intent за authority.
Сохраняй scope, modality, units, state, authority и lifecycle. После attribution
построй weaker/null counterframe и назови body evidence, которое его отличает.
Если rival и attribution одинаково совместимы с прочитанным,
`read-insufficient`, не `unread` и не уверенный verdict.

Section-level evidence не требует section fragment в самой relation. Проверяй
независимо evidence address и minimal stable serialized endpoint, разрешённый
local dialect. Непрочитанный dialect не разрешает mutation.

## Admission Test

Проверь семь gates по каждому atom.

### 1. Atomization

Назови один Y, один X и одну relation job. Если carrier сопровождает несколько
самостоятельных claims, раздели их до verdict. Общий endpoint не доказывает
одинаковый смысл, силу или impact.

### 2. Attribution And Counterframe

Закрой конструкцию:

> В holder evidence address конкретный **Y** приписывает target evidence address
> смысл, authority, support или constraint **X**.

Target body действительно утверждает X в том же смысле и при тех же
qualifiers. Затем сформулируй weaker/null rival: target только тематически
связан, поддерживает более узкий claim или не нужен этому Y. Укажи exact body
evidence, различающее версии. Без discriminator: `read-insufficient` +
`undetermined`; тематическая близость тест не проходит.

### 3. Direction

Holder применяет, цитирует, ограничивает или навигирует к target. Если target
на самом деле делегирует X holder-у, relation развёрнут или ownership спорен.

### 4. Serialized Endpoint Fit

Endpoint должен обозначать правильного semantic owner-а и быть minimal stable
endpoint внутри разрешённого local dialect. Более granular не значит лучше:
exact evidence section и file-level dependency совместимы.

`Retarget` нужен, когда endpoint ведёт к неверному owner-у, устарел или нарушает
local endpoint contract. Он не означает автоматически «дописать `#section`».

### 5. Necessity

Назови information job, которая исчезнет после удаления edge:

- owner/definition станет неадресуемым;
- evidence/provenance перестанет быть проверяемым;
- dependency не попадёт в propagation review;
- составная мысль потеряет обязательный reader path.

Если ни одна job не исчезает, edge декоративный, дублирующий или stale.
Optional navigation может оставаться sound только с честным navigation intent.

### 6. Concrete Strength Counterfactual

Hard edge требует допустимого изменения upstream predicate:

> Если target изменится из **X₀** в **X₁**, какой exact **Y** станет ложным или
> misleading и во что он должен измениться (**ΔY**)?

`X₀ → X₁` должно быть конкретным и сохранять роль target-а. Фраза «если X
materially изменится» без `X₁` и `ΔY` не проходит. Downgrade до weaker relation
допустим, когда attribution полезна. Upgrade material только после concrete
test и чтения local relation/endpoint contract.

### 7. Consistency And Sufficiency

Bodies совместимы по term meaning, scope, units, state, authority и lifecycle.
Clear owner + stale consumer — обычный repair. Два конкурирующих owner-а или
несовместимые инварианты — `read-conflicting` + `conflict`. Bodies, которые не
различают rival interpretations, дают `read-insufficient` + `undetermined`.

## Non-implications

- locator не является prose link;
- locator consumer не является hard dependency;
- direct-read job не доказывает invalidation;
- marker не доказывает missing graph edge.

Addressability admission и edge admission — разные решения local corpus-а.

## Edge Verdicts

- `sound` — evidence, endpoint dialect, attribution, direction, necessity и
  strength согласованы;
- `retarget` — relation нужна, но endpoint должен обозначать другого owner-а
  или другую разрешённую local form;
- `reclassify` — relation job или сила неверна, а local contract разрешает
  новую class;
- `remove` — decorative, duplicate, stale или misleading edge без
  самостоятельной information job;
- `missing` — конкретный holder Y использует target X, но нужной relation job
  нет;
- `conflict` — linked bodies или owner claims несовместимы, и локальный repair
  edge-а не разрешает authority;
- `undetermined` — bodies прочитаны, но evidence не различает допустимые
  attribution/counterframe, strength или impact interpretations.

`unread` — evidence-state и очередь, не semantic verdict. Для compatibility его
можно показать в verdict column, но рядом обязателен `evidence-state: unread`;
не смешивай его с `read-insufficient`.

Для каждого verdict сохрани attribution, evidence addresses и carrier отдельно.
Batch verdict по file names, snippets или graph rows недопустим.

## Delta Impact

Edge verdict и impact-status независимы:

- `affected` — эта delta target-а изменяет Y holder-а;
- `unaffected` — edge остаётся sound, но delta не касается применяемого X;
- `undetermined` — bodies прочитаны, но влияние delta не различено;
- `unread` — impact не проверен;
- `not-applicable` — edge audit идёт без конкретной delta.

Для `affected` выведи минимальный holder change `ΔY`. Следующий reverse hop
получает именно `ΔY` как incoming delta, а не исходную `ΔX`, file name или общий
label `affected`. Без `ΔY` propagation не доказан. `unaffected` останавливает
ветвь; `undetermined`/`unread` останавливает mutation и требует handoff.

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
`conflict` и вынос владельцу: этот выбор есть установление, и его не
делает ни один скил.

SCC сам по себе не verdict. Если каждое edge связывает разные, совместимые
инварианты, cohort может быть sound и требует совместного review. Propagation
по SCC веди worklist-ом до fixpoint: enqueue только новый конкретный delta,
полученный из `ΔX → ΔY`. Если local contract явно запрещает cycles, structural
blocker действует независимо от semantic verdict.

## Stop

Стоп, когда denominator carriers назван, каждый selected carrier разложен на
atoms, обе стороны каждого atom прочитаны либо `unread` передан,
evidence-state, verdict и impact-status записаны, для каждого `affected` выведен
и закрыт `ΔY`, а conflict/undetermined получил owner handoff.

Не распространяй этот stop на непросмотренный corpus или open-world missing
edges.
