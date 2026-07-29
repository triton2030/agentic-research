---
name: 1chat-recall
description: >
  Save and find source-bound owner words: automatically capture durable
  decisions, corrections, preferences, and facts from the current Claude
  session; recover earlier current-session input after compaction; search
  `_ops/chat-recall` for requests such as “what did I say?” or “find my quotes”;
  and repair an existing malformed record. Metadata errors never hide a quote.
  Search other sessions only while repairing an existing record.
allowed-tools: Bash(python3 *), Read, Grep, Glob
---

# Chat recall

## Invariant

The quote is primary. A wrong or missing date, type, topic, or format never
cancels it. Retrieval includes exact, legacy, partial, multiline, and raw
records. Metadata is repaired; valuable text is not dropped.

The log is dated evidence, not current canon. A later quote may supersede an
earlier one, and an approximate timeline must not be presented as current
truth.

## Router

- A fresh durable owner thesis appeared: capture it automatically in the same
  turn. Skip simple approvals, one-off commands, credentials, and quoted or
  pasted material that is not the owner's position.
- Earlier input or a Plan/AskUserQuestion choice from the current session can
  change a durable result: read current-session evidence.
- The user explicitly asks what they said, asks to find quotes, or requests a
  recall harvest: use corpus retrieval.
- An existing record has diagnostics or malformed metadata: use repair. This is
  the only branch allowed to search another session.

## Current-session evidence

Use the native current-session reader when earlier user input or a Plan answer
can change a durable result:

```bash
RECALL="${CLAUDE_SKILL_DIR}/scripts/chat_recall.py"
SESSION="${CLAUDE_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-}}"
python3 "$RECALL" --session-id "$SESSION"
```

The default is bounded and excludes the current turn. Add
`--include-current-turn` only when locating the exact record for a fresh
capture; add `--all` only when the bounded result is insufficient. A Plan
option is agent-authored: represent it as a selection (“user selected X”), not
a verbatim quote.

## Capture

Automatically capture one durable owner thesis at a time: decision, correction,
preference, idea, criterion, candidate rule, personal workflow fact, or fact.
Preserve the owner's wording by deletion-only shortening; do not turn agent
summaries, inserted text, credentials, or one-off commands into quotes.

For an exact transcript record:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/chat_capture.py" \
  --quote "<owner words>" \
  --source-timestamp "<timezone-aware transcript timestamp>" \
  --type решение --topic <handle> --agent claude \
  --project "$PWD" \
  --session "${CLAUDE_SESSION_ID:-${CLAUDE_CODE_SESSION_ID:-}}"
```

`--source-timestamp` always has a value. It accepts timezone-aware ISO, an
approximate ISO/date, or `unknown`. Approximate/unknown records must also pass
`--timestamp-source`, normally `--timestamp-precision`, and optionally
`--source-ref`. Use `--kind selection` for a chosen agent-authored option and
`--kind note` for a later explanation.

Default `source=transcript` is allowed only after reading that exact native
record. A remembered, inferred, filename-derived, or semantically matched time
is repaired/approximate even when written as a timezone-aware ISO; pass its
honest source and non-exact precision.

If the fresh message has no transcript record, preserve it with an observation
timestamp and explicitly pass both `--timestamp-source turn-context` and
`--timestamp-precision minute` (or `date`). Never present observation time as
source-exact; capture rejects that combination.

Type is one of `решение`, `коррекция`, `предпочтение`, `идея`, `критерий`,
`правило-кандидат`, `обо-мне`, `факт`, or the repair sentinel
`неопределено`. Unknown topic is `без-темы`.

## Corpus retrieval

For an explicit quote search or harvest, establish the runtime-specific
variables:

```bash
DIGEST="${CLAUDE_SKILL_DIR}/scripts/chat_digest.py"
RECALL_DIR="$PWD/_ops/chat-recall"
```

Then follow
[`references/reading-the-log.md`](references/reading-the-log.md), which owns
`check`, inventory, BM25, filters, timeline, `show`, bounded output, and
abstention.

## Repair

Historical search outside the live session is allowed only to repair an
already-existing recall record. Follow
[`references/repairing-the-log.md`](references/repairing-the-log.md).

In a read-only task, show the repair backlog. In a mutation-authorized task,
repair it session-by-session, use exact only after native text/choice
verification, and explicitly mark unresolved metadata.

## Boundaries and stop

- `chat_digest.py` owns `_ops/chat-recall` retrieval; generic Markdown search
  does not replace it. Screen history is not native transcript evidence.
- Do not send quotes or transcript evidence to network tools, import quotes from
  unrelated chats, or promote the dated log to current canon.
- Stop after the fresh durable theses are captured or the bounded question is
  answered or explicitly abstained, with provenance and diagnostics visible.
