---
name: 1md-search
description: >
  Use when needed Markdown evidence has no known address and must be found by
  meaning; ranked hits can misstate owner truth or absence. Also use for
  similarity, near-copy, recurring-topic, or corpus-topology candidates;
  resolve selected bodies and coverage honestly.
---

# 1md-search

## Product Job

When downstream work knows the claim it needs but not its Markdown address,
turn semantic uncertainty into **minimal decision-ready context**: read
addressable bodies, actual coverage, and the authority gap sufficient for the
next agent or domain owner to decide or act without guessing.

Search output is not a product by itself. Unless the user requested a search
report, inventory, or audit, keep retrieval state internal and continue the
original task; do not make the user consume tool rows or an intermediate packet.

The natural default obstructs this job: a semantic result already carries a
path, heading, snippet, and numeric score, so it looks like a finished answer.
The model can easily treat the first coherent candidate as truth, then derive
owner, duplicate meaning, or absence from its own early choice.

The skill therefore inserts the missing fork between search and downstream
work:

```text
one semantic aspect
→ actual corpus and retrieval contract
→ ranked addressable candidates
→ selected, read bodies
→ read authority mapping | owner: unresolved
→ decision or action by the calling domain owner
```

Semantic rank answers only **"what should I read next?"** The local measure of
success is decisive read context per unit of retrieval cost and prompt budget:
the smallest set of `path#heading` bodies capable of changing the next action,
with the remainder named honestly. A high score, polished snippet, or file count
does not measure that value.

## Retrieval Contract

Before the first semantic command, establish compact working state:

- the downstream consumer, its next action, and one independently retrievable
  aspect or claim that a body must support, refute, or refine;
- the likely language of the source block; for a genuinely mixed-language
  corpus, use a separate short query in each represented language;
- the explicit corpus root, effective includes and excludes, and expected
  evidence unit;
- what counts as sufficient body evidence and which gap blocks an honest
  downstream verdict.

Split a compound question into a query pack. A single query that searches for
multiple claims creates a smooth averaged rank and hides which aspect was lost.

For an external corpus, first read its `AGENTS.md` and `.md-tools.toml`: scope
belongs to the target corpus, not the current `cwd`.

### No Declared Boundary Yet

An absent `.md-tools.toml` is not a default of "everything is truth". With no
declared scope the index takes the whole tree, so drafts, projections, archives
and generated views rank beside authored truth, and every one of those files is
what leaves the machine for the embedding provider. The commands will not warn
you: an undeclared corpus dry-runs and indexes exactly like a declared one.

Authoring that boundary is retrieval work, and it is derived from this project,
never copied from a template:

1. **Read what the project says about itself first.** Its `AGENTS.md`, README,
   goal or index files usually name which documents carry authority and which
   are views. Folder names are a hypothesis about that, never the finding.
2. **Classify by function, not by label.** Three kinds behave differently under
   retrieval: authored truth; derived views of that truth (projections,
   translations, decks, generated exports); and working process (plans,
   scratch, archives, session logs). Only the first kind should be retrievable
   as an answer.
3. **Test each candidate against a real claim.** Ask: if a section from here
   came back as the answer to a question about this product, would that be
   right or wrong? A directory you cannot judge that way is not classified yet,
   so do not place it.
4. **Fail narrow.** Unclassified stays out. A missing document produces a
   visible no-hit that the next probe can fix; an admitted projection produces
   a confident wrong answer that nothing downstream catches, and it has already
   been sent to the provider.
5. **Prove the boundary before writing it.** Run the intended scope as command
   filters — `md search-read CORPUS --query "..." --path-include "..." --json` —
   and read the actually returned paths. The config is the durable form of a
   filter you already saw behave correctly.
6. **Write, then verify the scope really narrowed** with `md status CORPUS
   --json` and its reported `path_scope`.

This file is the owner's data boundary, not a tuning knob: propose it, name what
you excluded and why, and never widen it silently in a later task. When the
project never declares what carries authority, that gap belongs to the owner or
to `1ia-audit`; do not invent it from folder names.

### Authorization Gate at the Point of Action

Before `search`, `search-read`, or another cost-bearing semantic command, verify
that effective project instructions or explicit current user approval permit:

1. sending in-scope Markdown and an uncached query to the configured provider;
2. modifying the generated index or cache.

A request to "find it by meaning" does not create that authorization. Without
coverage, use a permitted filesystem or exact probe, or ask for approval for a
precise corpus and side effect. Semantic commands do not modify source Markdown.

## Controller: A Candidate Does Not Cross the Gate on Its Own

### 1. Get a Map, Not an Answer

The ordinary route is normal `search-read`: it returns section handles and
snippets, not evidence bodies.

```bash
md search-read CORPUS --query "ONE ASPECT" --limit 5 --json
```

Immediately inspect the actual returned paths, effective filters and
exclusions, `_envelope.corpus_state`, and `_envelope.next_step`. Config includes
and command includes can combine with OR; a narrow `--path-include` alone does
not prove a narrow effective scope.

### 2. Expand Only Strong Bodies

After narrowing by query, limit, and filters, open selected sections through
`search-read --expanded` with an explicit token budget or direct Read of
concrete handles. Do not use `--expanded` as a broad first call.

```bash
md search-read CORPUS --query "ONE ASPECT" --limit 3 \
  --expanded --token-budget 3000 --json
```

A candidate crosses the evidence gate only when the read body contains the
claim needed by the next decision. Headings, descriptions, snippets, incoming
links, specificity, and scores remain routing signals. If removing the body
would not change the next conclusion, reading it was ceremony rather than
evidence.

### 3. Separate Authority from Meaning

A thematically relevant read body does not thereby become an owner. Before
returning the packet, read the live owner map or contract and state the mapping:
why it assigns authority for this claim. If that evidence is unavailable,
return exactly:

