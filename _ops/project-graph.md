# Project Graph

Central index папочного графа: `depends-on` / `related-when` / `veto-class`.

Owner: `1folder-contract`. Single source of truth о связях папок. Root
`AGENTS.md` держит только одну строку-ссылку сюда; сам граф здесь.

Контекст. `agentic-research` — полигон для skill / agent / instruction
авторства под `GPT-5.5` и `Claude Opus 4.7`. Нет production-сервисов, бюджета
и public commitments; veto-class в локальных папках пуст. Cross-project blast
(правки глобальной скилл-системы) — отдельный блок ниже.

## Папки (depends-on — read-before-edit)

- `knowledge/wisdom-*.md` depends-on `_ops/GOAL.md` — модельная рамка
  `GPT-5.5` / `Claude Opus 4.7` ограничивает baseline.
- `knowledge/agents/*.md` depends-on `_ops/GOAL.md` — function-first
  принципы агентных систем под ту же модельную рамку.
- `knowledge/guides/` depends-on живые `SKILL.md` в `~/.claude/skills/` и
  `~/.codex/skills/` — guide не должен расходиться с действующим контрактом
  скилла.
- `knowledge/practical-guides/` depends-on `knowledge/wisdom-*.md` —
  принцип не дублируется в guide, ссылка на wisdom.
- `knowledge/research/{business,design,dev,meta}/` depends-on применимый
  `knowledge/wisdom-*.md` — research feeds wisdom, не наоборот.
- `_ops/GOAL.md` depends-on internal goal-formation thinking `1strategy-docs`
  (он думает + пишет; thinking не делегируется в `1strategy`).
- `_ops/PROJECT-ROADMAP.md` depends-on `_ops/GOAL.md` — текущая рамка
  работает внутри контракта.
- `_ops/self-learning/lessons.md` depends-on живой
  `/Users/triton/.codex/skills/1self-learning/SKILL.md` — формат, лимит и
  граница с `1findings` / `1user-said` живут в скилле.
- `_ops/plans/**/task-*.md` depends-on `_ops/PROJECT-ROADMAP.md` +
  релевантные `AGENTS.md` (root + subtree).
- `experiments/claude-bridge/` depends-on `~/.codex/skills/claude-mcp/`
  (skill it serves) + локальный `experiments/claude-bridge/AGENTS.md`.
- `experiments/gemini-mcp/` depends-on `~/.codex/skills/gemini-mcp/` +
  локальный `experiments/gemini-mcp/AGENTS.md`.
- `experiments/strategy-gallery/` depends-on локальный
  `experiments/strategy-gallery/AGENTS.md`.
- `experiments/md-embedding-server/` depends-on
  `~/.claude/skills/1md-navigator/SKILL.md` (server is the navigator's
  embedding backend). Также owns `.md-tools.toml` per-project filter
  config schema (sections `[index]` и `[graph]`, append-семантика для
  CLI поверх baseline, broken TOML → fatal). Mention в обоих
  `1md-navigator` и `1md-graph` (Claude + Codex) ссылается сюда; правки
  schema → `experiments/md-embedding-server/src/navigator/config.py`,
  затем синхронизация skill mentions.
  **Scope note.** Папка — runtime tooling для skills `1md-navigator` /
  `1md-graph`; работа по CLI shape, schema, UX легитимна как вклад в
  skill contract, не входит в polygon scope `_ops/GOAL.md` (тот про
  knowledge / skill design, не про runtime). Owner CLI / schema /
  envelope правил — backend (`docs/cli-conventions.md`,
  `docs/architecture-lock.md`, `src/navigator/schemas.py`); skills
  цитируют как view, не дублируют.
- `experiments/flowpage-v4-elk/` depends-on локальный
  `experiments/flowpage-v4-elk/AGENTS.md`.
- `experiments/all-my-messages/*.md` depends-on
  `/Users/triton/.codex/hooks/user_prompt_all_messages.py` — global per-project
  human-thread prompt analytics logs, не `1user-said` и не source of truth для
  решений; subagent/service prompts фильтруются hook-ом.
- Markdown graph frontmatter (`description`, `read-before-edit`,
  `edit-after-edit`) используется скриптом
  `/Users/triton/.codex/hooks/md_graph_pre_edit_reminder.py` — глобальный
  Codex `PreToolUse` reminder перед Markdown-правками; лёгкий, не блокирует,
  без широкого semantic search.

## Темы (related-when — retrieval hint)

- «правка skill / agent / prompt» → `knowledge/agents/` (runtime-layer,
  tool-design, memory, multi-agent, evaluation),
  `knowledge/wisdom-skills-plugins.md`,
  `knowledge/wisdom-claude-opus-4.7.md`, `knowledge/wisdom-gpt-5.5.md`,
  `knowledge/practical-guides/how-to-write-skills/`, `1skill-architect` skill,
  `1instruction-layer` skill, `1folder-contract` skill.
- «правка hook / runtime / settings.json» →
  `knowledge/practical-guides/hooks-runtime-guardrails.md`,
  `1start-here` (runtime delegate), `1folder-contract` skill.
- «изменение GOAL / scope / Definition of done» → `1strategy-docs` skill;
  Goal-цитаты в `AGENTS.md` и `CLAUDE.md` проверяются через `1folder-contract`;
  Codex синхронизирует только Codex-editable surfaces и отдаёт Claude-side handoff.
- «новый knowledge / wisdom / guide» → `knowledge/wisdom-systems-thinking.md`.
- «правка `experiments/**` subtree» → локальный `AGENTS.md` сабтри +
  релевантный skill контракт (`claude-mcp`, `gemini-mcp`).
- «routing / placement / naming инструкций» → `1instruction-layer` skill,
  `1folder-contract` skill.
- «закрытие работы / verify done» → `1work-review` skill.
- «git push / backup» → GitHub здесь — backup локального `main`,
  не collaboration flow.
- «design subagents / fresh eyes» → `1fresh-eyes` skill.
- «интервью / длинные вопросники» → `1interview-tool` skill, `_ops/AGENTS.md`
  раздел про `interviews/`.
- «важная цитата пользователя» → `1user-said` capture в
  `_ops/user-said/YYYY-MM-DD.md`.
- «самообучение / модель промахнулась / skill или tool сработал не так» →
  `1self-learning` и `_ops/self-learning/lessons.md`.

## Veto-class

В локальных папках `agentic-research` veto-class пуст: проект-полигон не
управляет production, бюджетом, public commitments или security-доменами.

**Cross-project blast** (требует явного `AskUserQuestion` перед commit):

- `~/.claude/skills/**` — правка задевает все Claude-проекты.
  **Note (post-P7 refactor 2026-05-21)**: skills `1md-navigator` и `1md-graph`
  теперь pure `SKILL.md` (no `scripts/` folder).
  **Note (post-MCP refactor 2026-05-22)**: MCP server удалён; skills
  используют Python CLI `md`. Backend живёт в
  `experiments/md-embedding-server/src/navigator/`, CLI — единственная точка
  вызова.
- `~/.codex/skills/**` — то же, post-refactor. Skills `1md-navigator` и
  `1md-graph` — pure `SKILL.md`.
- `~/.claude/CLAUDE.md` — user's private global instruction file.
- `~/.claude/settings.json` — глобальные hooks / permissions / MCP.

Эти поверхности живут вне репо, но видны отсюда как зависимости при работе
с `experiments/**`, где repo-local backend обслуживает глобальные handles.
