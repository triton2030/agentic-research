---
type: analysis
title: Chat recall pilot chronology and change signals
description: This analysis traces the pilot's major decisions, corrections, and design shifts across the six chat-recall holders.
tags: [analysis, chronology, change]
---

# Chat recall pilot chronology and change signals

This analysis asks how the chat-recall pilot changed from its initial capture rules to later retrieval and autonomy discussions. The corpus shows continuity in evidence discipline and simplicity, but several important expansions and corrections appear over time.

## Question and scope

Question: what changed, what stayed stable, and where did the user explicitly correct the direction of the pilot?

Scope: six immutable holders dated 2026-07-22 through 2026-08-21, all under [chat-recall-pilot](viking://resources/chat-recall-pilot).

## Timeline

### 2026-07-22: baseline capture rules

The first holder defines the core of the system: record the owner's quotes with dates, trigger automatically, keep entries short, store them in `_ops/chat-recall`, and treat the skill as global across projects ([2026-07-22 skill creation](viking://resources/chat-recall-pilot/2026-07-22-105500-claude-d8a832a4/2026-07-22-105500-claude-d8a832a4.md)). This establishes the durable baseline for later work.

### 2026-08-11: retrieval evaluation and simplification pressure

The 2026-08-11 holder introduces a different concern: how to improve retrieval quality. Several corrections narrow the task from general experimentation to specific script improvement. The user says this is not testing the skill itself but testing the script inside it; the new script must be significantly better than both the current approach and ordinary tools; and it should stay light and fast ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)). The same holder also criticizes noisy metadata and restates a preference for simpler systems, which acts as a brake on overbuilt solutions ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)).

### 2026-08-14: retrieval broadens from quote-only search to session-level routing

The 2026-08-14 set adds the largest design change. The user proposes a short session-context card per file so search can find the right conversation even when the task wording is not present in the quote text ([2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)). This is an expansion, not a replacement: the same source says the card is not the owner's truth and does not replace quotes ([2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)). A later design selection formalizes a two-route retrieval model with separate `records` and `session_candidates` outputs ([2026-08-14 codex holder part 2](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_2.md)).

### 2026-08-20 to 2026-08-21: autonomy, preferences, and correction of overreach

The later holders move beyond retrieval mechanics into broader agent behavior. The 2026-08-20 set contains repeated decisions, candidate rules, boundaries, and preferences about agents ([2026-08-20 codex holder parts 1-4](viking://resources/chat-recall-pilot/2026-08-20-222832-codex-01a02036/Chat_recall_2026-08-20_codex_01a02036/Chat_recall_2026-08-20_codex_01a02036_1.md)). The 2026-08-21 holders continue this with corrections and process-oriented notes, showing that the pilot corpus is not only about recall tooling but also about how captured memory should constrain future agent work ([2026-08-21 codex holder 01a020be](viking://resources/chat-recall-pilot/2026-08-21-010201-codex-01a020be/2026-08-21-010201-codex-01a020be.md); [2026-08-21 codex holder 01a0236d](viking://resources/chat-recall-pilot/2026-08-21-133152-codex-01a0236d/2026-08-21-133152-codex-01a0236d.md)).

## Stable themes

Across all dates, three themes stay stable:

1. **Evidence should stay close to owner wording.** This starts on 2026-07-22 and is never revoked.
2. **Corrections matter.** The user repeatedly narrows or reframes tasks when the implementation drifts.
3. **Extra machinery needs justification.** Simplicity and usefulness are recurring filters, especially from 2026-08-11 onward.

## Uncertainty

The late August holders clearly emphasize agent behavior and preferences, but this pilot sample does not itself provide a complete global policy. The analysis therefore treats them as strong signals within the pilot corpus rather than a fully stabilized doctrine.

## Sources

- [2026-07-22 skill creation](viking://resources/chat-recall-pilot/2026-07-22-105500-claude-d8a832a4/2026-07-22-105500-claude-d8a832a4.md)
- [2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)
- [2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)
- [2026-08-14 codex holder part 2](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_2.md)
- [2026-08-20 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-20-222832-codex-01a02036/Chat_recall_2026-08-20_codex_01a02036/Chat_recall_2026-08-20_codex_01a02036_1.md)
- [2026-08-21 codex holder 01a020be](viking://resources/chat-recall-pilot/2026-08-21-010201-codex-01a020be/2026-08-21-010201-codex-01a020be.md)
- [2026-08-21 codex holder 01a0236d](viking://resources/chat-recall-pilot/2026-08-21-133152-codex-01a0236d/2026-08-21-133152-codex-01a0236d.md)
