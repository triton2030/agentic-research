# Repairing the recall log

The quote or selection is the asset. Wrong date, type, topic, or syntax is
repairable metadata and must never justify hiding, skipping, or deleting it.
Repair only an already-existing local recall record.

## Evidence order

For each diagnostic, work by session and stop at the strongest evidence found:

1. Open the native transcript named by the record's `session:`.
2. Search an exact unique text fragment across all local Claude/Codex
   transcripts and local git branches.
3. Use a bounded semantic or manual search over local history.
4. Infer only what filename, frontmatter, or raw time directly supports.
5. If evidence is absent, keep the record with timestamp `unknown`.

Never send quotes to a network tool. Never import new quotes from unrelated
chats. A semantic match alone is not exact evidence.

## Repair rules

- Compare the stored text or selected option with the native record before
  assigning `precision: exact`.
- Exact transcript records keep the short line format without extra provenance.
- Repaired or approximate records add inline `source`, `precision`, and, when
  useful, `source-ref`.
- Valid precision is `exact`, `minute`, `date`, or `unknown`.
- Preserve one semantic type. If evidence cannot support one, use
  `type: неопределено`; do not combine types.
- If a topic cannot be recovered, use `topic: без-темы`.
- When adding either sentinel through `chat_capture.py`, use `kind: note`;
  sentinels are not allowed on a fresh quote.
- Do not change an existing quote or selection into `note` merely to attach a
  sentinel; the note-only rule applies to a newly added repair explanation.
- AskUserQuestion/Plan choices use `kind: selection`.
- Agent-authored summaries use `kind: note` unless a source-bound owner quote
  is actually recovered.
- Preserve malformed content as `kind: raw` until its structure is repaired.
- Merge duplicate holders only when the same session occurs twice inside the
  same project corpus. The same session in different project corpora is valid.

For a fresh user message missing from the native transcript, capture the
observation timestamp with `source: turn-context` and an honest non-exact
precision. Never label capture time as transcript-exact.

## Mutation boundary and proof

In read-only work, report the `--check` backlog and do not rewrite it. When
mutation is authorized, repair every reported record that can be repaired and
leave unresolved ones explicitly marked.

Before a corpus rewrite, save checksums and back up untracked originals outside
the scanned corpus. Afterward prove:

- the multiset of record texts and raw blocks did not shrink;
- every star-block is available through inventory/query/show;
- every malformed record has diagnostics or was repaired;
- type/topic are valid or explicit sentinels;
- approximate provenance is visible;
- one project corpus has at most one holder per session.
