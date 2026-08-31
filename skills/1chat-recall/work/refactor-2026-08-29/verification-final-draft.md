# Final-draft verification — 2026-08-29

Target: uninstalled Codex runtime candidate, теперь по адресу
`skills/1chat-recall/versions/draft-2026-08-29/codex/`.

## Static evidence

- System `quick_validate.py`: `Skill is valid!`.
- `description`: 181 characters and begins with `Use when`.
- Codex `agents/openai.yaml`: valid YAML and English UI text.
- Every body route points to an existing reference.
- The earlier paragraph-level 9 + reference count is withdrawn. Independent R4
  literal audit found 16 loaded / 11 applicable body units and maximum coherent
  active paths of Capture 48, Retrieval 47, Recovery 59, Restoration 28, Repair
  68, and Structural validation 21. This is an unresolved installation blocker,
  not a table-only defect.
- `plugin-eval analyze`: 100/100, 0 failures, 0 warnings, trigger 47 tokens,
  invoked body 355 tokens, deferred files 3352 tokens. This is static evidence,
  not behavioral acceptance.
- Existing unchanged helpers: 101 tests plus 12 subtests passed before drafting;
  no script or test file changed.
- Code inspection confirms `context-note` is indexed by both FTS5/BM25
  (`chat_digest.py:402-427`) and dense retrieval (`:801-808`); the existing
  test `test_context_note_is_searchable_but_shown_only_on_show` proves a term
  found only there retrieves its record.

## Clean trajectory A — Capture then Retrieval

In an isolated corpus, a new correction changed local dates to explicit UTC and
the owner asked whether it cancelled earlier speech. The clean executor opened
body → Capture → body → Retrieval, wrote one source-bound record with
`supersedes`, opened both records, ran facets and `--since`, and returned the
new position. It never held two references simultaneously. The probe could not
test its requested background agent because all collaboration slots were full,
and the fixture prompt prevented a real live-owner check.

## Clean trajectory B — Retrieval with live owner

In a fresh corpus, an older local-time quote and a later UTC correction coexisted
with `AGENTS.md` requiring explicit UTC. The executor skipped Capture, opened
Retrieval, launched exactly one nonblocking independent agent, resolved
chronology, checked `--since` and the live owner, and returned UTC with the
remaining `Z` versus `+00:00` gap. Recovery correctly did not trigger.

## Clean trajectory C — terminal Recovery

In a third corpus, two incompatible quotes had the same exact timestamp and no
live owner or supersession. The executor opened body → Retrieval, closed it with
a complete `recovery-needed` receipt, then opened Recovery only. Recovery made
one lexical retry, inspected timeline and both literal records, checked later
and live-owner absence, incorporated one independent agent's matching verdict,
and terminated `abstain`. No two references were active together.

The Recovery probe created a fresh `.uv-cache` and reported dependency download
output. No web/browser tool sent corpus records anywhere, but the probe does not
prove a completely network-free first bootstrap; the Product Frame already
permits one-time model/cache bootstrap.

## Clean trajectory D — topic selection and keyword context

After the owner's new correction, a fresh executor received a pronoun-bearing
quote about the local `1chat-recall` corpus. It opened body → Capture, read
`topics.md` in full before writing, compared `chat-recall-corpus` with
`chat-recall-retrieval` and `skill-instruction-authoring`, then chose the corpus
boundary. It wrote the literal quote with:

`context-note: локальный корпус 1chat-recall; формат записей корпуса; chat recall corpus`

The note restores the pronoun referent and adds stable search vocabulary without
restating the owner's rule. Receipt:
`2026-08-29-161819-codex-01a04d3c.md#L15` in the isolated fixture; no new topic
was created and no live package changed.

## Clean trajectory E — opaque selection through the router

After the owner selected the second of two offered topology options with
`да, второй вариант`, a clean executor opened body → Capture, treated the
statement as `selection` rather than empty assent, read the final `topics.md` in
full, and selected `skill-instruction-authoring`. It wrote:

`context-note: option B; Capture and Retrieval references; short router; 1chat-recall refactor`

Only after the Capture receipt did it open Retrieval. It read the literal
record, ran the inclusive later check, found no live owner in the fixture,
returned the selected reference topology, and continued the original refactor.
Receipt: `2026-08-29-164617-codex-44444444.md#L15` in
`/tmp/chat-recall-r4.2OpeKm`; the main repository and live packages were not
changed by the executor.

## Remaining blocker

The owner selected the independent reference topology at
`_ops/chat-recall/2026-08-29-150002-codex-01a04cf3.md:21` and later required the
invariant rather than eternalizing the former hot-body implementation at
`_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:15`. Clean trajectories A,
B, and E observe ordinary Capture/Retrieval through the router, so topology is
no longer an owner-choice. The unresolved blocker is the conservative atomic
instruction budget above; the exact draft must not be installed while it is
present.
