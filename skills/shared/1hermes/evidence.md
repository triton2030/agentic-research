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
