# Phase 6 — Workflow recipes в SKILL.md

**Estimated cost**: ~0.5 дня
**Depends on**: P3 (Tier 1 ready) для navigator recipes ИЛИ P5 (Tier 2 ready) для full recipes
**Unblocks**: P7 (cleanup)

Применимые инструкции: `AGENTS.md` (project root), `CLAUDE.md` (project root), `_ops/AGENTS.md`. **Эта phase задевает skill prose surface — read `1instruction-layer/references/instruction-layer-invariants.md` если у `1instruction-layer` есть инвaarianty для skill prose.**

## Цель

В обоих SKILL.md (`1md-navigator`, `1md-graph`) добавить секцию **`## Workflow recipes`** с конкретными канонами «хочу X → делай Y → Z». Это **soft layer** который превращает MCP capabilities в видимый канонический путь для модели.

Без recipes модель видит 15 MCP tools, но не знает **как их компоновать**. С recipes модель видит «вот 7 канонических workflow». Это и есть main differentiator nashego стека: composite tools уже компонуют, recipes явно говорят когда какой composite брать.

## In scope

- 5-7 workflow recipes в `~/.claude/skills/1md-navigator/SKILL.md`
- 4-5 workflow recipes в `~/.claude/skills/1md-graph/SKILL.md`
- Mirror в Codex: `~/.codex/skills/1md-navigator/SKILL.md` + `~/.codex/skills/1md-graph/SKILL.md`
- Update trigger phrases в frontmatter `description` если новые workflow добавляют intent surface

## NOT in scope

- Удаление `scripts/` из skill folders — это P7
- Удаление CLI examples из SKILL.md — оставляем минимально для index/init/strip fallback
- Изменение `1md-navigator` / `1md-graph` boundary — boundary уже зафиксирован в task-001

## Definition of done

- 4 SKILL.md (Claude × Codex × navigator × graph) содержат `## Workflow recipes` секцию
- Каждая recipe в формате:
  ```markdown
  ### [Workflow name]
  **Когда**: trigger phrase / use moment
  **Composite call**: `md_X({ args })`
  **Что вернётся**: shape output
  **Дальше**: typical next step
  ```
- Trigger phrases в frontmatter description включают main intent verbs для каждой workflow
- Cross-runtime consistency: Claude и Codex versions identical content (modulo `1md-graph` vs `$1md-graph` references convention)

## Stop rules

- Если new Claude session не выбирает MCP tools первыми после P6 — recipes не работают, переоценить formulation
- Если recipes начинают повторять MCP tool descriptions (drift) — стоп, recipes должны быть **workflow**, не tool docs

## Подшаги

### P6.1 — Draft recipes для navigator (1 час)

**Файл**: `~/.claude/skills/1md-navigator/SKILL.md`

Insert после `## Tools (MCP)` секции (где сейчас минимальный 3-line stub):

