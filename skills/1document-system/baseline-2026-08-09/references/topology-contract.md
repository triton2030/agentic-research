# Topology Contract

Распределяй документы по роли относительно истины, а не по удобству текущего
автора:

```text
canon/       = что истинно или известно сейчас
_ops/        = как истина строится, меняется, проверяется и откладывается
projections/ = как истина показывается конкретному читателю
```

Local live convention выигрывает. В существующем проекте сначала сопоставь её
этим ролям; не создавай параллельное дерево без target mapping.

## Zone Contract

| Zone | Владеет | Не владеет | Default retrieval |
| --- | --- | --- | --- |
| `canon/` | Current requirements, rules, models, contracts и durable evidence | Plans, rationale history, reader narrative | Да |
| `_ops/` | Goal, plans, backlog, findings, audits, decisions, change designs, running research/experiments, risks и documentation control | Current product/business/system truth | Только по вопросу о работе, изменении или rationale |
| `projections/` | Audience-specific composition, prose и visual views | Независимая factual/specification truth | Нет |

`DEC` хранит почему выбор сделан; если принятый результат меняет current truth,
обнови подходящий canon owner. `EDD` описывает планируемое изменение; после
реализации обновляются `ARCH`, `API`, `DOM`, `SEM` или другие current owners.
Не оставляй действующую истину только в `_ops/`.

Durable `RPT` и concluded evidence-part `EXP` могут жить в
`canon/evidence/` с `authority: evidence`. `RSP` и planned/running `EXP` живут в
`_ops/`. Это отделяет наблюдаемое знание от процесса его получения.

## Default Homes

Используй home из [catalog.md](catalog.md), если local registry не сильнее.
Служебные homes:

- `DOCS`, `MIG` → `_ops/documentation/`;
- project goal → `_ops/GOAL.md` через `1goal`;
- active/deferred work → `_ops/plans/`, `_ops/backlog/` через `1planning`;
- collateral defects → `_ops/findings/` через `1findings`;
- local admitted risks → `_ops/risks/`;
- instruction rules → live instruction hierarchy через `1instruction-shaping`.

Не создавай эти folders заранее. Материализуй home вместе с первым current
artifact, который действительно туда попадает.

## Canon Folder Algorithm

Filename уже кодирует genre; folder кодирует стабильный domain/capability owner.

1. Сохрани один текущий owner на `artifact-type + artifact-scope-key`.
2. Пока весь canon образует один coherent owner zone, допустим flat root.
3. Когда текущие artifacts принадлежат разным domain owners или регулярно
   читаются/проверяются разными потоками, используй `canon/<domain>/`.
4. На одном уровне применяй одну ось. Не смешивай folders по type, audience,
   status и domain.
5. Не создавай type-folder только потому, что существует template: code уже
   виден в имени. Type-axis допустим только при доказанном local retrieval flow.
6. Folder может начаться с одного artifact, только если сам domain boundary уже
   current и independently routed; ожидаемые будущие siblings этого не доказывают.
7. Если регулярны две оси чтения, выбери один truth-axis, а вторую реализуй
   projection/MOC. Не дублируй файл в двух homes.

Иллюстрация, не обязательная taxonomy:

```text
canon/
├── business/    # MRD, OPM
├── product/     # PRD, BRC, SEM, DOM
├── technology/  # ARCH, API
└── evidence/    # RPT, concluded EXP evidence
```

## Router And Retrieval

Documentation System Map остаётся compact link-first router: question → owner
path, admitted type и lifecycle. Он не повторяет product rules, requirements,
tables или rationale.

- Current-truth question → `canon/`.
- Why/when was this chosen? → `_ops/decisions/`.
- What is planned, blocked or being checked? → relevant `_ops/` owner.
- How should this read for an audience? → `projections/`, then its canon lineage.

Перед завершением проверь: нет empty/future folders; нет mixed folder axes; ops
не стал единственным current owner; System Map не стал вторым canon; projection
имеет traceable lineage и не участвует в truth retrieval.

