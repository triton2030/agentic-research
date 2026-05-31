---
description: "Условные правила выбора локальных CLI-проверок и evidence без отката чужих изменений."
read-before-edit:
  - "[[AGENTS.md]]"
  - "[[_ops/AGENTS.md]]"
  - "[[_ops/GOAL.md]]"
  - "[[_ops/project-graph.md]]"
edit-after-edit:
  - "[[AGENTS.md]]"
  - "[[_ops/AGENTS.md]]"
  - "[[_ops/project-graph.md]]"
---

# Local Tools Rules

Trigger: выбираешь проверку, собираешь CLI-evidence, ищешь stale refs, links,
deps, dead code, docs drift, package/security signals или готовишь closeout.

Owner: `1cli-tools` держит быстрые CLI-подтверждения; `1md-graph` держит
Markdown graph/preflight; `1work-review` держит финальную сверку после правок.

Check: evidence repo-local, scope явный, чужие изменения не откатываются,
вердикт не подменён метрикой.

## Defaults

- Сначала `rg`, `fd`, `git status`, `git diff`, `git log`; `find` только при
  необходимости.
- Dirty worktree не блокер: работай с текущим содержимым и не трогай чужие
  изменения вне scope.
- Repo-local запуск предпочтительнее global: `pnpm exec`, `npm exec --`,
  `npx --no-install`.
- GitHub здесь — backup локального `main`, не branch/PR collaboration flow.

## Tool Families

- Markdown graph/frontmatter/links/cycles -> `md preflight`, `md edit-context`,
  `md check`, `md cycles`, `md health`.
- Cleanup/move/delete/dead-code/docs-link/import/package/security evidence ->
  `1cli-tools`.
- JS/TS/Markdown/package evidence доступны по ситуации: `knip`, `lychee`,
  `markdownlint-cli2`, `tsc`, `biome`, `eslint`, `stylelint`, `depcruise`,
  `ast-grep`/`sg`, `publint`, `attw`, `syncpack`, `gitleaks`, `osv-scanner`,
  `trivy`, `semgrep`, `actionlint`.
