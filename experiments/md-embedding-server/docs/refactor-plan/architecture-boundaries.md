---
description: Architecture boundaries for md-tools-v2 modules and ownership.
depends-on:
- '[[public-capability-contract.md]]'
- '[[state-and-cost-model.md]]'
---
# Architecture Boundaries

Этот документ фиксирует границы до кода, чтобы v2 не стала ещё одной
папкой, куда добавляют всё подряд.

## Предварительные Слои

| Слой | Владеет | Не владеет |
|---|---|---|
| `markdown-core` | чтение файлов, frontmatter, sections, headings, links | embeddings, MCP, skill policy |
| `index-search` | index schema, embeddings, BM25/dense/RRF, search results | graph obligations, audit doctrine |
| `graph` | depends-on, impact, cycles, schema health | semantic verdict, IA shape |
| `audit` | overlaps, repeated concepts, drift signals, corpus health candidates | automatic refactor decisions |
| `profile` | section typing/classification cache | public workflow choices |
| `mcp-adapter` | tool schemas, transport, annotations, text/structured result shape | backend semantics |
| `cli-admin` | debug/admin commands, migrations, local checks | primary agent workflow |

## Boundary Rules

- MCP не должен владеть cost, dry-run or graph truth. Он вызывает backend
  contract and exposes it.
- Audit не должен быть частью search core.
- Graph не должен доказывать semantic completeness.
- Skill workflow остаётся в skills, не в backend.
- Compatibility aliases не становятся местом для новой логики.
