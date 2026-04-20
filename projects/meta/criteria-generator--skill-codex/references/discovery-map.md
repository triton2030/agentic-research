# Discovery Map

Extended patterns for Step 2 of `criteria-generator`. Use when the default probe list in SKILL.md is insufficient.

## Default probes (repeated from SKILL.md)

- `CWD/CLAUDE.md`, `~/.claude/CLAUDE.md`
- `CWD/AGENTS.md`, `CWD/GEMINI.md`
- `CWD/README*`
- `CWD/docs/`
- `CWD/ops/`
- `CWD/ops/NORTH-STAR.md`
- `CWD/knowledge/`, `CWD/projects/` (or legacy `CWD/_research/`, `CWD/_random-guides/`)
- `~/.claude/projects/<project-slug>/memory/MEMORY.md`
- `git log --oneline -20`, `git status` (if `.git` exists)

If `CWD/ops/` is missing, create it before deeper discovery.

If `CWD/ops/NORTH-STAR.md` is missing, create a minimal note there before continuing. Keep it short and strategic:

- why the project exists;
- who it helps;
- what must become easier;
- what wrong success should be avoided.

If the skill needs any additional operational files for its own execution, place them in `ops/`, not in root or `_research/`.

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

- Top-level `_`-prefixed folders (often convention folders).
- `MKDocs.yml`, `mkdocs.yaml`, `docusaurus.config.*`, `astro.config.*`.
- Any `CONTRIBUTING.md`, `STYLE.md`.

### Claude Code plugin / skill project

- `.claude/settings.json`
- `plugins/*/plugin.json`
- `skills/*/SKILL.md`
- `agents/*.md`

## By task type

### "Fix this bug"

Add to reads: recent `git log -p` for the file in question; any failing test output if the user quoted one; issue tracker mention if present in a linked `ISSUES.md` or `ops/`.

### "Add this feature"

Add to reads: the closest sibling feature (pick by directory adjacency); any design doc matching the feature keywords in `docs/` or `_research/`.

### "Research / investigation"

Add to reads: `_research/` and memory files that mention the topic keywords. Skip source code unless the question is about code behavior.

### "Refactor"

Add to reads: all current consumers of the target symbol (Grep). Refactors without a consumer map are a bypass risk.

### "Write documentation"

Add to reads: existing docs in the same section, style guide if any, audience profile in memory or team docs.

## What not to read

Skip unless the task explicitly demands it:

- Generated files (`dist/`, `build/`, `node_modules/`, `.venv/`, `target/`).
- Large lockfiles (`package-lock.json`, `yarn.lock`, `Cargo.lock`) — date and version are enough.
- Entire `docs/` when only one page is relevant.
- Full git history when `-20` gives you the tone.

Reading too much is itself a bypass — it dilutes the criteria by drowning the model in irrelevant constraints.
