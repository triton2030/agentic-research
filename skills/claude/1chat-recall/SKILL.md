---
name: 1chat-recall
description: >-
  Use to record owner words a future choice will need — his words or an agent
  proposal he accepted — or, when a task or discussion touches a subject, to
  read his past quotes as dated context on how he thought; also corpus repair. His current decisions live in
  project docs and instructions, not here. Excludes handoffs and updating
  project docs.
allowed-tools: Bash Read Glob Grep
---

# Chat recall

## Why this exists

The corpus exists so that conversations with the owner do not start from
scratch each time. It serves a future agent facing a choice the owner never
discussed with it: how he thinks about the subject, what he likes and
dislikes, and why. Its core material is his longer reasoning about a concrete
thing. A record is worth keeping only if it would change such a choice.

The corpus is context, not canon. The owner's current decisions live in project
docs, instructions and the current conversation. A quote says what he thought
then; it is not a lookup of his decisions. It is the past and has probably
aged: he may have changed his mind, and a record's type is the strength of his
words at that moment. Still, it helps understand his intentions and wishes in
general.

He thinks aloud, and many remarks steer only the thing at hand: «сделай этот
текст разговорнее», «да удаляй». Recorded, they read as policy — a later agent
turns one text edit into "all texts here are conversational", a rule he never
gave. An unneeded record is not harmless: a later agent reads it as how he
thinks, and it buries the reasoning that matters.

His position often arrives as agreement with an agent's proposal: the agent says
"let's not do that", he answers «окей». A bare «окей» says nothing; the position
is what he agreed to. In the corpus that is a `selection` whose text is the
words of the accepted proposal, not his speech.

He speaks Russian, in fragments, and names one subject in different words.
Quotes stay verbatim: a paraphrase loses conditions and is later read as his
position.

## Task

Record owner words that will change a future choice — his speech or an agent
proposal he accepted — with their subject and conditions, and read stored
quotes yourself as dated context on how he thought.

## Goal

A future agent understands how the owner thinks without asking again and takes
the current rule from live files and the current conversation. The corpus holds
words with their subject — not a stream of working remarks and not a decision
registry. Your own judgment stays distinguishable and is never presented as his
intent.

## Modes

- When an owner remark or agreement may matter to a future choice, a
  `capture-needed` arrives, or a later remark changes a record of this same
  conversation → [Capture](references/capture.md).
- When a subject comes up — in a discussion or a task — and his earlier
  thinking would help you understand what he wants →
  [Retrieval](references/retrieval.md). Gather it so the conversation does not
  start from scratch; what he says now still outweighs it.
- When the owner explicitly orders validation, repair or backfill →
  [Integrity](references/integrity.md).

## Environment

The corpus is `_ops/chat-recall/` of the target project: one file per
conversation; `topics.md` is the subject vocabulary, not a summary of decisions.
Capture and retrieval share one root, `TARGET_PROJECT_ROOT` (default: the
current folder); an explicit `--project` overrides it for Capture. From a
subfolder, pass the project root. No `_ops/chat-recall/` at the root means
no corpus here: say so and continue on docs and the conversation.

Commands and schema belong to `--help` of the scripts in `scripts/`; a mismatch
between help and behavior is a tool defect. The corpus stays local; retrieval
reads stored quotes, not transcripts or the web. No owner profile and no derived
summary layer.

A new record needs no permission. A record of the current conversation may be
overwritten by the Capture rule. Deleting a record without a new version, or
changing a record of another conversation, only on the owner's explicit order
about that record.

Revisit this skill if an agent relies on a quote as a current decision against
a live file or the current conversation, working remarks or bare agreements
reach the corpus again, a record is announced without a receipt, words are
paraphrased, or one empty query is taken as proof the owner said nothing.
