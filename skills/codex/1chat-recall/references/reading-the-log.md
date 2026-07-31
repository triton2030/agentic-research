# Reading the recall log

Contents: Bounded route; Reading for current work; Diagnostics.

`chat_digest.py` is the only retrieval owner. It treats every Markdown
star-block as a record. Metadata diagnostics never remove a record from
inventory, search, timeline, or `show`.

## Bounded route

Before opening this route, the runtime-specific root `SKILL.md` sets `DIGEST` to
its installed `scripts/chat_digest.py`. This shared reference never assumes a
Claude- or Codex-specific environment variable.

```bash
RECALL_DIR="<project>/_ops/chat-recall"

python3 "$DIGEST" "$RECALL_DIR" --check
python3 "$DIGEST" "$RECALL_DIR"
python3 "$DIGEST" "$RECALL_DIR" --query "субагент* параллел*" \
  --limit 5 --max-chars 4000
python3 "$DIGEST" "$RECALL_DIR" --query "память контекст" \
  --timeline --json --limit 5 --max-chars 4000 \
  | jq '{
      matched, returned, truncated, order, warnings,
      records: [.records[] |
        {record_id, timestamp, type, topic, text, diagnostics}]
    }'
python3 "$DIGEST" "$RECALL_DIR" --show <record-id>
```

The default command is a cheap topics/types/period inventory. `--query` builds
an in-memory SQLite FTS5 index with one record per document and BM25 ranking.
The record text has normal weight; `topic` has a small boost. Add original
terms, synonyms, and explicit Russian prefix forms such as `субагент*`.
Automatic lemmatization is intentionally absent.

Filters remain metadata, not query text:

```bash
python3 "$DIGEST" "$RECALL_DIR" --query "память контекст" \
  --type коррекция,правило-кандидат --agent <agent> --since 2026-07-01
python3 "$DIGEST" "$RECALL_DIR" --timeline --session <uuid>
```

Supported filters are `--type`, `--topic`, `--grep`, `--since`, `--until`,
`--agent`, and `--session`. Start agent-facing retrieval with `--limit 5` and
`--max-chars 4000`; widen only when the coverage gate below requires it. The
larger CLI defaults remain a compatibility ceiling, not a reason to spend it.

Human search output keeps only the stable ID, source date, evidence kind,
classification and excerpt; it marks records with diagnostics and omits file
addresses and the internal BM25 score. Use `--show` to recover complete text,
provenance, raw malformed metadata and address for a consequential candidate;
add `--verbose` only when the ranking or full parser record is under diagnosis.
`--json` returns `total`, `matched`, `returned`, `truncated`, `selection`,
quality counts, warnings, and records. With `--timeline`, it also returns
`order: newest-first`. In an agent-facing terminal, pipe JSON through `jq` so
only fields needed for the decision enter context, but retain `warnings` and
per-record `diagnostics`.

`selection=none` is a valid abstention, not a failure. A timeline orders known
timestamps newest-first and puts unknown records last. Bounded output therefore
keeps the newest evidence and drops older or uncertain records first. Date
filters omit records without a known date. Use `--show` for the complete text,
provenance, address, and diagnostics of one stable `record_id`.

## Reading for current work

Read the log to improve the current decision, not to produce a quote dump. Start
from the live choice: what owner evidence could change the goal, boundary,
adopted direction, quality criterion, or acceptable way of working? Search that
claim with original words, synonyms, prefix forms, and a broad topic filter when
useful. BM25 score selects candidates; it does not determine importance or
truth.

Within the resulting claim cluster, weigh evidence in this order:

1. Applicability to the current decision and scope.
2. Direct owner evidence: `quote` or `selection` before agent-authored `note` or
   malformed `raw`.
3. Commitment: an explicit correction or newly adopted decision can replace an
   earlier position; a later idea does not cancel an adopted decision merely by
   being newer.
4. Resolvable source time and its precision.
5. Retrieval coverage and diagnostics.

A later statement is presumptively current only when it addresses the same
claim and scope, actually corrects or replaces the earlier position, and its
source time is distinguishable at the recorded precision. A narrower statement
may be an exception rather than a replacement. Equal timestamps, same-day
date-only records, or unknown order require both records to remain visible.
For `type: факт`, recency identifies the owner's newer assertion, not
independent truth about the world.

Before declaring supersession, require `truncated: false` and
`matched == returned` for the chosen query, then check retrieval coverage:
search wording variants or the owning topic when a later paraphrase could have
been missed. If those gates do not close, state that the answer is based on an
incomplete window or abstain.

The useful reading result is a compact working context:

- active decisions, constraints, criteria, and preferences that can change the
  current work;
- the displaced position and why it no longer governs, when relevant;
- scoped exceptions, unresolved conflicts, and evidence gaps;
- source dates and `record_id` values for consequential claims.

If recall evidence conflicts with an active owner document, expose the
discrepancy instead of silently treating either surface as the other.
Do not promote repeated wording into a broader owner rule without saying that
the broader pattern is an inference. Chronology helps adjudicate relevant
evidence; it does not turn the dated log into current canon.

## Diagnostics

`--check` reports repair backlog but exits successfully so records remain
readable. Its summary counts records that carry diagnostics, not the number of
individual diagnostic labels. `--check --strict` is the validation gate and
exits non-zero while diagnostics remain. An invalid non-empty type or topic
becomes the corresponding repair sentinel while its original value remains
visible as `type_raw` or `topic_raw`; the raw topic also stays BM25-searchable.
Repair procedure and evidence rules live only in
[`repairing-the-log.md`](repairing-the-log.md).
