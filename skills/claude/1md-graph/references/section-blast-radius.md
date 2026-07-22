---
description: "Claim and consumer probes for hidden semantic downstream outside declared graph edges."
---

# Section Blast Radius

Open for a concrete heading/claim when material downstream may exist outside
the declared graph, especially across vocabularies or layers. Whole-file
semantic discovery belongs to `1md-navigator`; destructive file impact belongs
to the parent skill.

Before running the composite, read
[`runtime-gates.md`](runtime-gates.md): the live command is cost-bearing and may
write/heal index cache. If those side effects are outside authorization, close
the hard layer with `preflight` and hand semantic retrieval to
`1md-navigator`.

## Two Probes

Start from the change predicate, not the file topic:

```bash
md section-blast-radius PATH CORPUS --query "QUERY" --scan GRAPH_ROOT --limit 8 --json
```

1. **Claim probe** — a precise paraphrase of what becomes different.
2. **Consumer probe** — a decision, promise, interface behavior or constraint
   that becomes wrong if the claim changes. Use likely consumer vocabulary,
   not the source wording.

A topic-only query that returns the source and nearest thematic neighbors is an
echo, not downstream recall.

## Noise And Scope

- Run two bounded probes without automatic second hop.
- If results remain source echoes, rewrite the consumer probe once; a second
  failure stops the semantic route as `low-recall / low-signal`.
- No candidate means no candidate in that probe, not graph completeness.
- Name graph scope (`preflight`/scan policy) and semantic scope (corpus and
  filters) separately; command semantic filters do not narrow graph scan.

## Candidate Judgment

Graph results remain obligations from the parent workflow. Semantic results are
candidates only. Read a body when its snippet suggests that it either:

- repeats or constrains the changed predicate; or
- makes a decision that depends on the predicate being true.

After reading, apply the X/Y admission test from
[`semantic-edge-audit.md`](semantic-edge-audit.md). Similarity and folder
distance prove nothing alone.

Classify selected candidates only: `update-in-scope`, `check-only`, `add-link`,
`promote-to-depends-on`, `deferred`. Unselected output remains unreviewed; do
not imply full semantic coverage.

## Stop

Stop when both scopes and both probes are recorded (or the noise gate ended the
route), graph obligations are resolved, selected bodies have X/Y judgments,
and missing edges or shape questions have the correct owner handoff.
