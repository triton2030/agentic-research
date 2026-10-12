# Agentic Research

`agentic-research` is a knowledge workshop and testing ground for AI agent skills,
hooks, prompts, instructions, and working agreements.
It helps agents understand the owner's context, act with appropriate autonomy,
and use local knowledge and criteria when making decisions.

The deliverables are reusable skills and patterns used across projects.
This repository holds their research, source packages, experiments, and history.
Most working documents are in Russian; this README is the English entry point.

## Start here

1. [AGENTS.md](AGENTS.md) — shared agent instructions, repository map,
   and sources of truth.
2. [INDEX.md](INDEX.md) — shortcuts to knowledge found through earlier research.
3. [Project goal](_ops/GOAL.md) — scope, current model targets,
   completion criteria, and stop rules.
4. [Product frame](_ops/product-frames/agentic-research.md) and
   [product principles](_ops/product-frames/agentic-research.principles.md) —
   guidance to read before substantive work.

The goal document defines the working model set and each model's role.
Older model references remain historical research evidence.

## Repository map

| Location | Contents |
| --- | --- |
| [knowledge/](knowledge/README.md) | Knowledge organized by subject: models, runtimes, agents, skills, instructions, and concepts. |
| [science/](science/README.md) | Research into LLM reasoning, with evidence status, verification, and experiments. |
| [skills/shared/](skills/shared/README.md) | Source packages shared across runtimes and the package ownership registry. |
| [skills/claude/](skills/claude/README.md), [skills/codex/](skills/codex/README.md) | Runtime-specific source packages or tracked copies of shared packages. |
| `skills/1<name>/` | Skill development history, snapshots, and research evidence. |
| [experiments/](experiments/) | Independent experiments governed by their local instructions. |
| [_ops/](_ops/README.md) | Project goals, owner quotes, findings, interviews, plans, and handoffs. |
| [_workspace/](_workspace/README.md) | Local working artifacts, HTML previews, and orchestration materials; generally excluded from Git. |

## Working with this repository

Before changing a skill, start with [skill knowledge](knowledge/скил/README.md)
and locate its source package through the ownership registry.
Read any `product-frame*.md` files in that package alongside the project frame
and principles.
Frames under `skills/1<name>/` belong to the historical archive.

When a tracked source package exists, edit it first; the installed copies in
`~/.claude/skills/` and `~/.codex/skills/` are its projections.
If there is no tracked source package, the installed package remains
the source of truth.

[_ops/chat-recall/](_ops/chat-recall/AGENTS.md) stores verbatim owner quotes,
one file per conversation, captured by `1chat-recall`.
Its `topics.md` is a topic vocabulary, not a summary of decisions.
`_ops/user-said/` is its frozen, read-only predecessor.
Read findings, interviews, and plans when the current task calls for them.

This README provides navigation; the project contract lives in `_ops/GOAL.md`.
Use the applicable source documents and task criteria before making
substantive changes.
