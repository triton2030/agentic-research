# Roadmap

## Current Aim

Keep the repository structurally clear with three root domains: `knowledge/` for all durable research and reference, `projects/` for agents/skills/plugins grouped by category, `ops/` for the operational layer.

## Current Phase

Structural split `knowledge / projects / ops` is in place (refactor 2026-04-19). The next phase is to strengthen the content inside each domain without blurring the new boundaries.

## Key Principles And Constraints

- `knowledge/` holds everything durable: wisdom, guides, examples, per-category research and inventory.
- `projects/{category}/{slug}/` holds only agents, skills, and plugins. No research files mixed in.
- `ops/` is a working folder for the project, not a research archive.
- Base files (wisdom-*.md, perfect-*.md, AGENTS.md) should stay lean and durable.
- Cross-cutting ideas stay in `knowledge/` top level; category-specific ideas live in `knowledge/research/{category}/`.

## Active Bets

- Clear `knowledge / projects / ops` split will reduce future confusion and repeated cleanup.
- `knowledge/research/meta/` is the right home for cross-cutting research on agents, meta-agents, and thinking-oriented skills.
- Case-based evidence (examples + inventories) matters more than elegant theory when deciding what to formalize later.
- `knowledge/examples/` as a pull source for future prompt/skill writing will pay off as the corpus grows.

## Near-Term Horizon

- Build evidence-based notes inside `knowledge/research/meta/`, beginning with `ops` and meta-agents.
- Add new agents and skills as separate projects inside `projects/{business,design,dev,meta}/`.
- Define the rule for when a research insight should move into the stable base layer (`wisdom-*`, `perfect-*`).

## Not Now

- One mega-folder for every kind of agent research.
- Exhaustive taxonomy before the core boundaries are stable.
- Large volumes of notes without a clear question or decision value.
