# Нативные операции Codex

## Цель

Довести одно текущее решение controller-а до наблюдаемого результата.

## Общая truth

Актуальные official Codex docs задают public semantics, а current callable
schema — exact native calls. При отсутствии нужного call верни exact gap, не
выдумывай.

Для каждого текущего решения выбери одну branch; следующее решение начинай
заново.

## Mode

Обычный offload — managed: используй `1orchestration`, жди terminal или
explicit blocker/needs-input, затем root принимает end-to-end decision.

Literal create/fork с возвратом handle — launch-only: `1orchestration` не
нужен, а handle означает launch, не outcome.

## Model and environment

Luna/max — default. Sol доступен только при addressable evidence реальной
сложности сверх Luna и только на `medium` или `xhigh`; если capable route не
доказан, верни gap вместо auto-upgrade.

Local — default. Worktree допустим только при доказанном write overlap, который
не устраняется ownership split или safe isolation.

## Reuse

Разреши ровно один ready same-topic `threadId`; archived retained topic должен
быть discoverable, затем unarchive и отдельно прочитай его state, refresh
current truth, отправь follow-up только после refresh и проверь unpinned state.

## Launch

Create/fork выполняй только по explicit owner request; launch nonblocking,
handle не outcome.

Для queued create/fork дождись ready `threadId` до unpinned verification; если
readiness не наблюдается, верни gap, иначе верни только observed unpinned
handle.

Fork использует completed history и не переносит active turn.

Receiver launch передаёт подготовленный receiver prompt.

Continue выполняй только с ready `threadId`: отправь prepared receiver prompt с
refreshed current truth и затем проверь unpinned state.

## Managed closure

Managed закрывается только на observed terminal или explicit
blocker/needs-input; progress остаётся active.

Mutable writer result требует independent external check; self-report
недостаточен, а read-only result writer-check не требует.

Archive bounded thread только после root acceptance и integration; retained
umbrella держи active, пока topic продолжается, и архивируй после service
completion и acceptance; persistence pin/archive подтверждай отдельным read,
потому что setter return не является доказательством.
