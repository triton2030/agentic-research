# Recovering recall coverage

## Protocol

1. Read `matched`, `returned`, `truncated`, `truncated_by`, `retrieval`, and the
   unique holder files; these describe a candidate set, not claim breadth.
2. Rephrase the same claim once as a short natural subject rather than an
   artifact name.
3. Make at most one lexical retry with three or four distinguishing roots. Put
   Russian roots separately with `*` after the stable stem; keep exact names
   intact.
4. Split a broad subject into material facets using snippets and
   `session-context`, with one facet in the current task's language. After two
   facets add no holder, stop with a gap only if no named next facet could still
   change the claim.
5. When hybrid is unavailable, use `--lexical`; use `--timeline` for records of
   selected holders, remembering that its `--limit` cuts records rather than
   holders. Raise `--limit` only when truncation makes that useful.
6. If the local model is not prepared, run `--prepare` as its own command before
   retrying retrieval:

   ```bash
   ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"

   uv run --locked --script "$ROOT/scripts/chat_digest.py" --prepare
   uv run --locked --script "$ROOT/scripts/chat_digest.py" \
     _ops/chat-recall --query "<claim or roots>" --lexical --json
   ```

7. Do not add query variants that cannot change the candidate set; empty
   recovery means only that the named routes found nothing.
8. Report routes, unique holders, facets, truncation status, read record
   addresses, and unresolved gaps; return to the body router, then finish
   Retrieval with this packet as input until it yields a position or `abstain`.
