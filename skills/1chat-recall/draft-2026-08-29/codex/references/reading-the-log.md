# Recovering recall coverage

## Protocol

1. Start only from Retrieval's `recovery-needed` handoff; retain its claim,
   scope, date, diagnostics, read addresses, and gaps as this mode's input.
2. Read `matched`, `returned`, `truncated`, `truncated_by`, `retrieval`, and the
   unique holder files; these describe a candidate set, not claim breadth.
3. Rephrase the same claim once as a short natural subject rather than an
   artifact name.
4. Make at most one lexical retry with three or four distinguishing roots. Put
   Russian roots separately with `*` after the stable stem; keep exact names
   intact.
5. Split a broad subject into material facets using snippets and
   `session-context`, with one facet in the current task's language. After two
   facets add no holder, stop with a gap only if no named next facet could still
   change the claim.
6. When hybrid is unavailable, use `--lexical`; use `--timeline` for records of
   selected holders, remembering that its `--limit` cuts records rather than
   holders. Raise `--limit` only when truncation makes that useful.
7. If the local model is not prepared, run `--prepare` as its own command before
   retrying retrieval; add no query variant that cannot change the candidate
   set:

   ```bash
   ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"

   uv run --locked --script "$ROOT/scripts/chat_digest.py" --prepare
   uv run --locked --script "$ROOT/scripts/chat_digest.py" \
     _ops/chat-recall --query "<claim or roots>" --lexical --json
   ```

8. Open every selected literal record needed for the decision, including its
   `superseded_by` or `contested_by` address; rankings, cards, and snippets only
   route reading.
9. Resolve later speech inside needed holders, repeat the claim with
   `--since <evidence date>`, and compare applicable live project owners. Live
   owner evidence wins, but expose both addresses rather than resolving a
   conflict silently.
10. Finish this mode with an applicable position or `abstain` · scope · date ·
    all read addresses · normal and recovery routes · later/live-owner checks ·
    unresolved gaps. Empty recovery is evidence of only the attempted routes,
    never proof that no owner position exists.
