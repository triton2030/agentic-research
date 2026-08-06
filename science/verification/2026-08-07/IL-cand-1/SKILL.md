---
name: 1instruction-layer
description: >
  Use when writing or auditing durable `AGENTS.md`, `CLAUDE.md`, path rules or
  repo-local instruction files; a plausible rule can otherwise load from the
  wrong owner or be obeyed in form while leaving the same agent decision
  unchanged. Recover the effective chain and design the smallest
  trajectory-changing delta; prose is not enforcement.
---

# Слой Инструкций

Рабочее состояние: `admission → chain map → owner → steering cell → control →
exact delta → proof`. Каждый gate порождает свой наблюдаемый результат до
следующего; читай его файл в момент прохождения, не по памяти. Пропустить gate
можно только когда его результат уже прямо подтверждён текущим evidence.

Файлы в `references/`, по одному на момент: `product-measure.md` (до всего: три
product job, mode, мера), `controller.md` (правила хода, re-anchor, decision
traces), `steering-cell.md` (до wording), `gate0-admission.md`, `gate1-chain.md`,
`gate2-owner.md`, `gate3-cell.md`, `gate4-control.md`, `gate5-wording.md`, `gate6-bypass.md`,
`gate6-proof.md`, `triggered-rules.md` (cold `_ops/rules/**`), `output-stop.md` (перед
вердиктом).

Условная глубина — только по условию, названному в файле gate: `discovery-*.md`
(Claude Code loading, description limits), `placement-*.md` (topology, duplicate,
hot path), `meaning-*.md` (load-bearing meaning, критерии, design mode),
`language-*.md` (wording), `divergences-*.md` (model tell), `cli-recipes.md` (evidence
вне уже прочитанных instruction files), `demo-contrastive.md` (лозунг против
развилки).

## Boundaries

- split/merge/move/new instruction container → `1ia-audit`;
- `depends-on`, holders, anchors, cycles, broken links → `1md-graph`;
- skill/agent/hook selection, trigger/collision → `1skill-architect`;
- project scope/done/stop → `1goal`; task contract → `1planning`;
- permissions/hooks/settings/enforcement → live runtime owner.
