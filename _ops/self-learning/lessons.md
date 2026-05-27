# Self-Learning Lessons

> [!summary] Owner: [[_ops/self-learning/README|Self-Learning]] · Skill: `1self-learning` · Лимит 4000 (`wc -m`). Проектное → `1findings`; цитаты → `1user-said`.

## GPT-5.5

### Scope и workflow

- Не навязывай «режимы» outcome'у: scope проверяй через потребителей.
- Для личного agent-tool — минимальный runtime primitive + умный skill; CLI comfort откладывай до доказанного выигрыша.
- Перед design/role вариантами — 1-2 сценария; мягкая роль промахнётся, если нужен жёсткий оппонент.
- Batch: freeze target set + dry-run; scope называй заранее.

### Evidence before blame

- До обвинения tool/code проверь вход: stale map, fixture, temp side effect, cwd, путь, валидность данных.
- Внешние skill-файлы — read + validate; YAML с `:` → folded/quoted.
- Read-only smoke в `/tmp`, иначе доверие к «read-only» сломано.

### Tools и handoff

- Hooks: lifecycle moment явно (`UserPromptSubmit` ≠ `PreToolUse`); analytics — фильтруй service prompts.
- Code-architecture review: сначала `1repo-map`, потом `1cli-tools`; IA-риски docs/ownership отделяй через `1ia-audit`.
- На «почему не вызвал X-скил» — не объясняй задним числом, классифицируй и запиши владельцу.
- Named subagent: сверь `agent_type`; роль не принимается → не имитируй, фиксируй mismatch.
- `fork_context` ≠ named `agent_type`: либо full-history наследование, либо named без fork + self-contained brief.
- Bridge relay truncated → восстанови из logs до rerun.
- Shell one-liner с `$1`/backrefs — только single quotes или `apply_patch`; double quotes тихо съедают группы.
- Append-only capture в один файл не запускай параллельно; сериализуй вызовы и проверь группировку строк.

## Claude Opus 4.7

### Review и background jobs

- Background jobs: жди notification, не poll-loop, не kill по low CPU; проверь output/sockets/rate-limit.
- После compaction hook видит долг прошлых ходов — закрывай по доступным следам.

### Routing и соседние owner-скилы

- Не аналогируй runtime roots; файл не там, где ждал → расширь поиск (`~/.codex`, `~/.claude`).
- Внутри скила спроси, какой соседний owner владеет частью сигнала: `1md-navigator`, `1md-graph`, `1ia-audit`.

### Debug

- Расширяешь downstream API → сначала трассируй pipeline до места, где данные ещё correct; чини mid-pipeline.
- Tool error → refresh saved state + проверь path из traceback, потом «tool broken».
- Diagnostic thresholds — ≥2 стилистически разных корпуса; cutoff из familiar corpus не переносится.

### Solution scope: minimal first

- Critic finding ≠ mandate to expand. Patch решает risk, не строит фичу. Минимум → расширяй под давлением.
- Не закладывай оси гибкости (форматы, frozen dataclasses, source-tracking) под нишевые гипотезы; обычно один список / формат / ось.
- TOML/JSON/dataclass-валидация — только при втором потребителе схемы; до этого plain text + ~10 LOC parser.
- Перед commit представь самую короткую форму того же поведения. Короче на >5× → переписать.

### Markdown graph

- После правки `read-before-edit` / `edit-after-edit` frontmatter → ОБЯЗАТЕЛЬНО `md cycles --paths ROOT --json` до closure.
- Перед claim «owner X отсутствует» — `md search CORPUS --query "X" --scope descriptions --json`; без CLI-probe = vacuum-default.
