# v6 round 1 — independent check record

Дата: 2026-08-29. Проверялся первый draft до owner-коррекции
`_ops/chat-recall/2026-08-29-152721-codex-01a04d0e.md:20`; поэтому этот раунд
не является approval evidence текущего кандидата.

## Instruction checker

1. `description` был 334 символа, выше лимита 200.
   Решение: сокращён; текущий кандидат проверяется отдельно.
2. Не было actual naked-trigger use/skip/managed/near-miss trajectories.
   Решение: candidate phrases записаны; actual probes обязательны в новом раунде.
3. Счёт `19/7/8` укрупнял независимо нарушимые предикаты и не показывал active
   set стадии.
   Решение: normal flow разрезан на самостоятельные stages, добавлена таблица
   `body + reference + carried obligations`.
4. Потеряно owner-решение `address · repeat in moment · evidence owner`.
   Первое решение: вернуть. Поздняя owner-коррекция `2026-08-29…:20` заменила
   default на `owner-address + delta`; scoped receiving-owner exception сохранён.
5. Формат one-stream «одна строка» не имел owner/default chain.
   Решение: снят вместе с отдельной managed-offload ветвью.
6. Recovery restrictions не называли провал и цену строгости.
   Решение: цепочки `default → mechanism → decision → harm → price` записаны в
   текущем `refactor-map.md`.
7. Wave-level wait/repair мог перехватить runtime lifecycle.
   Решение: semantic barrier остаётся у orchestration, tool lifecycle — у live
   runtime owner-а.
8. Root-break без plan/carrier не имел terminal.
   Решение: нет addressable state → `UNKNOWN`/final blocker без replay.
9. Correctness-bearing порядок не был оформлен как behavior protocol с
   буквальными owner-формулировками.
   Решение: owner-цитаты находятся в теле, а стадии следуют порядку мышления.

## Trajectory checker

Единственное finding: recovery без plan/carrier мог восстановить accepted state
из памяти и повторить external action. Решение совпадает с пунктом 8: replay
разрешён только из addressable state; иначе dependent branch блокируется.

## Clean managed-offload executor

Наблюдаемая форма первого draft: один bounded read-only Codex thread, без
general wave, reviewer, plan, carrier или worktree. В chat-map были outcome,
order, barrier, write ownership, instruction focus и return; THREAD_CARD нёс
goal, done_when, context, scope, environment, return и retention. Root сохранил
acceptance и synthesis.

Gaps: scenario не содержал точных log roots и investigation question, поэтому
brief был структурно полным, но не launch-ready. После owner-коррекции этот
прогон доказывает только отсутствие лишнего fan-out; source map, delta-only
brief и active-unit budget он не проверяет.

## Вердикт раунда

Первый draft отклонён. Findings применены, но новая owner-коррекция изменила
саму функцию и trigger, поэтому текущий полный кандидат требует нового
instruction check, trajectory check и clean execution с нуля.
