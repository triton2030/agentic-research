# Opus Advisor Prompting

`opus_advisor` is the default for architecture, debugging, code review, planning
and ongoing project advice. The profile already owns model alias and effort; do
not add arbitrary CLI overrides.

Give Opus the task, intent, current state, exact sources, constraints, evidence
bar, expected output and stop condition in the first turn. Name exact sources
or a relevant Claude `Skill` when their use matters. Prefer a compact
self-contained brief over a chat transcript and ask for a general solution, not
a test-shaped patch.

Continue with `session_id` for iterative work with one retained specialist.
Start fresh when Codex needs an independent challenge, another branch/project,
or a different role. Verify material claims locally before acceptance.

Official volatile owner:

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-4-8
