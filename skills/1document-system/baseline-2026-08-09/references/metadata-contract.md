# Metadata Contract

Metadata помогает агенту найти artifact и понять authority/lifecycle. Не
превращай её в дублирующую анкету.

Весь live local metadata contract сильнее этого fallback: набор и отсутствие
полей, допустимые authority/status values, identity, link policy и approval
semantics применяются целиком. Не нормализуй локальную schema по отдельным
defaults ниже.

## Contents

- [Required Core](#required-core)
- [Description As Retrieval Surface](#description-as-retrieval-surface)
- [Conditional Fields](#conditional-fields)
- [Approval](#approval)
- [Missing Sections](#missing-sections)
- [Zone Semantics](#zone-semantics)
- [md-tools Adapter Boundary](#md-tools-adapter-boundary)

## Required Core

Только при отсутствии live local metadata contract требуй семь полей для файлов
в `canon/` и typed standard artifacts в `_ops/`, включая DEC, EDD, RSP, EXP и
Documentation System Map. Plans, backlog, findings и instruction files следуют
своим local owner contracts:

```yaml
---
artifact-id: mavo-prd-personalization
description: Определяет продуктовые требования управляемой персонализации.
artifact-type: prd
authority: canon
artifact-scope-key: personalization
status: active
approved: false
---
```

Единственное исключение для `description`: live local contract явно запрещает
это поле. Тогда не добавляй его и используй только названный тем же contract
alternative retrieval label. Если альтернативы нет, не выдумывай новое поле:
зафиксируй `retrieval-label-unavailable` в closeout и не заявляй artifact или
projection retrieval-ready. Content/authority validation может завершиться с
этим bounded retrieval gap; сам запрет не создаёт противоречивое требование
одновременно добавить и удалить `description`.

- `artifact-id`: читаемый immutable kebab-case ID; move/rename его не меняет.
- `description`: одна различающая routing-фраза; quality contract ниже.
- `artifact-type`: lowercase code global catalog, reserved system type или
  local registry. Filename продолжает использовать uppercase display code.
- `authority`: `evidence`, `decision`, `canon`, `projection` или `ops`.
- `artifact-scope-key`: стабильный логический scope.
- `status`: `draft`, `active`, `superseded` или `archived`.
- `approved`: личная отметка пользователя, не trust/authority gate.

Для plural types делай `artifact-scope-key` instance-specific (`checkout-tax`,
а не просто `project`). Начальная формула ID — construction convention, не
вычисляемое поле: после создания ID не меняется. При исторической коллизии добавь
читаемый identity suffix и никогда не переиспользуй старый ID.

Для active `authority: canon` допускай один artifact на
`artifact-type + artifact-scope-key`.

## Description As Retrieval Surface

Default `description` должен позволять агенту выбрать файл среди соседей до
чтения body. При local prohibition те же требования применяются к явно
назначенному alternative retrieval label. Одной ясной фразой назови:

- information job — какой изменяемый ответ, contract или evidence здесь ищут;
- bounded scope — к какому продукту, процессу, решению или вопросу он относится;
- различие с near-miss artifact, если по первым двум пунктам возможна коллизия.

Фраза должна быть понятна без filename и headings. Не оставляй `TODO`, не
повторяй title/path, не пиши generic «документ о X», не перечисляй оглавление и
не превращай поле в полный summary.

`1md-read` показывает description в filesystem maps, а `1md-search` индексирует
непустое поле отдельным `descriptions` item и использует его как context для
section embeddings. Поэтому пустой или расплывчатый description — retrieval
defect, а не косметика. При этом description, similarity и rank остаются
routing signals: claims, owner и authority подтверждай чтением body и live
project contract.

## Conditional Fields

Добавляй только при реальной функции:

```yaml
workflow-state: accepted
depends-on:
  - "[[../canon/OPM — Operating Model — Project.md#Money Flows]]"
derived-from:
  - ../canon/RPT — Research and Evidence Report — Buyers.md
supersedes:
  - project-prd-personalization-v1
owner: product
```

- `workflow-state`: type-specific state, отдельный от file lifecycle.
- `depends-on`: только hard invalidation edge holder → source. Добавляй, если
  изменение конкретного X может сделать Y в holder ложным. При активном
  `md-tools` используй quoted wikilink `"[[path#Heading]]"`; anchor уточняет
  evidence, но текущий cascade остаётся file-level.
- `derived-from`: lineage/provenance; не создаёт update obligation.
- `supersedes`: явная замена прошлого artifact того же logical owner-а.
- `owner`: только когда разные люди/роли действительно имеют разные права
  изменения; не повторяй `triton` во всех личных файлах.

Без иного live local contract не храни вручную reverse dependents, path,
modified date, validation result, generic `last-reviewed`, required sections,
`primary-reader` или `decision-enabled`. Локальный owner может назначить этим
полям реальную функцию; тогда его contract сильнее этого default.

## Approval

Считай ясный положительный ответ пользователя (`отлично`, `всё верно`,
`принимаю`) approval только когда он однозначно относится к текущему artifact;
не переноси praise о процессе или плане на файл. Любая смысловая правка claims,
decisions, requirements, scope, sections или dependencies ставит
`approved: false`. Formatting, typo и broken-link repair не сбрасывают его.
Active artifact при этом остаётся active. Approval не меняет retrieval.

## Missing Sections

Форму missing section назначает live local section contract: он может требовать
не создавать пустой heading либо сохранить его с собственным marker и enum.
Только при отсутствии такого contract сохраняй heading и первой строкой ставь:

```text
SECTION-STATUS: unresolved | not-evidenced | not-applicable — причина
```

Не подменяй marker правдоподобным текстом и не дублируй список missing sections
во frontmatter.

## Zone Semantics

В `canon/` metadata обязательна; default authority — `canon` или `evidence`.
Decision/change artifacts обычно живут в `_ops/` с `authority: decision` или
`ops`; принятый outcome обязан обновить current canon owner. Documentation
System Map (`artifact-type: docs-system-map`) использует `authority: ops`.
Этот reserved system type не входит в 15 domain profiles.

В `projections/` полная schema необязательна, но retrieval-label contract и
lineage обязательны: Markdown по умолчанию держит различающий `description`,
`authority: projection`, `derived-from` и hard `depends-on` для maintained
current claims. Явный local prohibition `description` проходит только через
exception route выше; другой формат — один companion manifest или существующий
projection manifest. Metadata не даёт projection права владеть canon.

## md-tools Adapter Boundary

Portable artifact metadata не является текущей strict schema `md-tools`: его
scanner принимает только собственные graph fields и может вернуть
`UNKNOWN_FIELD` для `artifact-id`, `artifact-type`, `authority`, `status` и
`approved`. Этот schema — adapter contract графового runtime, а не ontology и
не универсальный whitelist metadata. `UNKNOWN_FIELD` означает отсутствие
нужного runtime profile, а не semantic запрет на поле.

При включённом strict scanner не удаляй нужные artifact fields, не подменяй их
на `depends-on` и не заявляй validation success. Зафиксируй
`runtime-schema-mismatch`; для повторяемой path-scoped семьи передай владельцу
runtime/profile минимальное расширение schema. До него считай совместимым
только фактически поддержанный field/format contract.

