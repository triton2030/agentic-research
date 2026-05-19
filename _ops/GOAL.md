# GOAL

## Что делаем

Создаём полигон знаний, критериев и рабочих контрактов, который помогает
будущей ИИ-сессии проектировать и улучшать skills, agents, prompts и
instruction files под `GPT-5.5` и `Claude Opus 4.7`.

## In scope

- Собирать и поддерживать `knowledge/`: wisdom, guides, practical guides,
  examples и research для агентных систем.
- Улучшать skill contracts, instruction files, routing, prompt-подходы,
  guardrails и owner-модели.
- Держать `_ops/criteria/*.md` как устойчивые критерии по сфере будущей работы.
- Использовать `_ops/problems/**` только для актуальных проблем до стратегии,
  задачи, критерия или решения.
- Использовать `_ops/interviews/**` как временный вход для длинного сбора
  ответов пользователя.
- Использовать `_ops/plans/**` только по явному запросу для активной сложной
  работы.
- Сверять рабочий канон с модельной парой `GPT-5.5` / `Claude Opus 4.7`.

## NOT in scope

- Runtime-код агентов или продуктовая кодовая база.
- Каталог project artifacts и сохранение чужих рабочих материалов ради архива.
- Backlog, inbox или обязательная стадийная дорожная карта.
- Model-neutral канон под все модели сразу.
- Рост instruction-процесса вместо более точных scope, evidence, validation и
  stop rules.
- Восстановление `INTERVIEW.md`, `LEARNINGS.md` или `projects/` как живых
  рабочих поверхностей.
- Новые control surfaces без выбранной функции и owner-а.

## Definition of done

- Новая ИИ-сессия без устного контекста понимает контракт проекта, текущий
  режим, критерии и нужный owner-маршрут.
- `README.md`, `_ops/GOAL.md`, `_ops/PROJECT-ROADMAP.md`,
  `_ops/criteria/*.md` и живые skills не дублируют source of truth друг друга.
- Старые model-neutral или process-heavy советы либо удалены, либо сужены, либо
  оставлены только как research evidence.
- Работа над skill / prompt / instruction file начинается от локальных знаний,
  применимых критериев и текущего owner-контракта.

## Stop rules

- Меняется основной outcome, scope, NOT in scope или definition of done проекта.
- Новый файл, папка, скилл, hook или guardrail создаёт второй source of truth.
- Roadmap, criteria, instruction file или skill начинает владеть тем, что
  должен держать `_ops/GOAL.md`.
- Нужно расширить модельную рамку за пределы `GPT-5.5` / `Claude Opus 4.7`.
- Для продолжения не хватает прямого пользовательского сигнала о цели,
  красной линии или критерии принятия.
