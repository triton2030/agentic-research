# Claude Ask Failure Handling

Classify the failed layer before recovery:

- tool absent or stale in the current Codex task;
- external-data approval cancelled before dispatch;
- invalid cwd/session or macOS-protected path;
- subscription auth or Agent SDK rejection;
- Claude timeout, cancellation or SDK execution failure;
- malformed or truncated terminal result.

## Recovery

1. For stale/absent schema, retry from a fresh Codex task. Do not use legacy
   tools or a raw Claude subprocess.
2. For declined external-data approval, state what was not sent. Retry only when
   the user explicitly reopens that scope; do not invent another policy layer.
3. For auth/SDK failure, preserve the subscription-only route. Do not
   inject a key/token/base URL, enable a cloud provider or change model aliases.
4. For path or session failure, report the exact invalid input or OS denial;
   correct it or start a fresh session without changing authority.
5. For timeout, cancellation or SDK failure, report the compact typed error. Do
   not auto-retry a token-consuming or session-appending turn.
6. For malformed or truncated output, do not claim that Claude review finished.

Stop when the same boundary remains after its exact recovery. Report the failed
layer, evidence and one next user/system action. Do not replace the missing
Claude opinion with Codex and label it as Claude.
