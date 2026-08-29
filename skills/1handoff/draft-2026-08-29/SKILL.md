---
name: 1handoff
description: >-
  Use when $1handoff or /1handoff is requested, or when long repository work
  must move to a fresh session before continuation-critical state is lost. Not
  for a summary, report, or task plan.
---

# Handoff

## Unique Context

The next agent will hold this repository and one file path, and nothing else.
What dies with this chat is exactly what the files cannot hold: a route this
session disproved, an owner decision spoken once, a reading of the terrain that
looked obvious and turned out wrong, and the cost already paid to find that out.

## Owner's Goal

«хэндофф это для меня инструмент, чтобы один агент передал следующему агенту с
чистым окном все необходимое, чтобы тот агент не совершал его ошибок и уверенно
прошел работу дальше»

«не забывай про самую главную цель, чтобы новый агент прочитав хендоф мог
успешно продолжить работу а все процедуры хендофа как раз для этого и служат»

Every name, list and example below orients you toward that outcome and does not
bound it: do whatever the outcome needs inside the authority this task already
has, and never treat a list as the full extent of the work.

## Always True

- Create no more than one handoff in a chat.
- Deliver by returning the exact packet path, and let the owner open the next
  session by hand.
- Add no latest-handoff index, hook, automatic discovery, consumed state or any
  other lifecycle surface: manual delivery is the owner's standing choice, not
  a gap waiting to be closed.
- The packet is a dated delta and never a second truth. Live files and runtime
  state override it, and it never becomes a transcript, a summary, a task plan,
  a user profile or project canon — each of those already has its own owner.

## Work Through These Stages

1. Before anything is written into `_ops/handoffs/`, read
   `references/leave-the-project-current.md` and finish it, because the packet
   can only record what has already happened to the owner's words and to
   project state.
2. Once that stage is closed, read `references/write-the-packet.md` and write
   the file.
3. Before the path leaves this chat, read
   `references/read-it-as-the-next-agent.md`.
