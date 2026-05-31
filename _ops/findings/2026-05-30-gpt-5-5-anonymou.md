# Findings — 2026-05-30 — gpt-5-5 — sess:anonymou

- 17:08 — hook-audit: live root_cause_hook.py still uses 300s interval, not every 3 user messages | /Users/triton/.codex/hooks/root_cause_hook.py:21,436-440 | memory/context is stale until owner decides schedule
- 17:08 — hook-audit: Codex Supermemory UserPromptSubmit recall.js also captures transcript after autoSaveEveryTurns=3 | /Users/triton/.codex/supermemory/recall.js:2597-2600,2444-2523 | old claim 'UserPromptSubmit only recall' is no longer live truth
- 17:08 — hook-audit: Claude Supermemory credentials are 0644 and auth.js saves without mode | /Users/triton/.supermemory-claude/credentials.json perms + src/lib/auth.js:34-40 | should become 0600 / private dir if kept
- 17:15 — hook-audit resolved: root_cause_hook 300s timer confirmed intentional by user | finding 17:08 root-cause | no code change needed
- 17:15 — hook-audit scope-corrected: Claude Supermemory code/cache fix was reverted after user narrowed scope to Codex-only; only stricter existing credential file perms remain | ~/.claude/plugins/marketplaces/supermemory-plugins clean, node_modules removed | do not continue Claude-side work in this task
- 17:20 — hook-audit fixed: Codex Supermemory tracker/cache storage now uses 0700 dirs + 0600 files; existing tracker files chmodded | ~/.codex/supermemory/recall.js, ~/.codex/supermemory/flush.js, ~/.codex-supermemory/trackers | verified node --check and stat perms
- 17:28 — self-learning: пользователь поправил intent — Stop hook видим, но не решает async chat insertion; не подменять realtime delivery lifecycle-event fallback-ом | root_cause_hook chat visibility | следующий ход: сначала доказать thread/app-server/turn-steer surface, иначе честно сказать что hook-only не может
- 17:58 — subagents: visible meta-agent chat delivery should be separate delivery owner, not hook stdout only | root_cause_hook visibility | next: proof spike app-server thread/steer/inject_items before global chat mutation
- 17:58 — self-learning: cursor advanced on job start would create blind window after failed worker | root_cause_hook incremental slicing | next: move cursor only on successful delivered/completed analysis
