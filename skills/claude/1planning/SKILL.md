---
name: 1planning
description: >-
  Use at any thought of what to do next, «давай запланируем», or a big error
  (plans first): challenge whether to start, then prove the decomposition in
  chat before plan files. Not in native Plan mode.
---

# Planning

Plan files are written for agents, not the owner: this skill orchestrates the
autonomous work of many agents **in sequence**, clean window after clean
window, while the owner watches through the dashboard. Its own job is the
view from above — analyze the project and the whole map, decide what
genuinely matters now and what waits — and guard the entry to work.

## Goal

A decomposition proven in chat and the owner's yes — before a single plan
file changes. In hand afterwards: the chosen task named inside its epic, with
the reason it beats the queue.

## Protocol

1. **Read before planning.** Current epics and tasks, `GOAL.md`, and —
   mandatory — the project's root instructions plus the instructions and
   skills that govern this task's domain. Agents reliably plan past project
   rules, so quote in chat the lines that constrain this decomposition;
   found none — name the files read.
2. **Challenge admission — argue, including with the owner.** Can we start
   this task at all, and is it a good idea now: is it next by `порядок` and
   blockers on the map, what does it displace, what makes it matter more
   than the queue. Work that cannot find its epic is a question to the map
   (`1plan-map`), not a license to dig without one; the map's answer returns
   the work here.
3. **Decompose in chat, by the masters.** Write the steps directly in chat —
   the visible steps are the only proof decomposition happened — and name
   the book methods that shaped the cut, each with its specific point and
   the exact plan element it changed. Cut along a named axis — dependencies,
   independent branches, decision gates — never bare chronology (a genuinely
   dependent chain is a dependency axis: name it as such), and only to the
   nearest checkable frontier. Name the task's mode — **Wayfinding**: path
   materially unclear, subtasks resolve uncertainty, Next goes to the
   earliest expensive divergence, not the easiest; **Execution**: path
   clear, subtasks are results, at equal outcomes take the reversible
   door — and write the probe's answer in chat before claiming Execution:
   what the first step is, and whether it forces an invented product or
   architecture decision (it does → Wayfinding). An unknown stays a research
   step or a decision gate, never a silent premise; a material premise stops
   the cut until resolved.
4. **Close the grounds.** Run `1use-principles` over the cut — its trace is
   the principle names in the justification, each with what it settled;
   owner questions left after goal, principles and owner records go through
   `1interview-tool`. Then the owner's yes **to the shown decomposition** —
   the «давай запланируем» that opened the work is not it. Plan files only
   after it.
5. **Route and keep fresh.** Map composition changes, including a cut that
   spans epics → `1plan-map`; writing or continuing the task file →
   `1plan-task`; before any material step reread the current epic — stale
   epics or tasks are refreshed before the work continues.

## Boundaries

Native Plan Mode active → stay silent. Project goal — `1goal` · creating
principles — `1product-shaping` · side findings — `1findings`.
