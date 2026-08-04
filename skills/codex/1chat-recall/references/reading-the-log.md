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

# One-time bootstrap. This is the only command allowed to use the network.
uv run --locked --script "$DIGEST" --prepare

python3 "$DIGEST" "$RECALL_DIR" --check
python3 "$DIGEST" "$RECALL_DIR"
uv run --offline --locked --script "$DIGEST" "$RECALL_DIR" \
  --query "субагент* параллел*" \
  --limit 5 --max-chars 4000
uv run --offline --locked --script "$DIGEST" "$RECALL_DIR" \
  --query "память контекст" \
  --timeline --json --limit 5 --max-chars 4000 \
  | jq '{
      retrieval, retrieval_complete, candidate_count,
      returned, truncated, truncated_by, order, warnings,
      records: [.records[] |
        {record_id, timestamp, type, topic, text, diagnostics}]
    }'
python3 "$DIGEST" "$RECALL_DIR" --show <record-id>
```

The default command remains a cheap topics/types/period inventory. The first
`--prepare` downloads the pinned `intfloat/multilingual-e5-small` ONNX model and
locked Python runtime dependencies into the local cache (about 465 MB on the
current Mac). It never reads the recall corpus. Query commands use
`uv --offline`; a query never downloads a model or sends quote text to a network
service. Set
`CHAT_RECALL_CACHE_DIR` only when the default `~/.cache/chat-recall` location is
unsuitable. Keep `--locked` on both prepare and query commands so the adjacent
script lock remains authoritative.

`--query` now uses local hybrid retrieval by default:

1. Metadata filters narrow the corpus before either ranker runs.
2. In-memory SQLite FTS5/BM25 is the admission gate. If it finds no lexical
   candidate, the command returns `selection=none` without loading the model.
3. The pinned multilingual E5 model ranks the filtered records. Equal-weight
   reciprocal-rank fusion combines the first 40 BM25 and dense candidates.

The content-addressed SQLite cache stores only SHA-256 hashes and 384-dimensional
float vectors, never quote text. Its profile includes the model revision,
FastEmbed version, pooling, normalization, and E5 prefix scheme, so a changed
profile cannot silently reuse old vectors. The RRF score is candidate-routing
evidence, not a probability, relevance threshold, or claim about truth. The
first query over previously unseen quote hashes computes their vectors and can
therefore take materially longer; later queries reuse the shared local cache.

Use explicit lexical-only mode when bootstrap is unavailable or when diagnosing
exact-term behavior:

```bash
python3 "$DIGEST" "$RECALL_DIR" --query "субагент* параллел*" \
  --lexical --limit 5 --max-chars 4000
```

Original terms, synonyms, and Russian prefix forms such as `субагент*` remain
useful because BM25 is the honest abstention gate. Automatic lemmatization is
intentionally absent: measured prefix/stopword variants did not improve hit@5
over BM25 on the maintained Russian paraphrase regression.

The bundled regression fixture declares `corpus.project: agentic-research` and
the evaluator rejects another corpus as `corpus-mismatch` before checking target
IDs. A different corpus needs its own self-describing `--cases` fixture; missing
targets inside the declared corpus remain a distinct failure. Hit@5 measures
retrieval only: it cannot decide whether a context note adds surprise or whether
later evidence semantically supersedes an earlier statement.

Filters remain metadata, not query text:

```bash
uv run --offline --locked --script "$DIGEST" "$RECALL_DIR" \
  --query "память контекст" \
  --type коррекция,правило-кандидат --agent <agent> --since 2026-07-01
python3 "$DIGEST" "$RECALL_DIR" --timeline --session <uuid>
```

Supported filters are `--type`, `--topic`, `--grep`, `--since`, `--until`,
`--agent`, and `--session`; query filters run before ranking. Start agent-facing
retrieval with `--limit 5` and `--max-chars 4000`; widen only when the coverage
gate below requires it. The larger CLI defaults remain a compatibility ceiling,
not a reason to spend it.

`--limit` is the maximum number of returned records, not a guaranteed count.
The hard `--max-chars` budget applies to the complete rendered output and can
therefore return fewer records than `--limit`. Inspect `truncated_by`: `limit`
means the record ceiling was reached, while `max_chars` means the output budget
was reached. `--head` changes only the excerpt length in human output and is
ignored with `--json`. `truncated` and `truncated_by` describe presentation
only. Increase both budgets until `truncated: false` when the task truly needs
every generated candidate; this is not proof that every semantically relevant
record exists in the pool.

Human search output labels the denominator as generated candidates. It keeps
only the stable ID, source date, evidence kind, classification and excerpt;
marks records with diagnostics; and omits file addresses and the internal rank
score. Use `--show` to recover complete text, provenance, raw malformed metadata
and address for a consequential candidate. An optional agent-authored
`context-note` appears only in `show`/full-record output and never contributes to
BM25, embeddings, or record identity. Expect it for an isolated quote, but read
its contents only as non-inferable context, never as a restatement of the quote.
Add `--verbose` only when ranking or the full parser record is under diagnosis.
For queries, JSON adds `retrieval`, `retrieval_complete`, `candidate_count`, and
for hybrid retrieval `candidate_depth`. `matched` remains a compatibility alias
for `candidate_count`; neither field means independently verified relevance.
`retrieval_complete: true` means the declared candidate-generation policy
finished, not that semantic recall is perfect. The envelope also returns
`total`, `returned`, `truncated`, `truncated_by`, `selection`, quality counts,
warnings, and records. With `--timeline`, it adds `order: newest-first`. Pipe
agent-facing JSON through `jq` so only decision-relevant fields enter context,
but retain `warnings` and per-record `diagnostics`.

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
useful. Hybrid or lexical rank selects candidates; it does not determine
importance or truth.

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

Before declaring supersession, require `retrieval_complete: true`, inspect each
consequential candidate with `--show`, and check the claim cluster with at least
one wording variant or its owning topic when a later paraphrase could have been
missed. Do not use `matched == returned`, a dense score, or a fixed similarity
threshold as semantic coverage proof. Widen the presentation window when top
candidates are ambiguous or variants change the result. If those gates do not
close, state that the answer is based on an incomplete window or abstain.

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
