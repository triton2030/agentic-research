---
type: concept
title: Chat recall capture policy
description: This page explains the core rules for what the chat-recall system should record and what kinds of distortion or metadata it should avoid.
tags: [chat-recall, capture, policy]
---

# Chat recall capture policy

The chat recall capture policy defines how owner statements should be preserved in the recall system. Across the pilot, the stable goal is to keep short, evidence-grounded records that stay close to what the owner actually said while avoiding interpretive drift and noisy metadata.

The earliest holder sets the baseline: the system should record the owner's quotes with dates, trigger automatically, and keep the shortest form that still preserves the point rather than the assistant's interpretation ([2026-07-22 skill creation](viking://resources/chat-recall-pilot/2026-07-22-105500-claude-d8a832a4/2026-07-22-105500-claude-d8a832a4.md)). That same source also narrows literalism: the quote should be "in principle literally a quote, but slightly shortened," which permits compression but not paraphrastic rewriting ([2026-07-22 skill creation](viking://resources/chat-recall-pilot/2026-07-22-105500-claude-d8a832a4/2026-07-22-105500-claude-d8a832a4.md)).

Later corrections sharpen the boundaries. On 2026-08-11, the user rejects "garbage metadata" and says the quote-writing script should reject such output instead of writing it ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)). In the same holder, the user also says the simpler system is better and more reliable, explicitly referencing a previous removal of an entire reading-script layer in favor of simpler mechanisms ([2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)). Together, these statements make cleanliness and simplicity part of the capture policy, not just implementation taste.

The policy also includes provenance and scope boundaries. Records are meant to capture the owner's meaningful statements, not to inflate the archive with assistant inference. On 2026-08-14, session-context cards are explicitly described as retrieval aids that "do not replace quotes, do not retell decisions, and are not treated as the owner's truth" ([2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)). That distinction keeps the quote archive authoritative while allowing supporting metadata.

## Implications

- Shortening is allowed only when it preserves the owner's point more faithfully than a looser paraphrase.
- Metadata must help retrieval or provenance; if it becomes noisy or approximate, it should be removed or blocked before write.
- Simpler capture mechanisms are preferred when they can satisfy the same evidence standard.
- Supporting context may exist, but it must stay visibly subordinate to the recorded quotes themselves.

## Sources

- [2026-07-22 skill creation](viking://resources/chat-recall-pilot/2026-07-22-105500-claude-d8a832a4/2026-07-22-105500-claude-d8a832a4.md)
- [2026-08-11 codex holder](viking://resources/chat-recall-pilot/2026-08-11-163847-codex-019ff09d/2026-08-11-163847_2more_5a7a2bfd_2.md)
- [2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)
