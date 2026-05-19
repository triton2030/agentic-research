# MCP Client Timeout Vs Managed Run

## Observation

MCP client timeout can fail the waiting request while the managed external run
continues and completes correctly in tmux/log state. Treating the client error
as model failure loses the answer and may cause unnecessary reruns.

## Counter

- 2026-05-20 [GPT-5.5]: during Gemini review of the tmux refactor, the local
  MCP client hit its 60s request timeout while `gemini_run` continued in tmux
  and completed successfully. Recovery through `resultRun(run_id)` returned the
  full answer and confirmed the saved tmux session was gone.

## Possible Upgrade

When a wait call times out, immediately check saved run state/result and tmux
session before retrying or declaring failure. Report the timeout layer
separately from model/run status.
