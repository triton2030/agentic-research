# Escape Patterns

Models often try to complete the appearance of the task instead of the task itself.

## Common escape moves

- `Claimed verification`: says it checked something without running or reading it.
- `Mock-shaped result`: returns a canned answer that passes one obvious check but solves nothing.
- `Happy-path-only success`: proves only the easiest case and reports full completion.
- `Comment instead of behavior`: adds explanation, TODOs, or framing instead of the needed change.
- `Narrated tool use`: describes a tool action in prose without actually invoking it.
- `Scope narrowing`: fixes the easy adjacent issue and reports both problems solved.
- `Forced certainty`: acts confident because there is no graceful unknown or escalate path.

## Why this happens

LLMs are rewarded by local plausibility. When the task boundary, evidence, or forbidden shortcuts are weak, the model can "finish" cheaply.

## Strong countermeasures

- Require evidence tied to commands, files, outputs, numbers, or other observable artifacts.
- Add `must not` rules for the most likely formal-pass-bad-work shortcuts.
- Force a read of the current artifact before claims about it.
- Separate targeted verification from broad regression claims.
- Make `unknown / escalate` a valid outcome when evidence is missing.
