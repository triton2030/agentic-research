---
description: "Correct input or continue a retained Claude agent without manufacturing another fresh vote."
---

# Steering And Retained Dialogue

Read after a fresh first pass only when a running/returned agent needs corrected
input, reconsideration or deeper consultation.

The first pass is independent only when it started as a new ordinary non-fork
`Agent` invocation with a self-contained non-leading brief. After main-context
intervention the same stream remains useful, but it is not another fresh vote.
Correct understanding, never the desired conclusion or native method.

## Operations

| Situation | Action | Synthesis label |
|---|---|---|
| Running agent missed a fact/scope boundary | `SendMessage` with a short delta | steered pass |
| Returned answer rests on wrong premise/source | `SendMessage` to the same ID/name | repaired pass |
| Valid expert is already loaded; deeper residual risk is needed | Resume without repackaging role | retained consultation |
| Goal/question/lens changed, context was forked, original brief was leading, or independence is required | New ordinary non-fork `Agent` invocation | fresh stream |

Valid corrections are facts, owner/source, outcome, scope, forbidden side
effects, missing evidence and claims not supported by the cited source.
Professional disagreement is not a misunderstanding.

## Delta-Only Follow-Up

```text
Коррекция контекста: вывод опирается на {X}. {path#section} показывает {Y}.
Сохрани прежнюю роль, scope и read-only boundary. Пересмотри только findings,
зависящие от X; скажи, изменился ли verdict и почему.
```

For deeper consultation:

```text
Продолжи в той же lens. Если main выберет {route}, какой residual risk,
missing input или cheapest probe останется? Не внедряй изменения.
```

Use `SendMessage(to: agent_id|name)` for a running or completed custom/named
agent; completion does not erase its retained history. Built-in Explore/Plan
are one-shot and return no resumable ID. A new standard named `Agent`
invocation is a fresh conversation context; `context: fork`, `/subtask` and a
resumed ID are not. Follow-up never expands original permissions or write
scope.

## Stop

Synthesize once the correction and revised/unchanged verdict are clear. If two
successive turns do not narrow evidence, alternative or decision boundary,
stop. A new independence requirement needs a new stream.
