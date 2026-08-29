# Final-draft verification — 2026-08-29

Target: uninstalled Codex runtime candidate in `draft-2026-08-29/codex/`.

## Static evidence

- System `quick_validate.py`: `Skill is valid!`.
- `description`: 174 characters and begins with `Use when`.
- Codex `agents/openai.yaml`: valid YAML and English UI text.
- Every body route points to an existing reference.
- Operational mode counts: body 9; Capture 20 total, Retrieval 20, Recovery
  19, Restoration 16, Repair 20, Structural validation 12.
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

## Remaining owner decision

The clean traces show that the reference router works in these cases. They do
not themselves cancel the older explicit decision to keep ordinary Capture and
Retrieval in the guaranteed-read body. Installation therefore still requires
the owner's approval of this exact reference topology and exact English draft.
