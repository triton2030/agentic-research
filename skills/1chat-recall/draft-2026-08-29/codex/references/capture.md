# Capture

## Protocol

1. Capture in the same turn when the statement changes a future decision,
   boundary, criterion, preference, or understanding outside neighboring
   messages; when usefulness is genuinely uncertain, preserve it before later
   work can depend on it.
2. Skip only assent that neither chooses an option nor changes durable meaning.
   When assent selects an offered option, preserve it as `selection` and make
   the selected referent recoverable in metadata without widening the choice.
3. Read the current session holder. Do not duplicate the same thesis; repeat
   capture only to supply the complete current `session-context`, which may
   return `context-updated` without rewriting the record.
4. Before writing any `quote` or `selection`, complete topic selection in this
   order: read `_ops/chat-recall/topics.md` in full; name the record's durable
   subject; compare it with every existing boundary by meaning rather than word
   overlap; reuse the nearest fitting topic. Only when none fits, create one
   short Latin topic name and one-line boundary with `--new-topic`. Poor topic
   metadata can make the record effectively unrecoverable, so inventory output
   never substitutes for reading the map.

   ```bash
   python3 "${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall/scripts/chat_capture.py" \
     --list-metadata --project "$PWD"
   ```

5. Preserve literal owner wording as the default `quote`; use `selection` only
   for an option the owner actually selected, and never turn an agent paraphrase
   into owner speech.
6. For each `quote` or `selection`, write a short `context-note` as keyword-like
   noun phrases: missing named referents, the selected option when its wording
   is opaque, stable artifact names, and useful search synonyms. Do not write
   prose, repeat/paraphrase the thesis, assert current truth, or widen its scope.
   If no non-repeating search keys can be named, return to source context instead
   of inventing them.
7. For each `quote` or `selection`, write one complete `session-context` line
   that retains earlier major tasks/artifacts/operations/names and adds the new
   subject with useful synonyms; it helps search but never states decisions or
   current truth.
8. Use current timezone-aware time only for this-turn speech; use the native
   transcript timestamp for older speech.
9. A directly incompatible earlier position in the same scope gets its fresh
   address through `--supersedes`; an unresolved winner uses `--contested`;
   compatible detail uses neither.
10. Perform one write through the helper, adding `--kind selection` only for a
    selected option and adding other optional flags only when applicable:

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
