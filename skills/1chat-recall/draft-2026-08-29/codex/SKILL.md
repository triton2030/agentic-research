---
name: 1chat-recall
description: >-
  Use when owner speech should be captured; before consequential work that may
  depend on it; or to recover, restore, validate, repair, or backfill source
  evidence. Skip assent.
---

# Chat recall

## Unique context

The corpus preserves what the owner said; it does not say what is true now.
Corpus evidence stays local.

## Choose the current mode

1. Owner speech may matter after this turn → fully read
   [Capture](references/capture.md).
2. Prior owner speech may affect consequential work or a later answer →
   fully read [Retrieval](references/retrieval.md).
3. Retrieval ended `recovery-needed` because its normal route could not support
   a decision → fully read
   [Recovering recall coverage](references/reading-the-log.md).
4. This session is explicitly transferring recovered meanings into existing
   owner files → finish Retrieval first, then fully read
   [Restoring meanings](references/restoring-meanings.md).
5. A record needs provenance repair or the owner requests pre-capture backfill
   → fully read
   [Repairing the log](references/repairing-the-log.md).
6. The owner requests corpus structural validation → fully read
   [Validating the corpus](references/validating-the-corpus.md).

Complete triggered modes in numbered order, returning here after each; only the
reference-defined receipt closes a mode, never a candidate list or unread
address.
