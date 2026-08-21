---
type: concept
title: Session-context retrieval model
description: This page describes the file-level session-context card introduced to improve recall retrieval without confusing retrieval hints with owner evidence.
tags: [chat-recall, retrieval, session-context]
---

# Session-context retrieval model

The session-context retrieval model adds one short, continuously maintained card per recall file so search can locate the right conversation even when the relevant task terms do not appear in the captured quotes. Its purpose is retrieval guidance, not evidentiary substitution.

The key proposal appears on 2026-08-14: each quote file should have a short description of the session context, written in a keyword-friendly way and updated if the session's focus changes ([2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)). The same holder immediately constrains the idea: the card helps find the right conversation, but it does not replace quotes, does not summarize decisions, and is not treated as the owner's truth ([2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)).

A later design selection specifies the retrieval behavior in more operational detail. The `session-context` field remains separate in JSON and `--show`; normal record ranking searches only quotes and `context-note`; session cards are indexed separately as one BM25 line per file; and `session_candidates` appear as a separate top-5 route when a query term is absent from the record index ([2026-08-14 codex holder part 2](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_2.md)). If no record matches exist, the same route becomes the fallback, and timeline mode may then return all records from the matched files ([2026-08-14 codex holder part 2](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_2.md)).

The model also depends on a one-time corpus improvement step. The user says existing quote files are not yet in the needed shape and should be manually updated so retrieval can be tested on the real archive ([2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)). Another correction says this context cannot be derived from the saved quote snippets alone; the relevant sessions must be found and actually read, at least for accessible Codex sessions ([2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)).

## Boundaries

- Session context is file-level retrieval metadata, not quote-level evidence.
- It is allowed to route attention toward a file, but not to reorder quote evidence as if it were itself a quote.
- The card can justify which full conversation to read next, but not what the owner's position was.

## Sources

- [2026-08-14 codex holder part 1](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_1.md)
- [2026-08-14 codex holder part 2](viking://resources/chat-recall-pilot/2026-08-14-124028-codex-019fff2e/Chat_recall_2026-08-14_codex_019fff2e/Chat_recall_2026-08-14_codex_019fff2e_2.md)
