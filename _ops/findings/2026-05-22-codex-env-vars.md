# Codex Env Vars For md-tools Cost Ledger

Context: task-102 checks the cost ledger session id chain for the current Codex
Desktop runtime.

Observed `CODEX*` variables:

- `CODEX_CI=1`
- `CODEX_INTERNAL_ORIGINATOR_OVERRIDE=Codex Desktop`
- `CODEX_SHELL=1`
- `CODEX_THREAD_ID=019e4ebf-c706-7393-ad06-e481e8b2d52d`

Finding: `CODEX_SESSION_ID` is not present in this runtime. The ledger keeps it
in the resolution chain as a defensive future hook, but effective Codex
attribution currently falls through to `MD_CLI_SESSION_ID` if set, otherwise the
generated `~/.cache/md-tools/session-id` fallback.

