# Projections

`projections/` — свободная reader-facing зона. Здесь разрешены контролируемые
дубли canon, HTML, diagrams, decks, canvases и любые удобные форматы. Папка
сообщает, что это view; lineage доказывает, из какой истины view получен.

## Единственная Жёсткая Граница

Каждая projection обязана иметь traceable `derived-from`, включающий relevant
current canon или durable evidence. Дополнительно можно ссылаться на DEC, plan
или risk для rationale/future narrative, но current claim не должен опираться
только на ops. Перед созданием/обновлением прочитай sources. Для Markdown
используй минимальный frontmatter:

```yaml
---
description: Объясняет checkout scope и ограничения для внешнего product reader.
authority: projection
derived-from:
  - "[[../canon/product/PRD — Product Requirements Document — Checkout.md]]"
depends-on:
  - "[[../canon/product/PRD — Product Requirements Document — Checkout.md#Scope]]"
---
```

`description` — default retrieval label для Markdown projection: одной фразой
назови reader-facing information job и bounded scope. Явный local prohibition
поля обрабатывай только по exception route из
[metadata-contract.md](metadata-contract.md). Retrieval label помогает
`1md-search` выбрать view, но не делает его canon или evidence.
`derived-from` фиксирует lineage. Для maintained current view добавь
`depends-on` на каждую source-section, изменение которой может сделать claim
ложным. Dated snapshot может не иметь update edges, только если явно хранит
`as-of` boundary и исключён из current projection retrieval.

Для PDF, deck, image или другого формата без metadata создай/обнови один
companion source manifest либо зарегистрируй lineage в существующем projection
manifest. Не создавай manifest-system ради одного artifact, если native source
file уже хранит lineage.

Projection может менять порядок, emphasis, prose и visual explanation для
reader-а. Она не может добавлять новую mutable product truth, усиливать
hypothesis до fact, скрывать material contradiction или переопределять owner.

После generation/update сравни factual claims с sources. Conflict блокирует
готовность; отсутствующая опора помечается `not-evidenced` либо claim удаляется.
Если hard source содержательно изменился после последней проверки, projection
stale до повторной сверки. Folder и свежая дата сами по себе freshness не
доказывают.

Не используй projection как источник для canon, decision или evidence. Если
утверждение нужно вернуть в truth-bearing документ, найди исходный source или
пометь его `not-evidenced`. Default retrieval и refactor inventory игнорируют
projection content.

Полная metadata и standard section schema здесь не обязательны;
retrieval-label outcome по metadata contract, lineage и contradiction check
обязательны. Форматную реализацию передавай подходящему skill/tool, не раздувая
`1document-system` правилами HTML, slides или PDF.

## Optional Recipes

Используй только когда они помогают reader outcome:

- **Lean Canvas:** problem, segments, UVP, solution, channels, revenue, costs,
  key metrics, unfair advantage.
- **Value Proposition Canvas:** customer jobs, pains, gains; products/services,
  pain relievers, gain creators.
- **Customer Journey Map:** actor, scenario, stages, actions, touchpoints,
  emotions, friction, opportunities.
- **External Brief / Deck:** audience decision, narrative, evidence, model,
  differentiation, risks, milestone, ask.
- **HTML / Executive View:** reader question, concise synthesis, navigation back
  to canon owners.

Recipe не создаёт standard artifact type и не входит в local registry. Готовая
projection названа reader-view, перечисляет sources и не содержит unsupported
current claims.

