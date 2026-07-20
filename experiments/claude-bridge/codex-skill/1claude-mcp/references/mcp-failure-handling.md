# Claude Ask Failure Handling

Classify the failed layer before recovery:

- tool absent or stale in the current Codex task;
- external-data approval cancelled before dispatch;
- invalid cwd/session or macOS-protected path;
- subscription auth or Agent SDK rejection;
- Claude timeout, cancellation or SDK execution failure;
- missing or truncated terminal result.

## Recovery

1. For stale/absent schema, retry from a fresh Codex task. Do not use legacy
   tools or a raw Claude subprocess.
2. For external-data approval, state that the exact named local material will be
   sent to Anthropic's service and request confirmation. Retry only after the
   user approves. No result means no completed Claude review.
3. For auth/SDK failure, preserve the subscription-only route. Do not
   inject a key/token/base URL, enable a cloud provider or change model aliases.
4. For path failure, keep broad-read intent but report the exact OS denial;
   macOS-protected locations require owner-granted OS access.
5. For timeout/cancellation/SDK execution failure, report the compact typed
   error and verify no live Claude process tail before another attempt.

Stop when the same boundary remains after its exact recovery. Report requested
role, failed layer, evidence, whether a live process remains and the one next
user/system action. Do not replace the missing Claude opinion with Codex and
label it as Claude.
