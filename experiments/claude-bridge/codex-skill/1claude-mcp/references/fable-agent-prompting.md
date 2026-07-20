# Fable Advisor Prompting

Use `fable_advisor` only for the hardest long-horizon, ambiguous, high-stakes or
multi-system judgment. It is one blocking trusted-native call and may take
minutes.

## Brief

Give Fable the real outcome and why constraints matter, not only commands. Name:

- the decision or claim to attack;
- exact owner files and live evidence;
- native authority plus the investigate/do-not-modify behavior instruction;
- success criteria, uncertainty to expose and stop condition;
- a compact verdict-first output.

Ask for findings, evidence, alternatives and uncertainty, never private
reasoning. Strong but short instructions work better than repeated process
scaffolding. Claude may use its own tools, skills or subagents inside the one
blocking advisor turn; Codex still receives only one bounded terminal result.

## Continuation And Fallback

Reuse `session_id` when accumulated context is valuable. Start fresh for a blind
review or materially different frame. A Fable request may resolve to Opus;
treat the run as success, report both model fields, attribute the answer to
`resolved_model`, and do not invent the reason. Preserve a refusal instead of
silently rewriting the task or changing billing/tool authority.

Official volatile owners:

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
- https://code.claude.com/docs/en/model-config
