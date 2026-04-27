---
name: 1guide-subagents
description: >
  Use only when the user explicitly asks for Codex subagents, delegation,
  parallel workers, or says to use multiple agents. This is a compact gotcha
  guide: treat subagents as a proposed method, name the missing judgment,
  decide whether a split is useful, keep blocking work local, name skills in
  worker prompts, keep scopes disjoint, and verify evidence. Do not trigger
  merely because a task could be parallelized.
---

# Guide Subagents (Codex)

The model already knows the basics of subagents. Use this guide only after the
user has explicitly asked for subagents, delegation, parallel workers, or
multiple agents. Its job is to avoid predictable failures: fake parallelism,
missing skill activation, copied prompt style, scope drift, status theatre, and
outsourced judgment.

Activating this guide does not force a launch. If the split is weak, continue
locally.

Do not launch subagents merely because a task has independent streams. Without
an explicit user ask, keep the work in the main agent and optionally mention the
parallelization opportunity in ordinary prose.

## Outcome Gate

Treat subagents as a proposed method, not the task.

Before splitting, name the judgment the request needs: speed, evidence,
critique, domain knowledge, disjoint implementation, validation, or synthesis.
If the needed judgment is strategic rather than executable, route to
`1strategy-discussion` instead of launching workers.

Prefer the cheapest shape that buys the needed judgment:

- main agent only;
- one sidecar worker;
- multiple disjoint workers;
- adversarial critique or evidence collection instead of implementation.

## Split

Use subagents for independent side streams: separate files, leaf implementation,
evidence collection, critique, or validation that can run while the main agent
keeps moving.

Keep with the main agent:

- the immediate blocking step;
- dirty or hotspot files;
- integration surfaces and synthesis;
- repo-level verification.

Give workers clean, disjoint scopes. One worker owns one scope. If two workers
need the same files or decision surface, the split is probably wrong.

## Brief

A good worker prompt names only what matters:

- role;
- owned scope;
- task;
- skills to use;
- boundaries;
- evidence/report expected.

Tell the worker explicitly which skills to use. Do not rely on it to infer skill
activation from the task. The launcher sees the broader context, so skill choice
belongs in the prompt.

Subagents copy the prompt's style, tone, and format. If you want a conversational
answer, prompt conversationally. If you want findings, prompt in a findings
shape. Prompt format steers output.

Brief for judgment, not obedience theatre. Add ordered steps only when sequence
is actually load-bearing or safety-critical.

## Gotchas

- **Broken telephone:** do not delegate synthesis through chains of summaries.
  Pass exact evidence; synthesize in the main context.
- **Outsourced judgment:** workers may collect evidence, critique, validate, or
  implement scoped slices. The main agent owns the delegation choice and final
  synthesis.
- **Sycophantic consensus:** multiple workers can agree on the same wrong answer.
  For validation, ask for evidence-first or adversarial critique.
- **Missing skills:** if a skill would improve the worker's job, name it in the
  prompt.
- **Scope drift:** workers report only owned scope. They do not summarize other
  workers or become mini-orchestrators.
- **Status theatre:** worker status is not truth. Check diffs, citations, logs,
  screenshots, or other evidence.
- **Verification inflation:** workers claim only scoped checks. The main agent
  owns integration and final verification.

## Plan-First

Do not pause for split approval by default. Use plan-first mode only when the
user asks to inspect or approve the split first.

Done means the split was real, worker claims were evidence-checked, and the main
agent integrated the result.
