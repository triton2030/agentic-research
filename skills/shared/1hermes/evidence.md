# Evidence — 1hermes Ox Alpha override

## Proven live before the change

- OpenRouter API returned exact `stealth/ox-alpha`, provider `Stealth`, cost `0`.
- Hermes Agent 0.20.0 resolved `stealth/ox-alpha` through `openrouter`.
- A reasoning `max` probe used `read_file` and returned the exact file marker.
- An uncommitted write probe changed a file inside the Hermes worktree, after
  which Hermes removed that worktree and its branch.
- Hermes source preserves a worktree only when it finds unpushed commits.
- A committed probe in a repo without `refs/remotes/*` was also removed; Hermes
  source explicitly classifies that repository shape as having no unpushed work.

## Was still unknown before post-change verification

- Claude-side behavioral routing into the Ox Alpha branch.

## Proven live after the change

- Session `20260822_071345_537b44`: exact Ox Alpha/OpenRouter/max read used one
  file tool and returned the exact marker at estimated cost `0.0`.
- Session `20260822_072130_8b4284`: the post-change wrapper automatically passed
  the live free-only gate, then returned the exact read marker at estimated cost
  `0.0` without warnings.
- Session `20260822_071827_407285`: Ox changed only `result.txt`, committed
  `a77bc05990ab6bd71fb0047985ef417ac11e2071`, and Hermes preserved the worktree.
  Independent inspection proved one commit ahead, a clean tree, exact bytes and
  an unchanged base file. The disposable proof worktree was then removed.

## Provider correction

- The live Hermes catalog lists `stealth/ox-alpha` under both `nous` and
  `openrouter`; the first implementation chose OpenRouter from the supplied URL.
- Official Nous `/v1/models` returned exact Ox pricing with prompt and completion
  both `0.0000000000`; the account itself is a paid Nous tier.
- Session `20260822_080754_80bcf3` resolved exact `stealth/ox-alpha` through
  `nous`, reasoning `low`, and returned the sentinel at estimated cost `0.0`.
- Session `20260822_083730_a4bf38` proved Nous/max file reading with one file
  tool call and exact marker. Session `20260822_083759_59847c` proved Nous/max
  writing in a preserved Hermes worktree: only `result.txt` changed, commit
  `6aa4335e679cafe47874ebf68dd4d53cb1cc49c4`, base remained unchanged, estimated
  cost `0.0`.
- A resume probe exposed that Hermes 0.20.0 otherwise used the current configured
  `z-ai/glm-5.2` while the session export still reported its original Ox model;
  `session_model_usage` recorded the drift and estimated cost `0.002301464`.
- The corrected wrapper pins the saved model/provider/reasoning on resume and
  verifies a new main-call delta in `session_model_usage`. Clean session
  `20260822_084549_a41a3f` passed fresh and resume sentinels; its only usage row
  is two `stealth/ox-alpha` calls through `nous`, estimated cost `0.0`.
- Contract tests pass 16/16 in the Codex projection and 20/20 in the Claude
  projection.

## Intermediate bounded harness and modular refactor verification

- The live packages keep the runtime contract outside the repository because
  no tracked code owner exists. Their shared implementation is split into five
  byte-identical modules: request contract (205 lines), free-route policy (74),
  runtime evidence (285), process/worktree execution (204), and health state
  (94). The Codex/Claude orchestrators are 409/419 lines.
- Session `20260822_121258_b5d7cb` proved the post-refactor Codex path: Ox read
  `_ops/GOAL.md` through `read_file`, returned exact `OX_FRESH_OK`, and added two
  calls on exact `stealth/ox-alpha | nous |
  https://inference-api.nousresearch.com/v1 | billing_mode=''`. No other route
  appeared; estimated cost was `0.0`, while `actual_cost_usd` remained unknown.
- Session `20260822_120644_c1bdc3` proved pinned resume after a real tool turn.
  Its accepted resume added one call on the same exact route and returned exact
  `OX_RESUME_OK`; no unexpected model, provider, endpoint, or billing mode
  appeared.
- Session `20260822_120948_773f54` proved file-only editing. Ox changed only
  `seed.txt` in wrapper-created worktree
  `1hermes-ox-write.XXXXXX.Q3DX8MyT9H-20260822T070947Z-99689-37c10a`; the host
  committed `ced952042c2e09753385ba9489275a4b759b48ff`. Independent Git
  inspection proved a clean tree, exactly one commit over
  `3651389d3de11307588b2acce615fe79e10f6a21`, committed bytes `after\n`, and
  unchanged base bytes `before\n`. All four exact-route calls had estimated
  cost `0.0`; `actual_cost_usd` remained unknown.
- Session `20260822_121325_b0b5d9` closed the earlier Claude-side gap: the
  Claude projection read the same file and returned exact `CLAUDE_OX_OK`; its
  two calls used the same exact Ox/Nous route at estimated cost `0.0`, with
  `actual_cost_usd` unknown.
- Upstream Hermes `tests/tools/test_file_write_safety.py` passed 57/57 through
  the project's declared `uv run --extra dev` environment. Local contract
  suites pass 22/22 for Codex and 27/27 for Claude; Ruff reports no errors.

## Minimal agent-shaped runtime verification

- Owner correction on 2026-08-22 moved research strategy, role choice, reading
  order, depth, and solution method out of Python and into the skill, where the
  agent applies them flexibly. Python retains price/route gates, session
  evidence, safe-root/worktree, timeout/resume lock, and machine receipts.
- Native `hermes status`, `hermes portal info`, and `hermes tools list` replace
  the custom health/state layer. The Claude-only raw proxy was removed because
  this skill has one product path: a Hermes agent with session-backed evidence.
- Production Python across both live packages decreased from 3,749 to 2,078
  lines. Four hard-gate modules are byte-identical; the two thin orchestrators
  are 334/344 lines. Local suites pass 19/19 plus 5 subtests for Codex and
  23/23 plus 5 subtests for Claude; Ruff and Python compilation pass.
- Session `20260822_123232_d83243` proved the simplified read path: exact
  Ox/Nous/max, one `read_file`, exact `OX_MINIMAL_OK`, two exact-route calls,
  no unexpected route, estimated cost `0.0`, actual cost unknown. Its accepted
  resume returned exact `OX_MINIMAL_RESUME_OK` and added one call on the same
  route with no unexpected model, provider, endpoint, or billing mode.
- Session `20260822_123304_b90475` proved the simplified write path. Ox used
  only file tools and changed `seed.txt`; host commit
  `92c44486bd8f9916e032c4a3e2af5c9a533c1e88` is one clean unpushed commit over
  `3651389d3de11307588b2acce615fe79e10f6a21`. Direct Git reads returned
  `after-minimal\n` in the worktree and unchanged `before\n` in the base. All
  four exact-route calls had estimated cost `0.0`; actual cost remained unknown.
- Session `20260822_124706_d96eea` verified the final boundary after removing
  code-level methodology restrictions: one `read_file`, exact
  `OX_SKILL_BOUNDARY_OK`, two exact Ox/Nous endpoint calls, no unexpected route,
  estimated cost `0.0`, and actual cost unknown.
