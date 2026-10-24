# Integrity

## Goal

The corpus state is checkable, and each change the owner ordered is backed by
its source scene and a visible before/after. His words are never replaced by
your editing; whatever stays unrepaired is named with a reason.

## Why

A diagnostic reports state; it does not authorize changing history. A transcript
may disappear, and then a past scene cannot be rebuilt.
[chat_recall.py](../scripts/chat_recall.py) confirms message provenance,
timestamp and source address, but not who wrote each fragment inside a paste.
Source and stored quote are for comparison, not for improving speech.

## Criteria

- Only records the owner explicitly ordered are changed, each with its source
  and a before/after comparison. Validation alone does not authorize repair; a
  label that honestly describes an old unknown is not a formatting error.
- The raw source stays unchanged and the backup lives outside the corpus;
  otherwise a check compares a repaired record with already repaired evidence,
  or finds the backup as a second voice of the owner.
- Restored units do not duplicate stored remarks: a repeat creates false
  independent confirmation. An unrecoverable scene stays a gap.
- After a change, show a repeated validation and the remaining diagnostics. A
  clean report before the change proves nothing about its result.

## When you check or change the corpus

[chat_digest.py](../scripts/chat_digest.py) runs the check:

```bash
ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"
TARGET_PROJECT_ROOT="${TARGET_PROJECT_ROOT:-$PWD}"
uv run --locked --script "$ROOT/scripts/chat_digest.py" \
  "$TARGET_PROJECT_ROOT/_ops/chat-recall" --check --strict
```

For an explicitly ordered restore of a named session, run `chat_recall.py` with
`python3`; its interface is `--help`. A transcript is not a fallback for
ordinary search: access to it belongs to this order only. If the session is not
named, find its id with `duckdb`: `select filename from
read_text('~/.codex/sessions/**/*.jsonl') where content like '%<фрагмент сцены>%'`.
Quote and provenance come only from `chat_recall.py`.

Before a change: an initial validation, a proven source and an external backup;
after it: a repeated validation. This order makes comparison possible; it is
not a license to fix everything found.

A confirmed missing remark goes back to the router as `capture-needed` with
target project, session and original timestamp, and ordinary Capture records
it. The text of an existing quote is not rewritten: only a source-confirmed
deletion within the order is allowed. Metadata rely on the same scene; deleting
a record requires the owner's word about it.

## When you restore addresses

`#L` marks a current line, not a record's identity. First read the referring
document and the quote: a neighboring line may be another decision. A hash
computed from whatever line is there now fixes nothing.

[chat_repair.py](../scripts/chat_repair.py) adds stable headings to verified
old records. Pass each as `--address 'file.md:line sha:verified-hash'` and keep
`--plan-out` outside the corpus. That call only builds a plan with old and new
addresses. After checking the mapping, `--apply-plan` re-checks file hashes and
applies the plan under the shared lock; on any mismatch it refuses to write.
While it runs, keep manual edits and old helpers away from those files: they
bypass the lock.

Headings change neither quotes nor file names but shift line numbers: move the
verified incoming links to the `#recall-…` addresses from the plan. The helper
does not guess what an old link meant and does not rewrite documents. Show how
much was moved and which old links remain; archived material does not become a
live document for the sake of a clean report.
