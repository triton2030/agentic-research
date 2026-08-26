---
description: Память агента и quality gate для learnings — почему eviction обязателен, и почему user corrections сильнее observations.
---

# Agents — Memory & Learnings

Снимок на 20 мая 2026. Снято с `wisdom-agents.md` при function-split refactor.

Здесь принципы про память агента, обновление learnings и self-learning
loops. Runtime гарантии (где живёт критическое ограничение) — `runtime-layer.md`.
Evaluation memory effectiveness — `evaluation.md`.

## Проверено

- Память агента должна забывать по дизайну: полная retention деградирует качество, цель — useful recall, не perfect recall. Eviction policy — обязательный элемент архитектуры памяти, не опциональный.
- User corrections — сильнейший сигнал для обновления памяти и learnings. Correction уже несёт вес пользовательского внимания; observation из собственного хода агента — слабее.
- Записывать learnings имеет смысл через quality gate (specific, actionable, scope-bound). Ожидаемая отбраковка кандидатов — 60-70%. Отсутствие записи — валидный исход.
- Self-learning criteria layer должен быть связкой из трёх петель: read-before, capture-after и periodic-prune. Любая из трёх без остальных деградирует файл: без read — контекст не влияет, без capture — не обновляется, без prune — превращается в мусор.
- Compaction должна быть типизированной: правила, authority и safety-квалификаторы
  сохраняются с точной формулировкой и проверяются после сжатия; episodic history
  можно сжимать агрессивнее. Это design evidence, а не гарантия конкретного
  runtime: на Sonnet 4.6 в одном препринте type-blind compaction сохраняла 53%
  safety rules после одного раунда и 10% после пяти, тогда как typed strategy
  держала 96% после пяти
  ([Compaction Cliff](https://arxiv.org/html/2608.22752), 24 августа 2026).

## Опоры

- `/knowledge/guides/perfect-context-engineering.md`
  Устойчивые правила про отделение долгоживущей рамки от ephemeral context.
