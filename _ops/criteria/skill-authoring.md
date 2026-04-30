# Skill Authoring Criteria

## Зона ответственности

Когда работа создаёт, переписывает или проверяет `SKILL.md`, trigger
description, `agents/openai.yaml`, skill references или границы между скиллами.

## Цель

Скилл должен быть коротким, outcome-first и вызываться в нужный момент без
старого process-heavy поведения.

## Критерии

Rule: `description` должен ясно говорить, когда скилл использовать и когда не использовать.
Why: Codex видит `description` до тела скилла, поэтому trigger surface важнее длинного body.

Rule: Body скилла должен задавать outcome, constraints, evidence, output и stop rules, а не длинный алгоритм.
Why: Рабочая рамка проекта — `GPT-5.5` и `Claude Opus 4.7`; для них важнее outcome, scope, evidence, validation и stop condition, чем старый process stack.

Rule: Model-delta правка скилла должна удалять или сужать старое process-heavy правило, а не добавлять новый слой поверх него.
Why: Иначе live skill одновременно тянет модель к outcome-first контракту и к старому defensive process.

Rule: Tool-specific детали должны жить в tool descriptions или runtime metadata, если они не меняют общую policy.
Why: Это снижает шум в prompt и сохраняет точную ответственность tool surface.

Rule: Reasoning effort не должен повышаться как первая попытка починки скилла.
Why: Для GPT-5.5 сначала проверяются цель, критерии, ограничения, validation и stop rules.

Rule: Новый скилл создаётся только для повторяемого workflow с отдельным trigger.
Why: Иначе skill landscape разрастается как каталог идей, а не как рабочая система.

Rule: После правки live skill нужно проверить `SKILL.md` и `agents/openai.yaml` на одинаковую историю.
Why: Разные trigger descriptions создают drift между UI/metadata и фактическим контрактом.

Rule: Если скилл отвечает за момент перед записью файлов, его тело должно быть узким, а повторяемый обязательный стопор лучше выносить в hook или validator, когда Codex это поддерживает.
Why: Runtime guardrail надёжнее, чем просьба к модели помнить правило в каждом будущем ходе.

Rule: Если pre-write скилл не находит подходящий criteria-файл для целевого типа работы, он должен остановиться и вызвать `1user-truth`, а не выбирать ближайший похожий критерий.
Why: Criteria должны приходить из пользовательской правды и быть применимыми к задаче; неподходящий критерий создаёт ложную уверенность перед записью.
