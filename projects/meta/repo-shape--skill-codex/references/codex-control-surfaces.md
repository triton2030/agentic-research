# Codex Control Surfaces

Use this reference when a rule is stronger as structure than as prose.

## Surfaces

- `AGENTS.md` and subtree instruction files: portable routing and placement rules.
- Skills: moment or topic instructions loaded when the trigger matches.
- `agents/openai.yaml`: Codex skill UI/policy metadata, including implicit invocation policy.
- Native subagents: independent read-only critique or delegated work when explicitly authorized by the user.
- Plugins / MCP / apps: external capability bundles and tool boundaries.
- Validators and scripts: deterministic checks that catch drift better than wording.
- Folder ownership: repo shape that makes the right owner obvious.

## Selection

Prefer the strongest layer that does not add unnecessary ceremony:

1. Validator/script when the invariant is mechanically checkable.
2. Folder or file ownership when placement prevents drift.
3. Skill when the rule needs fresh context at a trigger moment.
4. Instruction text when the rule is broad and portable.
5. Human checkpoint when judgment or approval is the real control.

## Red Flags

- A rule is repeated in many docs but has no validator or owner.
- A skill body is copied into root instructions.
- A Codex skill imports Claude-only runtime claims without marking them as external evidence.
- A config or plugin is assumed live without checking the current inventory.
