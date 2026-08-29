# Capture

## Protocol

1. Complete Capture in the same turn, before any later work that may depend on
   the statement.
2. Decide whether the statement still changes a future decision, boundary,
   criterion, preference, or understanding outside its neighboring messages.
   Skip assent; when usefulness is genuinely uncertain, preserve the statement.
3. Read the current session holder. Do not duplicate the same thesis; repeat
   capture only to supply the complete current `session-context`, which may
   return `context-updated` without rewriting the record.
4. Before writing any `quote`, complete topic selection in this order: read
   `_ops/chat-recall/topics.md` in full; name the quote's durable subject; compare
   it with every existing boundary by meaning rather than word overlap; reuse
   the nearest fitting topic. Only when none fits, create one short Latin topic
   name and one-line boundary with `--new-topic`. Poor topic metadata can make
   the quote effectively unrecoverable, so inventory output never substitutes
   for reading the map.

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall/scripts/chat_capture.py" \
     --list-metadata --project "$PWD"
   ```

5. Preserve owner speech as deletion-only `quote`; an owner-selected ready-made
   option is `selection`, agent explanation is `note`, and malformed evidence
   remains read-side `raw`. Never turn an agent paraphrase into owner speech.
6. For each `quote`, write a short `context-note` as keyword-like noun phrases:
   missing named referents, stable artifact names, and useful search synonyms.
   Do not write prose, repeat/paraphrase the thesis, assert current truth, or
   widen its scope. If no non-repeating search keys can be named, return to
   source context instead of inventing them.
7. For each `quote` or `selection`, write one complete `session-context` line
   that retains earlier major tasks/artifacts/operations/names and adds the new
   subject with useful synonyms; it helps search but never states decisions or
   current truth.
8. Keep the record project-local unless the owner explicitly gives
   cross-project scope. Use project language for ordinary concepts, preserve
   exact names, and pair a stable foreign term with a useful local synonym.
9. Use current timezone-aware time only for this-turn speech; use the native
   transcript timestamp for older speech. A directly incompatible earlier
   position in the same scope gets its fresh address through `--supersedes`;
   an unresolved winner uses `--contested`; compatible detail uses neither.
10. Perform one write through the helper, adding only applicable optional flags:

    ```bash
    ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"
    SESSION="${CODEX_THREAD_ID:-${CODEX_SESSION_ID:-}}"

    python3 "$ROOT/scripts/chat_capture.py" \
      --quote "<literal owner words>" \
      --context-note "<short keyword-like referents, artifact names, synonyms>" \
      --session-context "<tasks; artifacts; operations; names and synonyms>" \
      --source-timestamp "$(date -Iseconds)" \
      --type <speech-act> --topic <topic> \
      --agent codex --project "$PWD" --session "$SESSION" --json
    ```

11. Verify the JSON receipt and open the returned address. Report that address;
    for a new topic also report its map line, for cancellation the prior
    address, for self-correction `context-updated`, and for a skipped statement
    the usefulness-gate reason.
