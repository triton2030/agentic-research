# Opus Advisor Prompting

`opus_advisor` is the exact-pinned `claude-opus-5` default for architecture,
debugging, code review, planning and ongoing project advice. The profile already
owns model and `xhigh` effort; do not add arbitrary CLI overrides.

Give Opus the task, intent, current state, exact sources, constraints, evidence
bar, expected output and stop condition in the first turn. Name exact sources
or a relevant Claude `Skill` when their use matters. Prefer a compact
self-contained brief over a chat transcript and ask for a general solution, not
a test-shaped patch.

Calibrate visible length and progress explicitly because Opus 5 narrates and
writes more than prior Opus models. Constrain narrow scope and stop. Do not add
generic double-check, verifier-subagent or automatic fan-out scaffolding: Opus 5
self-corrects and delegates readily. Delegate only genuinely independent
sizeable tracks, and use one subagent when one is enough.

Continue with `session_id` for iterative work with one retained specialist.
Start fresh when Codex needs an independent challenge, another branch/project,
or a different role. Verify material claims locally before acceptance.

Official volatile owner:

- <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>
