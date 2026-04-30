# Opus 4.7 Prompting

Use this reference when composing `prompt`, `systemPrompt`,
`appendSystemPrompt`, or `skill-audit` instructions for Claude through the
bridge.

Sources:

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- https://platform.claude.com/docs/en/about-claude/models/migration-guide
- https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7

## Default Shape

Use a short structured prompt:

```xml
<role>What Claude is responsible for in this run.</role>
<task>The exact outcome to produce.</task>
<context>Only facts that change the work.</context>
<constraints>Allowed moves, must-not rules, tools, and boundaries.</constraints>
<evidence>What files, logs, tool calls, checks, or citations must support the answer.</evidence>
<output>Final answer shape and stop condition.</output>
```

## Rules

- Be explicit about the desired output, constraints, and stop condition.
- Add context or motivation when it helps Claude choose correctly.
- Use examples only when format, tone, or edge cases are fragile.
- Use XML tags when instructions, context, examples, and user input might blur.
- Prefer telling Claude what to do over only saying what not to do.
- Match the prompt style to the output style when formatting matters.
- For long context, put large documents/context before the query and ask for
  evidence before conclusions when accuracy matters.
- For coding, ask for a general solution, not just a test-passing patch.
- For temporary files, tell Claude whether to clean them up.
- Before finishing, ask Claude to verify the answer against the criteria.

## Opus 4.7 Notes

- Opus 4.7 follows instructions more literally than 4.6, especially at lower
  effort. Say what should happen instead of relying on implication.
- If reasoning looks shallow on a complex task, raise effort/profile rather
  than adding a long step-by-step ritual.
- Use `high` or `xhigh` effort for intelligence-sensitive agentic work when
  the runtime exposes effort. The bridge `turbo` profile uses max effort.
- Opus 4.7 may use tools less often by default. If tools are required, say when
  and why to use them.
- For multiple independent operations, explicitly request parallel tool use.
- Opus 4.7 has better progress updates during long agentic traces. Ask for
  shorter or differently shaped updates only when the default is wrong.
- Do not use sampling parameters as a control surface for Opus 4.7 API work;
  behavior should be guided through prompts, effort, and task scope.
- Token counting changed in 4.7. Leave more headroom for long prompts and
  image-heavy work.

## Bridge-Specific Checklist

Before `claude_run`:

1. Pick the profile: `normal`, `read-only`, `no-memory`, `no-skills`,
   `skill-audit`, `streaming-observe`, or `turbo`.
2. State memory/skill/tool boundaries explicitly.
3. Put evidence requirements in the prompt, not only in the final Codex answer.
4. For skill/context audits, require tool evidence and use `claude_audit_skill`
   or bridge logs; never accept self-report alone.
5. For long work, plan to `peek` during the run and `kill` if the direction is
   visibly wrong.
6. If the user wants Claude's answer visible in Codex chat, make the requested
   output self-contained; Codex will relay the bridge `chat_relay.text` field.
