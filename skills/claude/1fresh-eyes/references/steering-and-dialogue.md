---
description: "Correct input or continue a retained expert without manufacturing another fresh vote."
---

# Steering And Retained Dialogue

Read after spawn only when a running/returned expert needs corrected input,
reconsideration or deeper consultation.

The first pass is independent. After main-context intervention the same stream
remains useful, but it is not another fresh vote. Correct understanding, never
the desired conclusion or native method.

## Operations

| Situation | Action | Synthesis label |
|---|---|---|
| Running agent missed a fact/scope boundary | Send a short delta | steered pass |
| Returned answer rests on wrong premise/source | Follow up on the same target | repaired pass |
| Valid expert is already loaded; deeper residual risk is needed | Follow up without repackaging role | retained consultation |
| Goal/question/lens changed, original brief was leading, or independence is required | New clean-context spawn | fresh stream |

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

When a custom/general-purpose subagent completes, retain the returned agent ID
or unique name. Continue it through `SendMessage(to: agent_id|name)`; completed
agents auto-resume under the same ID. Built-in Explore/Plan are one-shot and
return no resumable ID. A new `Agent` invocation is a fresh stream, not a
resumed pass. Follow-up never expands original permissions or write scope.

## Stop

Synthesize once the correction and revised/unchanged verdict are clear. If two
successive turns do not narrow evidence, alternative or decision boundary,
stop. A new independence requirement needs a new stream.
