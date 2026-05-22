# Equivalence Doc Review

Context: `task-003` independent `1fresh-eyes` subagent review of
`experiments/md-embedding-server/docs/skills-semantic-equivalence.md`.

Verdict: `FAIL` before repair.

Blocking findings:

- `F1`: `1smart-simple` section was too generic; it missed concrete live values
  `limit: 3`, `threshold: 0.85`, `top: 20`.
- `F2`: `md_index` confirm flow contradicted the safety rule: canonical CLI
  signature and equivalence doc allowed bare `--confirm` without
  `--transaction-id`.
- `F3`: legacy helper `md_navigator.py cluster` was underspecified; automatic
  "nearest subcommand" rewrite would be unsafe.
- `F4`: `1md-graph` section preserved flags but not the output-reading
  contract: `preview/full/strict`, action labels, no binary safe/unsafe
  summary, transaction requirement for `md_init` / `md_strip`.

Resolution route:

- Fixed canonical signatures so `md_index` and `md_profile_sections` include
  `--transaction-id`.
- Tightened the equivalence doc shared rules and explicit skill sections.
- No task-201/202/203 gap added: missing transaction flags were corrected in
  task-001 canonical signatures and are already owned by task-204.

Second review after repair: `FAIL` only on live pre-migration Codex skill text.

- Passed: `1smart-simple` concrete values are preserved in the doc.
- Passed: legacy helper `md_navigator.py cluster` is explicitly kept as debug
  fallback, not auto-mapped to `md audit`.
- Passed: `1md-graph` output-reading contract is preserved.
- Still open: live `~/.codex/skills/1smart-simple/SKILL.md` and
  `~/.codex/skills/1md-navigator/SKILL.md` still contain pre-CLI
  dry-run/confirm prose. Do not patch them early against a CLI that does not
  exist yet; route to task-302/task-305 and enforce after task-204 lands.