```text
owner: unresolved
```

Do not infer owner, canon, readiness, `supported/conflict`, or pass/fail from
rank, description, link direction, or apparent quality. Those verdicts belong
to the calling domain owner.

## Practical Route Choice

This is a stable job-level map, not a copy of the full CLI catalog. Before using
a rare flag or threshold, or parsing a schema-dependent result, read
`md tools COMMAND --json`.

| Retrieval job | Route |
| --- | --- |
| Unknown meaning, then bodies are needed | `md search-read` — ordinary default |
| Only ranked handles or snippets are needed | `md search` |
| A target is known; external similar blocks are needed | `md semantic-neighbors` |
| Sections of an explicit semantic type are needed | `md query-by-type`; only with ready profiles |
| Pair, topic, or topology candidates are explicitly needed | `md overlaps`, `md repeated-concepts`, or `md cluster` |
| Indexed roots are unknown | `md corpus-scan` |

`semantic-neighbors`, `overlaps`, `repeated-concepts`, and `cluster` operate on
retrieval-enriched representations: descriptions, titles, heading chains, and
sometimes sibling context can pull different claims together, while different
framing can push equivalent claims apart. Therefore these commands **never
prove semantic duplicate meaning or its absence**. They only generate
candidates whose bodies must be read.

Reranking likewise cannot recover an aspect lost during retrieval. Enable it
only when top candidates already contain the required aspect but their order
could materially change what gets read.

Confirm numbers, statuses, closed vocabularies, and exact counts from owner
bodies and exact evidence, not semantic scores.

## No-Hit and Index Recovery

Empty or noisy output does not prove absence. Before drawing such a conclusion,
check:

- index and corpus state, plus the actual returned scope;
- language and query framing;
- threshold, eligibility, and output or token budget;
- the strongest plausibly missing candidate with one alternative short query.

A cold, partial, busy, or warmup-required state is a retrieval state, not a
no-hit. `NO_INDEX`, `NEEDS_WARMUP`, and `index_warmup_required` never license
the conclusion that a corpus lacks the claim. Where authorization covers
ordinary warmup, run the recovery here rather than inventing one:

```bash
md status CORPUS --json                 # only after edits or an index question
md index CORPUS --dry-run --json
md index CORPUS --confirm --transaction-id TRANSACTION_ID --json
md status CORPUS --json
# then replay the original query with the same filters
```

Confirm carries the `transaction_id` or `fingerprint` from **that same**
dry-run; with zero pending and cleanup counts no confirm is needed. When
`_envelope.next_step.args` proposes a parent corpus or filters, use them as-is
instead of composing your own. `NEEDS_REBUILD` means a schema, model, or
integrity mismatch and still goes through this normal index transaction.

Everything past ordinary warmup — `cleanup-shadowed`, vacuum, manual deletion of
SQLite/WAL/SHM, forced rebuild — needs its own separate grounding first.
[`references/index-lifecycle.md`](references/index-lifecycle.md) holds the full
state table, delta/cleanup rules, and the transaction contract; open it when a
state does not match this sequence.

`profile-sections` and corpus-scope expansion are likewise outside ordinary
warmup. Serialize semantic queries against one corpus; independent roots can run
in parallel.

After a second material no-hit and one query variant, stop the semantic loop. If
absence is material, add a filesystem map and exact search through the proper
owner; still phrase the conclusion as coverage of specific probes rather than
corpus-wide proof of absence.

Rare runtime and setup diagnostics belong to
[`references/setup.md`](references/setup.md); ranking and language behavior
belong to [`references/retrieval-engine.md`](references/retrieval-engine.md).

## Contrastive Scenes

> **Default → transition.** A query returns `Decisions#Authority` as top-1. Its
> heading and score make it look like the natural owner. The controller first
> reads the body, finds a historical projection, then reads the live owner map.
> The result changes from "owner found" to an exact mapping or `owner:
> unresolved`.

> **Anti-example.** The agent lists a query, filters, five handles, and an
> `evidence packet`, but derives its conclusion only from snippets. The fields
> are filled, but the gate is still open: no candidate has become body evidence.

> **Transfer — duplicate search.** `overlaps` returns a pair with high
> similarity. A shared template and heading chain may have produced that score
> even though the bodies make different claims. Read both sides and hand them
> to the owner of the duplicate verdict. A low score or empty pairs likewise do
> not prove that a semantic duplicate is absent.

## Feedback and Reopen

If output stops at tool rows while the original task remains open, or any
material conclusion still rests on a snippet or rank, shaping failed. Return to
the last uncrossed gate instead of expanding search by inertia.

This design hypothesis is dated to `GPT-5.6`, 2026-08-04. A target-model change,
or matched cases where the bare rule "read the body" produces the same
downstream result, reopens the mechanism for simplification.

## Delivery and Stop

Maintain bounded working state:

```text
downstream claim/action ← read addresses ← authority mapping + gaps
```

When a search report, inventory, audit, or handoff is itself the requested
product, return a compact search evidence packet:

- aspect or query and source language;
- corpus root, actual filters and exclusions, index state, and side effects;
- ranked `path#heading` candidates and addresses of bodies actually read;
- `authority: <read owner contract + mapping>` or `owner: unresolved`;
- the `candidate → body evidence` boundary, material coverage gaps, and the
  owner of the next verdict.

In every other task, use the packet as an internal controller, continue the
original work, and show the user only the changed conclusion, addresses of
material evidence, and material gaps. Do not publish retrieval theater.

Stop when material aspects have read, addressable bodies; effective scope and
gaps are named; and the strongest plausibly missing candidate has been checked
in proportion to the cost of error. Do not pursue corpus-wide completeness
without a concrete claim it could change.
