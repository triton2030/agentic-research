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
- Expert-evidence amendment, 2026-08-13: a fresh subagent read the existing
  root-produced `172516-evidence-page-map.md` and wrote
  `180906-evidence-page-subagent-review.md` without opening page sources.
- The amended report produced a page model, five opened public UX sources,
  addressed `E-id + S-id` chains and six separate hypotheses. It made no
  grounded change recommendation where the map lacked action semantics.
- Matched comparator: the pre-amendment `172516` review recommended moving the
  action block and strengthening its primary control without action semantics;
  the amended review moved both claims out of accepted changes.
- Root re-opened all affected HTML anchors and all five public sources. Five
  `Оставить` chains were supported. The `E03` keep claim was rejected because
  source lines 14-15 and 31-33 show E05 shares E03's filled treatment, so the
  current state does not express one unambiguous primary control.
- Source support was checked against GOV.UK Button, Headings and Paragraphs,
  plus USWDS Button Group and Card guidance. Public sources supported only the
  general principles; page-specific effects remained labelled as inference.