```markdown
## Workflow recipes

### W1 — Понять незнакомый Markdown-корпус
**Когда**: новая сессия в новом repo, не знаю что в `knowledge/` / `docs/` / похожей папке
**Composite call**: `md_orient({ corpus: "/path", top: 10 })`
**Что вернётся**: index status + file list с in_degree/out_degree + top-10 important files
**Дальше**: pick важный файл → `md_read_related` для контекста

### W2 — Найти где обсуждается X
**Когда**: «где про X», «какой файл про Y», «есть ли content про Z»
**Atomic call**: `md_search({ corpus, query: "natural language" })`
**Если ищу файл а не section**: `md_search({ ..., scope: "descriptions" })`
**Что вернётся**: ranked sections с rrf_score, snippet
**Дальше**: `md_pick` для extract, или `md_read_related` для context вокруг top hit

### W3 — Обогатить понимание файла связанными блоками
**Когда**: открыл файл с wikilinks/markdown links, хочу понять с контекстом
**Atomic call**: `md_read_related({ paths: ["file.md"], scan: "corpus" })`
**По умолчанию**: anchor-aware — `[[file#Heading]]` тянет только эту секцию, не весь файл
**Cheap variant**: `mode: "preview"` — только descriptions/titles, no content
**Что вернётся**: anchor file + linked sections в одном packet
**Дальше**: если есть конкретный edit intent → switch к `md_edit_context` (W4)

### W4 — Refactor opportunities в корпусе (Tier 2)
**Когда**: хочу понять где дублируется, где можно заменить wikilinks
**Composite call**: `md_refactor_candidates({ corpus, top: 10 })`
**Что вернётся**: список proposals shape `{ proposal_type, affected_section, target_owner, evidence, confidence, why, no_automation: true }`
**Дальше**: editorial — для каждого proposal manual review, replace by wikilink ИЛИ explicit reject с обоснованием

### W5 — Найти все [open questions / decisions / definitions] (Tier 2)
**Когда**: «найди все TODO», «все decisions about X», «где определяется Y»
**Composite call**: `md_query_by_type({ corpus, types: ["open-question"] })`
**Что вернётся**: filtered sections с profile metadata
**Дальше**: pick relevant → `md_read_related` или `md_cat` для extraction

### W6 — Аудит здоровья корпуса
**Когда**: периодический check (раз в неделю/месяц), большая правка ожидается
**Composite call**: `md_audit({ corpus })`
**Что вернётся**: orchestrated report — overlaps + repeated-concepts + cluster + 0-100 health score (slow, ~minutes)
**Дальше**: для каждого finding — route к соответствующему workflow (refactor proposals для duplicates, etc.)

### W7 — Прочитать конкретные секции из saved map
**Когда**: уже получил map от `md_ls`/`md_toc`/`md_search`, хочу batch extract нескольких headings
**Atomic call**: `md_cat({ map_data, headings: "1.2,3.1", token_budget: 2000 })`
**Что вернётся**: section bodies в одном packet
**Note**: для one-file path use built-in Read tool — оно короче и identical

## CLI fallback

Все MCP composite/atomic tools имеют CLI equivalent через `md_navigator.py` (entry-script в repo). MCP — primary interface; CLI — для bootstrap (`md_navigator.py index <corpus>`), debug, и pre-commit hooks.

`index`, `profile-sections`, `init`, `strip` остаются CLI-only — mutating операции с costs (LLM calls), не подходят для MCP UX. После `md_orient` если status показывает NEEDS WARMUP — instruction tu user "run `md_navigator.py index <corpus>`".
```

**Update frontmatter description** добавить trigger phrases для new workflows (если ещё нет):

```yaml
description: >
  Semantic-first reader for any Markdown corpus...
  ...existing description...
  Workflow triggers: «о чём этот корпус», «понять корпус», «refactor opportunities»,
  «где дубли», «найди все open questions», «найди все decisions», «обогатить контекст».
```

### P6.2 — Draft recipes для graph (45 минут)

**Файл**: `~/.claude/skills/1md-graph/SKILL.md`

Insert после `## Tools (MCP)`:

```markdown
## Workflow recipes

### W4 — Я буду править file X (pre-edit safety)
**Когда**: substantive edit ожидается на конкретном файле, хочу понять что прочитать до и обновить после
**Composite call**: `md_edit_context({ path: "file.md", mode: "full", corpus?, query? })`
**Modes**:
- `preview` — только descriptions/titles, cheap
- `full` (default) — preflight + anchor-aware linked content + optional semantic search (если passed corpus+query)
- `strict` — только blockers (anchor-drift / missing-target / broken-link / cycles)
**Что вернётся**: graph preflight + related content + optional search в одном packet
**Дальше**: edit с учётом must-read и must-update; после edit — `md_preflight` ещё раз чтобы verify

### W5a — Удалить или переименовать файл
**Когда**: вижу что файл устарел или его надо перенести
**Atomic call**: `md_impact({ path: "file.md", scan: "corpus" })`
**Что вернётся**: cascade holders + reference holders + body wikilinks + body markdown links — каждый с descriptions
**Дальше**: если impact пустой — safe to delete; иначе update сначала всех holders, потом delete

### W5b — Переименовать секцию (heading rename)
**Когда**: heading text меняется, могут сломаться `[[file#Heading]]` links
**Composite call**: `md_section_blast_radius({ path: "file.md", corpus, query: "section meaning", heading_id?: "1.2" })`
**Что вернётся**: hard layer (graph anchor wikilinks) + soft layer (semantic neighbors — paraphrase, named citation)
**Дальше**: hard layer обязательства; soft layer — кандидаты на manual review

### W6 — Pre-edit safety check (graph slice only)
**Когда**: хочу только графовую часть, без content body (когда уже знаю содержимое)
**Atomic call**: `md_preflight({ path, scan?, depth? })`
**Что вернётся**: must-read / must-update / anchor-drift / cycles / has_blockers flag
**Дальше**: если has_blockers=true — resolve до edit'a; anchor-drift — signal, не blocker

### W7 — Здоровье графа целиком
**Когда**: периодический check, хочу понять orphans / hubs / cycles
**Atomic call**: `md_health({ paths?: ["corpus"] })`
**Что вернётся**: description coverage, top hubs, orphans, cycles
**Дальше**: orphans → consider delete или wire; cycles → bug, всегда чинить

## CLI fallback

Mutating commands (`init` add empty frontmatter, `strip` remove legacy fields) остаются CLI-only — `md_graph.py init <files>`, `md_graph.py strip <files>`. MCP не expose'ит mutating tools (destructive UX через MCP плохой).

`changed` для git-driven preflight также CLI — лучше как pre-commit hook чем MCP tool.
```

**Update frontmatter description** trigger phrases добавить:

```yaml
description: >
  ...existing...
  Workflow triggers: «я буду править X», «edit context», «pre-edit safety»,
  «удалить файл», «переименовать секцию», «blast radius», «здоровье графа».
```

### P6.3 — Mirror Codex versions (45 минут)

**Файлы**:
- `~/.codex/skills/1md-navigator/SKILL.md`
- `~/.codex/skills/1md-graph/SKILL.md`

Copy content из Claude version с **двумя адаптациями**:
1. Skill references меняются: `1md-graph` → `$1md-graph`, `1md-navigator` → `$1md-navigator`, `1cli-tools` → `$1cli-tools` (Codex convention из existing files)
2. Path examples могут отличаться — если в Claude `~/.claude/skills/...`, в Codex `~/.codex/skills/...`. Recipes используют MCP calls (paths не появляются в recipe body), так что divergence минимальный

Sanity check: `diff -y` Claude и Codex versions — должен показать только references differences.

### P6.4 — Update mcp/README.md tool catalog (15 минут)

В `experiments/md-embedding-server/mcp/README.md` добавить секцию **`## Workflow recipes`** (короче чем в SKILL.md, link на skills для detail):

```markdown
## Workflow recipes

See full recipes в `~/.claude/skills/1md-{navigator,graph}/SKILL.md` (workflow contracts).
Quick reference:

| Workflow | Composite tool | Skill |
|---|---|---|
| W1 orient unfamiliar corpus | `md_orient` | 1md-navigator |
| W2 find content | `md_search` | 1md-navigator |
| W3 read with context | `md_read_related` | 1md-navigator |
| W4 edit safety | `md_edit_context` | 1md-graph + 1md-navigator |
| W5a delete/rename file | `md_impact` | 1md-graph |
| W5b rename section | `md_section_blast_radius` | 1md-graph |
| W6 corpus health | `md_audit` | 1md-navigator |
| W7 refactor opportunities (T2) | `md_refactor_candidates` | 1md-navigator |
| W8 semantic-shape query (T2) | `md_query_by_type` | 1md-navigator |
```

### P6.5 — Manual verification (30 минут)

1. Start fresh Claude Code session
2. Trigger queries — model should auto-call MCP composites:
   - «Помоги понять что в `/path/to/knowledge`» → should call `md_orient`
   - «Я буду править `_ops/GOAL.md`, дай контекст» → should call `md_edit_context`
   - «Найди все open questions в knowledge» → should call `md_query_by_type` (if Tier 2 ready)
3. Same in Codex session (после restart)

**Acceptance**: model выбирает MCP tools, не Bash, в ≥4/5 test queries.

**If fails**: trigger phrases в SKILL.md недостаточно явны. Re-iterate recipes wording.

## Verification (общая для P6)

- [ ] 4 SKILL.md files обновлены с `## Workflow recipes` секцией
- [ ] Frontmatter description trigger phrases расширены где нужно
- [ ] Codex versions mirror Claude (modulo `$` prefix in references)
- [ ] `mcp/README.md` имеет workflow quick reference
- [ ] Fresh Claude session test: ≥4/5 test queries trigger MCP composite (not Bash)
- [ ] Fresh Codex session test: same

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Recipes drift от actual tool behavior | Each recipe — minimal viable description. Detail в MCP tool description, recipe — only «when to use» |
| Trigger phrases в frontmatter слишком жадные → skill overtrigger | Specific trigger words («refactor opportunities», «pre-edit safety», not «edit», «refactor») |
| Cross-runtime drift (Claude vs Codex versions) | `diff` check; document обe в task; consider periodic sync check (`md_navigator search _ops "skill workflow recipes"`) |
| Recipes становятся monolithic doc | Cap 5-7 recipes per skill. Сложные cases — отдельный reference file |

## Hand-off to P7

После P6 готов:
- Skills имеют workflow recipes — модель видит canonical path
- Cross-runtime синхронизированы
- MCP catalog обновлён

P7 теперь может: проверить что MCP стабилен через burn-in (≥1 real session usage без fallback к Bash), затем удалить `scripts/` из skill folders.

## Anchors / Evidence

- High-level контракт: `task-001-md-tools-unified-backend.md`
- Adversarial review insight: recipes как soft layer make MCP visible
- Existing skill folder structure: `~/.claude/skills/1md-navigator/`, `~/.codex/skills/1md-navigator/`, same for graph
- Boundary spec: navigator owns understanding workflows (W1-W3, W6, W7, W8), graph owns edit-safety (W4, W5)
