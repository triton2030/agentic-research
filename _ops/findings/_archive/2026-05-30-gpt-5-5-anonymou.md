# Findings — 2026-05-30 — gpt-5-5 — sess:anonymou

- 17:08 — hook-audit: Codex Supermemory UserPromptSubmit recall.js also captures transcript after autoSaveEveryTurns=3 | /Users/triton/.codex/supermemory/recall.js:2597-2600,2444-2523 | old claim 'UserPromptSubmit only recall' is no longer live truth
- 17:08 — hook-audit: Claude Supermemory credentials are 0644 and auth.js saves without mode | /Users/triton/.supermemory-claude/credentials.json perms + src/lib/auth.js:34-40 | should become 0600 / private dir if kept
- 17:15 — hook-audit scope-corrected: Claude Supermemory code/cache fix was reverted after user narrowed scope to Codex-only; only stricter existing credential file perms remain | ~/.claude/plugins/marketplaces/supermemory-plugins clean, node_modules removed | do not continue Claude-side work in this task
- 17:20 — hook-audit fixed: Codex Supermemory tracker/cache storage now uses 0700 dirs + 0600 files; existing tracker files chmodded | ~/.codex/supermemory/recall.js, ~/.codex/supermemory/flush.js, ~/.codex-supermemory/trackers | verified node --check and stat perms
