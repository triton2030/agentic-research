# Retrieval

## Protocol

1. State the claim subject as a short natural phrase about the decision, not the
   artifact name, and query the local corpus yourself.
2. For an important topic that may have prior discussion, send exactly one
   background subagent for an independent verdict and new addresses. Do not wait
   or stop your own search; use its result at the next related decision. Handle
   a simple lookup or working clarification locally.
3. Run the normal route:

   ```bash
   uv run --locked --script "${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall/scripts/chat_digest.py" \
     _ops/chat-recall --query "<short natural claim subject>" --json
   ```

4. Treat `semantic_rank`, counts, `session-context`, and snippets only as reading
   routes; literal records are evidence. Open a holder when applicability needs
   scene or chronology, and always open `superseded_by` or `contested_by`
   addresses before use. Do not rerank by file length or quote count.
5. Cover material facets using vocabulary from cards and snippets, including
   one query in the current task's language. Two consecutive facets with no new
   holder permit stopping with a gap; continue when a named next facet could
   still change the claim.
6. Interpret `query_domain` only as dense top-1 proximity: the key is absent in
   lexical and empty output, and `off-domain` proves neither that no position was
   recorded nor that the query lies outside the corpus subject.
7. Treat `truncated=true` as invisible candidates. Continue with a named gap
   only when they cannot change the claim; otherwise end this mode
   `recovery-needed`. Empty, excessively broad, conflicting, or unavailable
   hybrid routes also end `recovery-needed`, never as a final candidate list.
8. Resolve later speech inside each needed holder; a later record or speech-act
   change may reverse an earlier one, while a self-contained quote remains the
   short route.
9. Repeat the same claim with `--since <YYYY-MM-DD>` from the evidence date and
   compare timezone-aware timestamps because the date filter is inclusive.
   Read every materially newer result needed to settle chronology.
10. Check every applicable live project owner (`AGENTS.md`, `GOAL.md`, config,
    active `SKILL.md`, Product Frame, or plan). Live owner evidence wins, but
    expose both addresses; a missing carrier or neighboring task neither proves
    cancellation nor supplies current status.
11. If no recovery is needed, report: applicable position or `abstain` · scope ·
    date · read record/holder addresses · query routes · later/live-owner checks
    · remaining gaps. Quote dumps and unread selected addresses are not results.
