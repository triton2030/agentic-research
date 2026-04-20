# Discovery Map

Extended patterns for `criteria-generator`. Use when the default probe list in `SKILL.md` is insufficient.

## Default probes

- `CWD/CLAUDE.md`, `~/.claude/CLAUDE.md`
- `CWD/AGENTS.md`, `CWD/GEMINI.md`
- `CWD/README*`
- `CWD/docs/`
- `CWD/ops/`
- `CWD/ops/NORTH-STAR.md`
- `CWD/knowledge/`, `CWD/projects/` (or legacy `CWD/_research/`, `CWD/_random-guides/`)
- `~/.claude/projects/<project-slug>/memory/MEMORY.md`
- `git log --oneline -20`, `git status` if `.git` exists

If `CWD/ops/` is missing, create it before deeper discovery.

If `CWD/ops/NORTH-STAR.md` is missing, create a minimal note there before continuing. Keep it short and strategic:

- why the project exists;
- who it helps;
- what must become easier;
- what wrong success should be avoided.

If the skill needs any additional operational files for its own execution, place them in `ops/`, not in root or `_research/`.

## By project type

### Node / TypeScript repo

- `package.json` — scripts and dependencies shape the verification protocol.
- `tsconfig.json` — strictness affects what "passes" means.
- `.eslintrc*`, `.prettierrc*` — style constraints can become Must-not items.
- `tests/`, `__tests__/`, `*.test.*` — existing test patterns to match.

### Python repo

- `pyproject.toml` / `setup.py` / `requirements*.txt`
- `pytest.ini`, `tox.ini`, `conftest.py`
- `mypy.ini`, `.ruff.toml`

### Go repo

- `go.mod`, `go.sum`
- `Makefile` if present
- `*_test.go`

### Rust repo

- `Cargo.toml`
- `tests/`, `benches/`
- `clippy.toml`

### Docs-only / knowledge repo

- Top-level underscore folders
- `mkdocs.yml`, `mkdocs.yaml`, `docusaurus.config.*`, `astro.config.*`
- `CONTRIBUTING.md`, `STYLE.md`

### Claude Code plugin / skill project

- `.claude/settings.json`
- `plugins/*/plugin.json`
- `skills/*/SKILL.md`
- `agents/*.md`

## By task type

### "Fix this bug"

- Read the smallest failing reproduction first.
- Add recent git history for the touched file only if current direction matters.
- Prefer nearby tests and error output over broad repository reading.

### "Add this feature"

- Read the closest sibling feature.
- Read the most relevant design note or requirements doc if one exists.
- Pull in config only if it changes what "done" means.

### "Research / investigation"

- Read internal notes before external sources.
- Read `_research/` and memory files that mention the topic keywords.
- Skip source code unless the question is about code behavior.

### "Refactor"

- Read all current consumers of the target symbol.
- Map behavior before renaming or moving anything.
- Treat missing consumer discovery as a bypass risk.

### "Write documentation"

- Read the closest existing docs in the same section.
- Read the writing style guide if one exists.
- Read audience notes from root instructions or memory files.

## What not to read

Skip unless the task explicitly demands it:

- Generated files such as `dist/`, `build/`, `node_modules/`, `.venv/`, `target/`.
- Large lockfiles where date and version are enough.
- Entire `docs/` when only one page is relevant.
- Full git history when `-20` already gives you the tone.

Reading too much is itself a bypass — it dilutes the criteria by drowning the model in irrelevant constraints.
