---
kind: experiment-observations
scope: openviking-chat-recall
owner: root-orchestrator
updated: 2026-08-21
---

# Переносимые наблюдения

Здесь живут только подтверждённые выводы текущего эксперимента, способные
изменить контракт будущего project-independent инструмента конвертации
`chat-recall` в layered knowledge library.

## Admission gate

Запись появляется, только если одновременно:

1. есть direct command/source evidence, а не self-report агента;
2. вывод сформулирован без зависимости от локального имени файла или темы;
3. вывод меняет архитектурный, операционный или acceptance contract будущего
   инструмента;
4. названа граница, за которой вывод ещё не доказан.

Иначе сигнал остаётся в чате, module return или `_ops/findings/`. Этот файл не
владеет status, планом, implementation truth, страницами Wiki и решениями о
создании общего инструмента. Promotion в такой инструмент требует отдельного
owner-решения.

## 2026-08-21 — Exact evidence предшествует semantic compression

**Вывод.** Универсальный compiler должен вычислять identity, membership, exact
count, first/latest и provenance детерминированно и передавать их модели как
неизменяемые typed facts. LLM может группировать и объяснять смысл, но не
владеет этими точными значениями.

**Evidence.** One-shot semantic V2 получила 4 FAIL, 1 UNKNOWN и outcome
inversion (`modules/return-wave-2-v2-audit.md`). После разделения seam commit
`9319f71` прошёл 5/5 tests и byte-identical rebuild; blind Luna Max reader
восстановил exact recurrence и все пять обязательств
(`modules/return-wave-3-typed-evidence-probe.md`).

**Что меняет.** В будущем tool deterministic evidence manifest и его validator
являются обязательным входом semantic generator, а не дополнительной
проверкой после генерации.

**Граница.** Доказано для records со стабильными source addresses и timestamps.
Качество автоматического semantic clustering полного разнородного корпуса этим
ещё не доказано.
