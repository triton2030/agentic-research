# Folder Contract Criteria

## Зона ответственности

Когда работа меняет папочный граф, `_ops/project-graph.md`, Owner Decision Map,
system coherence, criteria delivery chain, hooks/runtime guardrails,
structural controls, paired `AGENTS.md` / `CLAUDE.md` shim или Goal-quote sync.

## Цель

Инструкционный стек приближает агента к контракту проекта из `_ops/GOAL.md`:
папки, criteria, skills, hooks, runtime guards и review образуют связную
систему, а не набор хороших фраз.

## Критерии

Rule: Folder-contract работа проверяет, ведут ли root/папочные инструкции, skill routing, criteria, hooks и review агента к контракту проекта из `_ops/GOAL.md`.
Why: User signal: новый `1folder-contract` отвечает за глубокий смысловой аудит того, как instruction stack приближает агента к конечной цели проекта.

Rule: Папочные инструкции и `_ops/project-graph.md` разделяют `depends-on`, `related-when` и `veto-class`; central index живёт в `_ops/project-graph.md`, а root-инструкции держат только короткий указатель.
Why: User signal: пользователь хочет, чтобы агент понимал связанность папок и не решал локально запросы, которые затрагивают бюджет, инфраструктуру, публичные обещания или другие зоны с правом вето.

Rule: `1folder-contract` и `1ia-audit` работают парой: IA-аудит владеет container fit, owner truth, naming, retrieval path и view-vs-truth; folder-contract владеет системным контрактом, folder graph, criteria delivery и goal alignment.
Why: User signal: риск collision высокий на ownership leak; граница должна быть явной: `1ia-audit` — форма контейнера, `1folder-contract` — соответствие системы цели.

Rule: Structural controls — folder shape, hooks, validators, config, permissions, MCP/apps, scripts и runtime boundaries — являются режимом `1folder-contract`.
Why: User signal: после split structural-controls и system-coherence больше не должны конкурировать с language-quality задачами `1instruction-layer`.

Rule: Session-state JSON `~/.claude/state/session-{session_id}.json` — canonical shared structure между hooks и skills для cross-hook/cross-skill памяти (anchor_reads, file_changes, skill_invocations, markers_seen, applied_criteria); folder-contract ссылается на schema в `~/.claude/skills/1start-here/references/session-state-schema.md`, не дублирует её содержимое.
Why: User decision (план «Hooks ↔ Skills enforcement architecture»): stateful enforcement требует одного источника правды о происходящем в сессии; structural contract координирует routing к этому единому CLI.

Rule: Hook-loaded Goal-quote sync — часть folder contract: при изменении `_ops/GOAL.md#Что делаем` проверить Codex-editable root pointer/quote и назвать Claude-side sync как read-only handoff.
Why: User signal: hook-loaded Goal-quote sync относится к контракту между goal, hooks и root shims, а не к формулировке отдельной инструкции.

Rule: Paired `AGENTS.md` ↔ `CLAUDE.md` shim invariant держит `1folder-contract`: поверхности должны совпадать по routing-смыслу, но Codex не редактирует Claude files.
Why: User signal: paired shim является системным invariant; Codex boundary остаётся жёсткой read-only границей.
