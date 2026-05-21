# mcp-self-sufficiency

Сделать `md-mcp` **самодостаточным продуктом**. Скилы — overlay, не gatekeeper. Агент в любом проекте читает `listTools`, видит self-explanatory descriptions, зовёт нужное без установки скилов.

## Зачем

После md-tools-refactor (2026-05-21) у нас 19 MCP tools и backend единый. Но:

1. **MCP не покрывает CLI surface** — `overlaps`, `cluster`, `repeated-concepts`, `scan`, `check`, `cycles`, `changed`, `index`, `init`, `strip`, `profile-sections` живут только в CLI. Агент в типичной IA-работе вынужден писать Bash — это противоречит цели «MCP дешевле Bash по токенам».
2. **Descriptions короткие** — текущие tool descriptions не учат `WHEN`/`WHY`/`WHAT`/`WHAT IF NOT`. Агент без скила не разберётся когда что брать.
3. **Скилы дублируют MCP framing вместо overlay** — current SKILL.md повторяют что делает MCP вместо того чтобы учить **когда применять / как интерпретировать**.

## Что строим

**MCP surface ~27 public tools**:
- 6 composite primary
- 17 atomic (navigation/content/graph/IA-probes/git)
- 4 mutating с guards (`confirm: true` / `dry_run`)

**Self-sufficient design contract** для каждого описания:
- `WHEN` — триггер (когда звать)
- `WHY` — почему лучше Bash альтернативы
- `WHAT` — output shape preview
- `WHAT IF NOT` — failure mode / cost

**Skills overlay** (16 SKILL.md = 8 скилов × 2 платформы): учат **когда применять / как интерпретировать**, не дублируют tool spec.

## Стадии

| Phase | Файл | Owner | Параллель | Зависит от |
|---|---|---|---|---|
| **A** Backend expansion | [`phase-a-backend-expansion.md`](phase-a-backend-expansion.md) | 1 subagent (sequential work) | — | — |
| **B1** Navigator+Graph skills | [`phase-b1-navigator-graph.md`](phase-b1-navigator-graph.md) | subagent | parallel с B2/B3/B4 | A done |
| **B2** IA+Folder skills | [`phase-b2-ia-folder.md`](phase-b2-ia-folder.md) | subagent | parallel | A done |
| **B3** Instruction+Planning skills | [`phase-b3-instruction-planning.md`](phase-b3-instruction-planning.md) | subagent | parallel | A done |
| **B4** Strategy+Review skills | [`phase-b4-strategy-review.md`](phase-b4-strategy-review.md) | subagent | parallel | A done |
| **C** Final sweep + cross-runtime check | [`phase-c-final-sweep.md`](phase-c-final-sweep.md) | parent session | — | B1-B4 done |

## Surface — что войдёт в MCP

| Категория | Tools | Status |
|---|---|---|
| **Composite primary** | `md_orient`, `md_edit_context`, `md_section_blast_radius`, `md_audit`, `md_refactor_candidates`, `md_query_by_type` | Exists (6) |
| **Atomic navigation/content** | `md_status`, `md_ls`, `md_toc`, `md_search`, `md_extract` (← merge pick+cat), `md_read_related`, `md_importance` | 6 exist, 1 to merge |
| **Atomic graph** | `md_preflight`, `md_impact`, `md_deps`, `md_health`, `md_cycles`, `md_check`, `md_scan` | 4 exist, 3 new |
| **Atomic IA probes** | `md_overlaps`, `md_repeated_concepts` | 2 new |
| **Git-driven** | `md_changed` | 1 new |
| **Mutating с guards** | `md_index`, `md_init`, `md_strip`, `md_profile_sections` | 4 new (with confirm/dry_run) |
| **Server** | `md_ping` | Exists |

Cut from previous proposal: `md_cluster` standalone (доступен через `md_audit` composite), `md_pick`+`md_cat` (merge в `md_extract`).

## Self-sufficient description template

Каждый tool description после rewrite:

```
md_<name>
---------
<one-line action>.

WHEN: <trigger phrases / situations>
WHY OURS: <vs Bash alternative — what we add>
INPUT: <main params + defaults>
OUTPUT: <shape preview, key fields>
ALT: <when to prefer composite / другой tool>
COST/RISK: <only for mutating / cost-bearing>
```

## Что меняется в скилах

Каждый из 8 скилов (`1folder-contract`, `1ia-audit`, `1instruction-layer`, `1planning`, `1strategy`, `1work-review`, `1md-graph`, `1md-navigator`) — **2 платформы × 1 SKILL.md = 16 файлов**.

После rewrite:
- SKILL.md описывает **когда** брать MCP tool под workflow + **как интерпретировать** output
- НЕ описывает input schema (это в MCP)
- НЕ показывает CLI invocations как primary (CLI только если MCP нет equivalent)
- Composite-first где композит реально дешевле, atomic-first где композит overkill

## Definition of done

- MCP version `0.6.x` с 27 public tools
- Smoke 100% passes (+ ~13 new assertions)
- Self-sufficient descriptions для всех 27 tools
- 16 SKILL.md обновлены overlay-style
- Cross-runtime: fresh Claude + Codex sessions видят весь surface через MCP
- `experiments/md-embedding-server/mcp/README.md` обновлён final catalog
- `_ops/PROJECT-ROADMAP.md` отражает completion

## Stop rules

- Backend smoke ломается на любой phase — rollback, не продолжать
- Mutating guard design не работает (agent обходит confirm) — escalate в `1strategy`, переосмыслить
- Описания приводят к overtriggering / undertriggering — calibrate before locking
- User меняет scope/done — escalate в `1strategy-docs`
