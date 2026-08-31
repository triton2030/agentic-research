# Validation evidence

Exact package: `/tmp/skill-creation-v10.FoE8TP/package`

Current manifest SHA-256:
`beb24fb9dbe6851bab68738ecb194356356a8eb5db8ddc6bf432ec8c873d1232`.

Installed baseline before this delegated correction:
`91b4fc8a77af41018eaee752c0d9679a6c61884d869c8294aa4928bc21707325`.

## Scope

Exact package changes:

- `SKILL.md` — continuation routes by saved refactor state instead of
  self-generated intermediate triggers.
- `references/refactor.md` — state precedence, one-shot consumption,
  `needs-input` and new-owner-evidence retry gate.
- `references/reference-files.md` — 20 units is a compression-first cognitive
  risk signal rather than an automatic split gate.

The approved two-wave validation limit and both reviewer files are unchanged.
No tracked owner, projection, live package or other skill was edited by this
delegated correction.

## Opus Advisor

- Requested: `opus_advisor`, `xhigh`.
- Resolved: `claude-opus-5`, no warnings.
- Session: `0e983111-575c-4365-99c0-be27ec8963e6`.
- Accepted architecture: router only names start/continue; `refactor.md` alone
  owns state precedence, consumption and retry eligibility.
- Rejected architecture: duplicate the state rule in `SKILL.md` and
  `refactor.md`; it would create two owners for the invariant that already
  drifted.

Local source check confirmed `reference-files.md` assigns routing conditions to
the body and local stage logic to one reference file. The implementation makes
the externally visible router rewrite but keeps all state transitions in
`refactor.md`.

## Local checks

- `quick_validate.py`: `Skill is valid!`.
- `rumdl check`: no issues in 11 files.
- `md check`: 11 targets, 0 issues.
- `git diff --check`: no whitespace errors.
- Overlay copies of all three changed exact files match the exact package.
- Exact package differs from the installed owner in only those three files.

Static transition probes all pass:

1. Fresh refactor with no state still reaches `goal-context.md`.
2. Saved state outranks the original refactor trigger.
3. A ready intent token becomes `ожидается смысловой черновик` before dispatch
   and cannot dispatch twice.
4. A material loss without new owner evidence stops at `нужен ответ владельца`.
5. Explicitly new material owner intent/evidence permits one retry.
6. Repeated same loss requires another new owner response.
7. More than 20 active units first triggers semantic compression, not automatic
   package splitting.

## Validation-wave boundary

No new validator subagents were launched. The two validation waves of this task
remain exhausted; Opus was the explicitly requested single external
architecture advisor, not a validation-wave participant.

## Handoff

Root must decide integration and installation. This delegated pass does not
authorize or perform either.
