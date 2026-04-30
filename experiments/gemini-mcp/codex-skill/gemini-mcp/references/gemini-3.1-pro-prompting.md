# Gemini 3.1 Pro Prompting

Use this reference when composing `prompt`, `systemInstruction`, or Gemini MCP
call parameters for `gemini-3.1-pro-preview`.

Sources:

- https://ai.google.dev/gemini-api/docs/models
- https://ai.google.dev/gemini-api/docs/gemini-3
- https://ai.google.dev/gemini-api/docs/thinking
- https://ai.google.dev/gemini-api/docs/prompting-strategies

## Defaults

- Use `model: "gemini-3.1-pro-preview"` unless the user explicitly asks for a
  cheaper or faster Gemini model.
- Use `thinkingConfig.thinkingLevel: "high"` for the strongest reasoning path.
- Leave `temperature` unset by default for Gemini 3; Google recommends the
  default `1.0` and warns that low values can harm complex reasoning.
- Prefer structured output or tool parameters for machine-readable results
  instead of relying only on prose format instructions.

## Prompt Shape

Use a direct, structured prompt:

```xml
<role>What Gemini is responsible for.</role>
<task>The exact outcome to produce.</task>
<context>Only facts that change the answer.</context>
<constraints>Allowed moves, must-not rules, tools, and boundaries.</constraints>
<output>Required answer shape and stop condition.</output>
```

Markdown headings are also fine; keep one delimiter style inside one prompt.

## Rules

- Be precise and direct. Avoid persuasive filler and vague goals.
- Define ambiguous terms, success criteria, and constraints explicitly.
- Add context that the model cannot infer reliably.
- Use a few consistent examples when format, tone, or classification boundaries
  are fragile.
- For heavy reasoning, rely on `thinkingLevel: "high"` and simple prompts
  before adding chain-of-thought style instructions.
- Do not ask for hidden reasoning in the final answer. Ask for conclusion,
  checks, assumptions, and evidence instead.
- For current, obscure, or factual claims, enable grounding/search tools when
  available or require external citations from the calling agent.
- For arithmetic, counting, or code-like calculation, prefer a tool or code
  execution path when available.

## Gemini 3.1 Notes

- Gemini 3 models respond best to direct prompts with clear structure and
  separated context/task/constraints.
- Internal thinking is already part of the model family; prompt for careful
  work, not verbose reasoning transcripts.
- `thinkingLevel: "high"` is the default for this MCP because the user chose
  maximum reasoning over speed/cost.
- If a run is too slow or expensive, lower `thinkingLevel` only as an explicit
  tradeoff and report that the call no longer uses the strongest reasoning
  setting.
