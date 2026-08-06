# Claude skill authoring 5

## Claude-Specific Done

- References are one level deep and every bundled file has an action-changing
  route from `SKILL.md`.

- The actual live Claude skill root is verified; no path migration is inferred
  from another runtime.

- No `agents/openai.yaml`, Codex-only tool names, or Codex validation commands
  remain in the Claude projection.

- Tracked runtime projection and installed package match the shared owner.

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
