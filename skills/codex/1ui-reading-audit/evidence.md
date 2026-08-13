# Evidence

## Support Envelope

- Target: Codex `gpt-5.6-sol`, reasoning `xhigh`.
- Harness: Codex desktop subagents with shared filesystem.
- Required tools: source-code reading, filesystem writes, one clean subagent.
- Default evidence: one desktop PC page from source code; no render.

## Acceptance

- Structure: `quick_validate.py` and `qv-skill` passed; Markdown lint passed
  after line-wrap repair.
- Realistic application test, 2026-08-13: one root agent wrote the map, then a
  separate clean subagent read only that map and wrote its own report. A
  one-agent audit is not acceptance evidence for this skill.
- Full-skill artifacts:
  `Workspace/Design/1ui-reading-audit/2026-08-13/171854-evidence-page-map.md`
  and `171854-evidence-page-subagent-review.md`.
- Root re-opened source anchors, accepted one size change, rejected the
  unsupported button move and preserved `не доказано` gaps.
- No-skill comparator skipped the map and second agent, introduced an
  unrequested mobile finding and presented stronger visual claims directly.
- Source fixture remained unchanged at SHA-256
  `2012c04b49a46c1b6c9f741cca3a1b62a18aa4daca1f18ff8c2ea9e44297840e`.
- Activation: a representative bare prompt without the skill name produced a
  second two-agent run and artifacts `172516-evidence-page-map.md` and
  `172516-evidence-page-subagent-review.md` in the same daily directory.
- Activation completion: the second map contained 11 addressed elements; root
  rejected the unsupported block move and accepted only the source-supported
  button hierarchy correction.
- Near-miss routing passed: `Проверь WCAG-доступность этой
  страницы по исходному коду` used the same HTML but correctly skipped this
  skill and created no `1ui-reading-audit` artifacts.
