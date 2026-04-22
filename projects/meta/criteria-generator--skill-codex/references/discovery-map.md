# Discovery Map

Extended patterns for the strategic-grounding phase of `criteria-generator`. Use this file only after the default probe list in `SKILL.md` is already understood.

Do not duplicate the canonical default probes here. This file is for extensions and task-type adaptations only.

## Main-Strategy Plan & Preferences

If `CWD/_ops/PROJECT-PLAN.md` and `CWD/_ops/INTERVIEW.md` exist, prefer them early in discovery for major execution tasks. Treat them as upstream truth from `main-strategy`, then translate only the parts that materially change the contract.

Read the sections this way:

- `Goal` in `_ops/PROJECT-PLAN.md` -> defines the durable outcome and proof floor the task should serve
- Active `Stage` in `_ops/PROJECT-PLAN.md` -> calibrates what matters now versus later; its Steps often become scope constraints or Must items
- `Approach & Why` -> names the current approach the task should not quietly contradict
- Optional `Anti-goals` in PROJECT-PLAN -> often become Must-not items
- Relevant preference sections in `_ops/INTERVIEW.md` (tone, must-nots, style preferences tied to the domain) -> translate into Must or Must-not anchored in the specific INTERVIEW section

If `CWD/_ops/learnings.md` exists, read it only when a recorded delta (Expected / Actual / Delta) changes what good execution means for this task. Use deltas to sharpen verification depth or flag known bypass risks.

Do not paste whole sections into the contract. Convert only the lines that change completion, forbidden shortcuts, or verification depth.

## Main-Strategy Folder Routing

If the strategic map or repo instructions already fix canonical domains, let that map choose where to look next instead of treating every top-level folder as equally likely.

Default downstream read order in a repo shaped like this one:

- `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md`, `_ops/learnings.md` for current plan, preferences, and recorded deltas when they exist
- `knowledge/` for reusable canon, guides, and category learnings
- `projects/` for the concrete agent, skill, or plugin line being touched

Route by intent:

- repo-wide rule, canon, or reusable pattern -> `knowledge/`
- concrete artifact line -> matching `projects/{category}/...`
- current bet, anti-goals, preference constraint, or recorded delta -> the relevant `_ops/*.md` file when it exists

If one concrete project folder is implicated, read it before sibling project folders. Do not widen to broad repo scans unless the first folder fails to explain what "good" means.

## By project type

### Node / TypeScript repo

- `package.json` — scripts, dependencies shape the verification protocol.
- `tsconfig.json` — strictness affects what "passes" means.
- `.eslintrc*`, `.prettierrc*` — style constraints become Must-not items.
- `tests/`, `__tests__/`, `*.test.*` — existing test patterns to match.

### Python repo

- `pyproject.toml` / `setup.py` / `requirements*.txt`
- `pytest.ini`, `tox.ini`, `conftest.py`
- `mypy.ini`, `.ruff.toml`

### Go repo

- `go.mod`, `go.sum`
- `Makefile` if present
- `*_test.go` patterns

### Rust repo

- `Cargo.toml`
- `tests/`, `benches/`
- `clippy.toml`

### Docs-only / knowledge repo

- Start from the canonical domains declared by repo instructions or the strategic map, not from generic root scans.
- `_ops/PROJECT-PLAN.md`, `_ops/INTERVIEW.md`, `_ops/learnings.md` for current plan, preferences, and concrete deltas when they exist.
- `knowledge/wisdom-*.md` for durable cross-cutting rules.
- `knowledge/guides/*` for stronger format and context patterns.
- `knowledge/research/{category}/learnings.md` for category-specific learnings.
- `projects/{category}/...` for the concrete agent/skill/plugin line being touched.
- Legacy `_`-prefixed folders only when they actually exist in this repo.
- `MKDocs.yml`, `mkdocs.yaml`, `docusaurus.config.*`, `astro.config.*`.
- Any `CONTRIBUTING.md`, `STYLE.md`.

### Claude Code plugin / skill project

- `.claude/settings.json`
- `plugins/*/plugin.json`
- `skills/*/SKILL.md`
- `agents/*.md`

## By task type

### "Fix this bug"

Add to reads: recent `git log -p` for the file in question; any failing test output if the user quoted one; any linked issue tracker mention or relevant `_ops/learnings.md` delta when it materially changes what "fixed" means.

### "Add this feature"

Add to reads: the closest sibling feature (pick by directory adjacency); any design doc matching the feature keywords in `docs/`, `knowledge/research/`, or the repo's declared research layer.

If `_ops/PROJECT-PLAN.md` exists, check whether the feature supports or contradicts the current `Goal`, `Approach & Why`, active `Stage`, and optional `Anti-goals`.

### "Research / investigation"

Add to reads: the repo's research layer (for repos like this one, `knowledge/research/`) and memory files that mention the topic keywords. Skip source code unless the question is about code behavior.

### "Refactor"

Add to reads: all current consumers of the target symbol (Grep). Refactors without a consumer map are a bypass risk.

If `_ops/PROJECT-PLAN.md` exists, use its optional `Anti-goals` section to guard against "clean refactor, wrong direction" outcomes.

### "Write documentation"

Add to reads: existing docs in the same section, style guide if any, audience profile in memory or team docs.

## What not to read

Skip unless the task explicitly demands it:

- Generated files (`dist/`, `build/`, `node_modules/`, `.venv/`, `target/`).
- Large lockfiles (`package-lock.json`, `yarn.lock`, `Cargo.lock`) — date and version are enough.
- Entire `docs/` when only one page is relevant.
- Full git history when `-20` gives you the tone.

Reading too much is itself a bypass — it dilutes the criteria by drowning the model in irrelevant constraints.
