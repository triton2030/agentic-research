# Validating the corpus

1. Name the project corpus to check; this mode diagnoses structure and never
   claims that an owner position is applicable.
2. Run the local strict validator without mutating records:

   ```bash
   ROOT="${CODEX_HOME:-$HOME/.codex}/skills/1chat-recall"

   python3 "$ROOT/scripts/chat_digest.py" \
     "$PWD/_ops/chat-recall" --check --strict
   ```

3. Report the checked corpus, exit status, diagnostics, and exact damaged
   addresses. A nonzero exit is a structure receipt, not a command failure; any
   mutation requires a separate Repair mode.
