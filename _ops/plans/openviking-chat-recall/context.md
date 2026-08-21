---
эпик: "самостоятельный experiment: openviking-chat-recall"
kind: context
записано: 2026-08-21
---

# Контекст — почему OpenViking Wiki

## Что изменилось

`chat-recall` хорошо сохраняет голос владельца, но его единица — цитата в
датированном holder. Повтор одной позиции, её эволюция и сводный документ не
имеют собственного потребительского представления. Владелец заказал не новый
поиск цитат, а нормальную библиотеку знаний из всего старого корпуса.

Graphiti решает другую задачу: извлекает temporal graph и ищет факты, но не
создаёт читаемую Wiki с каталогом документов. Поэтому новый outcome не является
продолжением Graphiti ingest и не должен наследовать его runtime-статус.

## Почему именно Compile + LLM Wiki

OpenViking уже владеет нужным классом решения:

- Compile читает corpus, применяет выбранный Skill и пишет новый knowledge tree;
- официальный LLM Wiki Skill разделяет entity, concept, method, comparison и
  analysis, объединяет дубли и требует provenance;
- OpenViking автоматически держит L0/L1/L2 representations для экономного
  context loading.

Мы меняем только `reason`: recurrence должно стать явным знанием с количеством,
первой/последней записью и chronology. Prompt/Skill upstream не форкается до
доказанного ограничения stock route.

## Граница истины

```text
_ops/chat-recall/**                 immutable source evidence
        ↓ static snapshot/import
OpenViking viking://resources/**   runtime resource tree
        ↓ Compile + official Skill
chat-recall-wiki/**                derived, rebuildable knowledge library
```

Wiki служит чтению и поиску, но не получает права переписывать слова владельца
или автоматически менять GOAL, Product Frames, skills и инструкции.

## Язык

Текущий Compile language route OpenViking ограничен `en` и `zh-CN`. Первый
pilot сохраняет stock behavior: Wiki на английском, вопросы и ответы агента на
русском. Это проверяет именно технологию OpenViking. Русский fork допустим лишь
после falsifying evidence, что межъязыковой слой мешает retrieval или
применению.

## Upstream и лицензия

На старте исследования проверены PyPI `openviking==0.4.16`, upstream commit
`9042a0254f9285aeab1779cc648440a5cf3108e5` и корневой `LICENSE` AGPL-3.0.
Writer обязан проверить и записать реально установленный runtime; README-claim
не заменяет authoritative license или package receipt.

## Принятый компромисс

«Превратить цитаты в библиотеку» означает заменить потребительский маршрут
агента, а не удалить provenance. Если библиотека проходит audit, агент сначала
читает Wiki и раскрывает holders только для проверки evidence. Если не проходит,
исходная система остаётся целой и эксперимент можно удалить без потери знания.
