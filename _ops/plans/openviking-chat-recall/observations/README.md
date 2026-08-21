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

## 2026-08-21 — Wiki pages и context layers имеют разных upstream owners

**Вывод.** Reusable compiler должен фиксировать две независимые OpenViking
поверхности: LLM Wiki Skill задаёт L2 semantic pages и `index.md`, а core
Context Layers задаёт L0 `.abstract.md`, L1 `.overview.md`, bottom-up generation
и progressive reading. Нельзя приписывать L0/L1 промпту Wiki.

**Evidence.** Текущий и pinned `SKILL.md` одинаково запрещают самому Wiki-agent
генерировать semantic sidecars и говорят, что ими владеет Compile. Официальный
`docs/en/concepts/03-context-layers.md` отдельно определяет L0/L1/L2,
token budgets и bottom-up generation. Root проверил оба источника напрямую на
commits `2af48624…` и `499995f3…`.

**Что меняет.** Prompt/provenance manifest, validators и tests разделяются на
`wiki_l2` и `context_layers_l0_l1`; custom compiler соединяет их только через
явный interface.

**Граница.** Это source-backed ownership seam. Точная локальная реализация
semantic prompt templates, их лицензионная применимость и retrieval benefit
ещё требуют проверки.

## 2026-08-21 — История выбирает знание, но не становится Wiki

**Вывод.** Reusable compiler должен разделять три поверхности: неизменяемые
source records хранят точные слова и chronology; evidence manifest хранит
адреса, membership и измеримые temporal facts; Wiki показывает
дистиллированные применимые claims. История может помочь определить, какой
claim жив, но не должна по умолчанию превращать страницу знания в отчёт о его
эволюции.

**Evidence.** Владелец прямо отделил хронологию цитат от дистиллированной Wiki
(`_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`). Ранее blind Wiki v1
выбрала историческую задачу вместо текущей, хотя provenance links были на
месте (`modules/return-wave-2-v1-diagnostic.md`).

**Что меняет.** Default Wiki schema больше не требует `count`, `first/latest`
или narrative evolution в теле страницы. Она требует current claim,
applicability, lifecycle-status и source record IDs; история раскрывается через
manifest/holders по отдельному маршруту.

**Граница.** Автоматическое определение supersession ещё не доказано. До
массовой генерации нужен held-out кластер с реальной отменой позиции.

## 2026-08-21 — Upstream надо фиксировать кортежем артефактов

**Вывод.** Версия пакета или digest одного prompt не фиксируют технологию
компиляции. Manifest будущего инструмента должен отдельно закреплять commit,
URL и SHA-256 каждого upstream owner: Wiki Skill, L1 prompt, Context Layers
contract и generator code path.

**Evidence.** Между OpenViking v0.4.16 (`499995f3…`) и current commit
`2af48624…` Wiki Skill не изменился, а `overview_generation.yaml` изменился с
SHA-256 `5a67431d…` на `6a3e077f…` и получил coverage-aware contract. Root
проверил оба source snapshots; детали — `modules/_returns/wave-4b-contracts.md`.

**Что меняет.** Upstream loader и receipts валидируют весь provenance tuple;
drift одного элемента инвалидирует зависимые generated layers.

**Граница.** Проверены только необходимые этой реализации upstream artifacts
и две named revisions; это не общий аудит совместимости всего OpenViking.
