# Claude from Codex

## When choosing the route

From Codex, launch Opus only in a T3 Code thread, where the owner watches
the work. The standalone Claude MCP bridge, Claude CLI and Google script
are not Opus fallbacks, even if their tools remain available. If T3 is
unavailable, follow the [connection checks](t3-code.md#connection) and report
any remaining blocker; do not switch transports.

## When choosing the model

Use Claude for an independent second opinion when no other family was named.
The owner's defaults are:

| Work | Model | Effort |
| --- | --- | --- |
| Documents, research, advice and other non-code work | `claude-opus-5-5` | `high` |
| Code work | `claude-opus-5-5` | `max` |
| Exceptional problems needing extra reasoning | `claude-fable-5-1` | `medium` |

Fable is the exception, not the default. An explicit choice for the task and
the calling environment's rules take precedence. Check the current catalog
with `orchestrator_capabilities` if the requested model or effort is missing;
do not silently substitute another model.

## When launching

The provider is `claudeAgent`. Its option is `effort`, not Codex's
`reasoningEffort`. For example, the default for non-code work is:

```json
{
  "instanceId": "claudeAgent",
  "model": "claude-opus-5-5",
  "options": [{"id": "effort", "value": "high"}]
}
```

Pass that selection to `t3_thread_launch` with the project, brief and runtime
mode described in the skill. The old bridge's `profile`, `session_id` and
`claude_ask` parameters are not T3 launch parameters. Continue through the
returned T3 `threadId`, using the skill's normal send, wait and read route.

## When the task needs independent judgment

A fresh T3 thread has no prior conversation with you, but Claude receives
the owner's Claude Code instructions, skills, hooks and project setup. This
was observed in the [2026-10-19 probe](t3-code.md#claude-in-a-thread).
The old bridge's launch without local settings is not preserved by T3;
the exposed T3 launch tool has no switch for that mode. If isolation from
these instructions is required, report that gap before using this route.

Give the original question and source files, keeping your proposed answer
out of an independent review. The shared role briefs already cover evidence
and permission to leave a sound result unchanged. Fable benefits from the
whole ambiguous problem and its real constraints; avoid prescribing a chain
of reasoning. Effort controls computation, not the required answer length.

## When interpreting a response

Use T3 run status and paginated thread reads. The retired bridge's text caps,
turn limits, terminal fields and model validation do not describe T3. A model
name in the agent's prose is not proof of the model used; inspect the run's
provider and model. Completion still requires the checks of the actual task.
