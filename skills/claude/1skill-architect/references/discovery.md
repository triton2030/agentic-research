## Discovery contract

Для model-invoked skill `description` решает, откроется ли body. Его opening
должен назвать наблюдаемый момент и stake: какой правдоподобный провал
произойдёт без скилла. Capability list и безрисковое «helps with...» не дают
модели причины потратить контекст.

Полная causal story, механизм и примеры остаются в body. `description` — не
summary, а убедительный указатель: **condition × stake**. Проверь его против
полного live candidate canvas и реальных near-misses; общий trigger phrase —
сигнал ownership/collision, а не повод для буквального dedupe.

## Discovery Contract

A model-invoked description must preserve one routing function:
**Condition × Stake**.

- **Condition** is an observable anchor Claude can recognize now: a user
  phrase, action, artifact, file, or path. An abstract topic is weaker than an
  observable moment.
- **Stake** is the plausible failure or lost advantage that makes opening the
  body worthwhile.
- A capability catalog does not replace a trigger.
- The description remains a pointer to the body, not its digest.

Cut test: if removing a phrase does not change which skill should activate
against live neighbors, it is a no-op or body material.

Дословно из словаря — то, что действует в момент письма `description`:

- **Hot Zone.** The opening clause or sentence of an implicit `description`. Put
  the main moment and trigger words here because runtime discovery can shorten
  metadata or decide before the body is available.
- **Observable Anchor.** Prefer path/file/action over abstract categories that
  require self-classification.
- **Description Budget.** _Avoid_: 1024 as target, premature shortening.
