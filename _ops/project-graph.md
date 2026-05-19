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
- `_ops/criteria/*.md` depends-on `_ops/GOAL.md` — criteria применимы
  только в рамках scope.
- `_ops/plans/**/task-*.md` depends-on `_ops/PROJECT-ROADMAP.md` +
  applicable `_ops/criteria/*.md`.
- `experiments/claude-bridge/` depends-on `~/.codex/skills/claude-mcp/`
  (skill it serves) + `_ops/criteria/external-agent-control.md`.
- `experiments/gemini-mcp/` depends-on `~/.codex/skills/gemini-mcp/` +
  `_ops/criteria/external-agent-control.md`.
- `experiments/strategy-gallery/` depends-on
  `_ops/criteria/strategy-gallery-workflow.md` + локальный
  `experiments/strategy-gallery/AGENTS.md`.
- `experiments/md-embedding-server/` depends-on
  `~/.claude/skills/1md-navigator/SKILL.md` (server is the navigator's
  embedding backend).
- `experiments/flowpage-v4-elk/` depends-on локальный
  `experiments/flowpage-v4-elk/AGENTS.md`.

## Темы (related-when — retrieval hint)

- «правка skill / agent / prompt» → `knowledge/wisdom-agents.md`,
  `knowledge/wisdom-skills-plugins.md`,
  `knowledge/wisdom-claude-opus-4.7.md`, `knowledge/wisdom-gpt-5.5.md`,
  `knowledge/practical-guides/how-to-write-skills/`,
  `_ops/criteria/skill-authoring.md`, `_ops/criteria/instruction-layer.md`,
  `_ops/criteria/folder-contract.md`.
- «правка hook / runtime / settings.json» →
  `knowledge/practical-guides/hooks-runtime-guardrails.md`,
  `_ops/criteria/repo-structure-and-runtime-guards.md`,
  `_ops/criteria/folder-contract.md`.
- «изменение GOAL / scope / Definition of done» → Goal-цитаты в `AGENTS.md`
  и `CLAUDE.md` проверяются через `1folder-contract`; Codex синхронизирует
  только Codex-editable surfaces и отдаёт Claude-side handoff.
- «новый knowledge / wisdom / guide» → `knowledge/wisdom-systems-thinking.md`,
  `_ops/criteria/knowledge-maintenance.md`.
- «правка `experiments/**` subtree» →
  `_ops/criteria/external-agent-control.md` +
  applicable strategy-gallery / claude-bridge / gemini-mcp criteria.
- «criteria-routing / placement / naming» →
  `_ops/criteria/criteria-routing-and-naming.md`,
  `_ops/criteria/instruction-layer.md`, `_ops/criteria/folder-contract.md`.
- «закрытие работы / verify done» →
  `_ops/criteria/work-review-and-evidence.md`, `1work-review` skill.
- «git push / backup» → `_ops/criteria/git-backup-workflow.md` (GitHub —
  backup локального `main`, не collaboration flow).
- «design subagents / fresh eyes» →
  `_ops/criteria/design-subagent-analysis.md`, `1fresh-eyes` skill.
- «интервью / длинные вопросники» →
  `_ops/criteria/interview-intake-workflow.md`,
  `_ops/criteria/ops-problems-layer.md`.

## Veto-class

В локальных папках `agentic-research` veto-class пуст: проект-полигон не
управляет production, бюджетом, public commitments или security-доменами.

**Cross-project blast** (требует явного `AskUserQuestion` перед commit):

- `~/.claude/skills/**` — правка задевает все Claude-проекты.
- `~/.codex/skills/**` — правка задевает все Codex-проекты.
- `~/.claude/CLAUDE.md` — user's private global instruction file.
- `~/.claude/settings.json` — глобальные hooks / permissions / MCP.

Эти поверхности живут вне репо, но видны отсюда как зависимости при работе
с `experiments/**` (где skills и MCP serverы реально живут параллельно
глобальным handle).
