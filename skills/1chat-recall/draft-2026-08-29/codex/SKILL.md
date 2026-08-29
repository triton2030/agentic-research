---
name: 1chat-recall
description: >-
  Use when owner speech may matter later; before consequential work that may
  depend on prior owner words; or for bounded recall recovery, restoration,
  repair, backfill, or validation.
---

# Chat recall

## Goals

- Preserve consequential owner speech during the turn in which it is spoken.
- Before consequential work that may depend on earlier owner speech, recover an
  applicable position from literal evidence or `abstain`.
- After a source-bound mode receipt, continue the original work instead of
  treating recall as its final product.

## Shared boundaries

- Search metadata routes reading; it is neither owner evidence nor current
  truth.
- Keep corpus evidence local; never send it to network tools.

## Choose exactly one current mode

Fully read the one matching reference and complete that mode before selecting
another:

1. Owner speech may matter after this turn →
   [Capture](references/capture.md).
2. Prior owner speech may affect consequential work or a later answer →
   [Retrieval](references/retrieval.md).
3. Retrieval ended `recovery-needed` because its normal route could not support
   a decision →
   [Recovering recall coverage](references/reading-the-log.md).
4. This session is explicitly transferring recovered meanings into existing
   owner files after completed Retrieval →
   [Restoring meanings](references/restoring-meanings.md).
5. A record needs provenance repair or the owner requests pre-capture backfill
   → [Repairing the log](references/repairing-the-log.md).
6. The owner requests corpus structural validation →
   [Validating the corpus](references/validating-the-corpus.md).
