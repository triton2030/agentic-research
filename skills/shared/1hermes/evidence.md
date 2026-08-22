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

## Still unknown before post-change verification

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
