# Relay Truncation Recovery

## Observation

Managed external runs can complete successfully while the bridge relay truncates
the final answer. Treating `chat_relay.text` as the only source loses useful
findings even though `stdout.log` still contains the complete streamed output.

## Counter

- 2026-05-20 [GPT-5.5]: during a Claude read-only review of
  `experiments/md-embedding-server`, the bridge report had
  `chat_relay.truncated=true` and stopped mid-finding. Reconstructing text from
  `stdout.log` stream deltas recovered the full answer without rerunning Claude.

## Possible upgrade

When relay output is truncated, recover from durable run logs before rerunning
or summarizing partial findings; report that the final answer came from log
recovery.
