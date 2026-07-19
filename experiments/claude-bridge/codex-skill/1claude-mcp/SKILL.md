---
name: 1claude-mcp
description: >-
  Когда нужно независимое ревью, второе мнение или совет от принципиально другой
  модели, либо пользователь прямо просит Claude, Opus или Fable: используй
  managed Claude Bridge. Native Codex fresh eyes → `1fresh-eyes`.
---

# Claude MCP

Use Claude for a genuinely different model-family perspective, a retained
Claude specialist, or explicitly authorized Claude-side work. Always use the
managed bridge, never a raw `claude` subprocess. Codex owns scope, synthesis,
user communication, and acceptance; Claude's answer is evidence, not a verdict.

## Default Route

- One review or answer: `claude_run(profile: "advisor")` on `opus`.
- Retained specialist: `claude_thread_start`, then `claude_thread_send`.
- Independent opinions: separate fresh named threads, which may run in parallel.
- Exceptional hardest/longest judgment: `fable-advisor`, normally a thread.
- Authorized edits: `worker` plus exact project-relative `writeFiles`.
- Long terminal work: add `useTmux: true`.

Use native Codex subagents for ordinary Codex delegation. Use `unrestricted`
only with explicit broad execution/write authority.

Every start validates Claude.ai subscription auth and refuses an unsafe route.
Use `claude_doctor` only for setup, auth, model, or CLI compatibility failures.

## Brief Claude

Pass the current decision state and exact owner sources, not a raw chat dump:

```xml
<role>External role and authority.</role>
<task>Exact deliverable and stop condition.</task>
<claim>Plan, diff, conclusion, or risk to challenge.</claim>
<sources>Exact files, logs, URLs, cwd, or addDir roots.</sources>
<boundaries>Read/write/tools authority and must-not actions.</boundaries>
<evidence>Required evidence; separate verified fact from inference.</evidence>
<output>Verdict first; compact decision handoff, optional evidence appendix.</output>
```

State the intent behind material constraints and facts Claude must not invent.
Ask for findings, evidence, uncertainty, and a direct verdict, never private
reasoning. Default to about 1200 words unless the user needs a long deliverable;
put optional depth after `## Evidence appendix` for selective relay.

## Models And Threads

`advisor` is the normal read-only Opus route. Reserve fixed read-only
`fable-advisor` at `xhigh` for capability-sensitive long-horizon judgment.
Inspect `resolved_model_history` and `resolved_model`: a Fable request may end
on Opus after a classifier fallback, and a missing identity is unknown.

Keep every `thread_id`/`run_id` pair separate and always pass the current `cwd`.
A thread is bound to its UUID, profile, model, effort, cwd, Git worktree, and
ref. Continue only when inherited context is useful; start fresh for a blind
review, disagreement, new role, branch/worktree, or model policy.

Use these references only for the named non-routine branch:

- [current-model-routing.md](references/current-model-routing.md) — model-policy
  changes or routing diagnosis;
- [fable-agent-prompting.md](references/fable-agent-prompting.md) — unusually
  long Fable work, delegation, refusal, or fallback;
- [opus-agent-prompting.md](references/opus-agent-prompting.md) — tuning Opus
  effort or delegation beyond the default brief.

## Authority And Claude-Side Capabilities

`worker` requires a Git worktree, clean targets, and exact `writeFiles`. Its
terminal check proves only the detected persistent footprint stayed in scope;
it is not an OS sandbox and never auto-reverts. Read-only runs also flag a
persistent worktree change, but attribution is unknown in a shared worktree.
Inspect warnings and the final diff before accepting edits.

Claude's configured skills, plugins, MCP tools, and auto memory remain available
unless a diagnostic profile disables them. Use `claude_audit_skill` only when
exact structured Read evidence matters; self-report is not read proof.

Claude-internal subagents belong to one Claude lead and do not create independent
Codex-owned opinions. Define them only for valuable independent fan-out, with a
self-contained deliverable and read/write/tool boundary. Read
[claude-agent-orchestration.md](references/claude-agent-orchestration.md) before
using supplied `agents`, nesting, or experimental teams.

## Finish Or Recover

Start one long `claude_wait`. If the host returns a continuation/session handle,
continue that same host call rather than launching another bridge wait. Observe
only when progress matters, passing that consumer's previous `next_cursor`.
A timeout does not stop Claude.

The terminal wait is the acceptance packet. Use `claude_result` only after
restart, compaction, or a lost wait. Read the answer once through
`claude_relay`; follow `next_cursor` only when the remainder matters. Do not open
the full report/output by default; inspect targeted evidence for warnings,
failure, model switching, or write-scope acceptance.

Close only at `completed`, legacy `completed_unknown`, `failed`, `killed`, or a
safely explained `orphaned`. `completed_unknown` permits relay but is not
verified success. Kill only the saved run/process/tmux session, never by broad
process name.

Read [managed-runs-and-relay.md](references/managed-runs-and-relay.md) only for
orphan recovery, legacy state, cleanup, or lifecycle debugging. If MCP is absent
or stale, use the repo-controlled CLI once; never raw Claude. Read
[mcp-failure-handling.md](references/mcp-failure-handling.md) only after a
managed call fails, and stop if neither controlled surface can prove a live tail.
