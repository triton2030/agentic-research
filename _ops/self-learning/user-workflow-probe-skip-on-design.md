# User workflow probe skip on feature design

## Observation

При design новой feature / tool / skill модель спрашивает пользователя про **общие категории болей** («discoverability vs hybrid vs cost vs aesthetics») вместо **конкретного use-case workflow** («покажи 2-3 реальных задачи, где ты использовал бы это»). Категории звучат rigorous, но пропускают **shape** реальной потребности. Пользователь не выбирает ни один из вариантов, а **reformulates** в своих словах — это сигнал, что варианты не resonate.

Близкое к archived `equal-options-vs-root-cause`, но specific к design phase: ошибка не в predisposition к одной опции, а в **shape опций**. Список абстрактных категорий вместо probe реального flow.

## Counter

- 2026-05-21 [Claude Opus 4.7]: сессия про MCP `md_read_related`. Я спросил «сделать оба corrective fixes или только один?». User отверг shape вопроса и сформулировал реальную боль: «агент пропускает связанные смыслы — хочу обогащение страницы content'ом связанных блоков на 1-2 шага по дереву». Реальный feature был anchor-aware extraction. Из общих категорий, что я предложил ранее (discoverability / hybrid / unified backend), эта потребность не была покрыта — я probed уровнем выше реального workflow. Скрытое предположение: «у пользователя боль той же формы что у меня в голове». Пришлось reframe и переписать backend в той же сессии (~30 строк Python новой parser логики + 50 строк related.py refactor).

## Possible upgrade

Перед feature design — спрашивать «покажи 1-2 реальных сценария использования» (workflow probe) **до** предложения дизайн-вариантов. Если пользователь даёт workflow → variants можно построить вокруг него. Если пользователь даёт только common pain → variants легко уходят в abstract категории, mismatch becomes invisible until user reformulates вручную. Это `1interview-tool` territory когда вопросов больше трёх — но даже 1-2 sample workflow вопроса до AskUserQuestion с design-вариантами radically уменьшают frame miss.
