## Model Baseline

- Give Opus 5 and Fable 5 a lightweight skill with progressive disclosure.
- Generic self-review, an automatic verifier, and fan-out are not part of the
  portable baseline. Add objective validation and an independent verifier
  according to the task/risk contract.
- Model, effort, thinking, long-run, and fallback rules belong to the current
  model owner/runtime. Do not copy them into the skill.
- Older Claude 4.x skills and prompts are historical migration evidence, not an
  active baseline or fallback.

## Source Discipline

- An Anthropic-endorsed claim requires a current official source:
  `platform.claude.com/docs`, `code.claude.com/docs`,
  `anthropic.com/engineering`, or `github.com/anthropics/skills`.
- Label local engineering as local engineering, not an Anthropic
  recommendation.
- Do not invent metrics, limits, or runtime availability. Recheck a drift-prone
  fact in live docs/runtime.

Current anchors:

- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices>
- <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview>
- <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5>
- <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5>
- <https://code.claude.com/docs/en/slash-commands>
