# Claude Ask Failure Handling

Classify the failed layer before recovery:

- tool absent or stale in the current Codex task;
- external-data approval cancelled before dispatch;
- invalid cwd/session or macOS-protected path;
- subscription auth or Agent SDK rejection;
- unsupported profile or non-Opus native model evidence;
- Claude timeout, cancellation or SDK execution failure;
- transient lease missing/busy, interrupt not settling, or session capacity;
- recoverable maximum-turn result carrying a native `session_id`;
- malformed or truncated terminal result.

## Recovery

1. For stale/absent schema, retry from a fresh Codex task. Do not use legacy
   tools or a raw Claude subprocess.
2. For declined external-data approval, state what was not sent. Retry only when
   the user explicitly reopens that scope; do not invent another policy layer.
3. For auth/SDK failure, preserve the subscription-only route. For
   unsupported profile/model evidence, preserve the Opus-only route. Do not
   inject a key/token/base URL, enable a cloud provider, retry Fable or change
   model aliases.
4. For path or session failure, report the exact invalid input or OS denial;
   correct it or start a fresh session without changing authority.
   For a native tool permission denial, use the compact tool-name warning and
   ask Claude for a permitted alternative or stop; do not auto-approve it.
5. For timeout, cancellation or SDK failure, report the compact typed error. Do
   not auto-retry a token-consuming or session-appending turn.
6. For a missing process-local lease, use `open_resume` only when the native
   `session_id`, cwd and next prompt are known. For busy/capacity, observe or
   stop the exact lease; do not create a second identity.
7. For `max_turns`, preserve its resumable UUID and metadata. Continue only when
   another turn is justified; do not hide it by raising the limit.
8. For malformed or truncated output, do not claim that Claude review finished.

Stop when the same boundary remains after its exact recovery. Report the failed
layer, evidence and one next user/system action. Do not replace the missing
Claude opinion with Codex and label it as Claude.
