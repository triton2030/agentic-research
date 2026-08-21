---
эпик: "самостоятельный experiment: openviking-chat-recall"
режим: Execution
kind: task
создано: 2026-08-21
---

# Batch compiler знаний из chat-recall

## Цель

Превратить полный статический snapshot `_ops/chat-recall/` в удобную агентам
библиотеку знаний: точные recurrence/chronology/provenance вычисляются
детерминированно, а официальный prompt, information architecture и layered
projection OpenViking используются для смысловой сборки документов. Runtime
OpenViking в принятом маршруте не участвует.

Исходные holders остаются неизменяемым evidence. Библиотека — производная,
проверяемая и полностью пересобираемая поверхность чтения в
`experiments/openviking-chat-recall/`.

## Критерии успеха

- Frozen inventory адресует каждую запись snapshot по source path, record ID,
  timestamp и digest; для каждой записи есть ровно один итог: использована,
  отклонена валидатором или пропущена с явной причиной.
- Детерминированный слой единолично владеет membership, exact count,
  first/latest, chronology и provenance. LLM не вычисляет и не исправляет эти
  факты.
- Смысловой compiler использует зафиксированный snapshot официального
  OpenViking LLM Wiki prompt и его IA. Происхождение, upstream commit и граница
  лицензии записаны в receipt; локальные добавления отделены от upstream.
- Результат организован как семантические директории и страницы нужных типов
  (`entity`, `concept`, `method`, `comparison`, `analysis`) с каталогом и
  слоями: L0 abstract, L1 overview, L2 source-backed page body. Пустые типы и
  source-by-source пересказы не создаются ради симметрии.
- Повторы сводятся в одно знание, но сохраняют exact count, первую и последнюю
  фиксацию, эволюцию позиции, противоречия и адреса исходных records.
- Build возобновляется после сбоя, повторный запуск на том же snapshot
  воспроизводим, секреты и полный приватный corpus не попадают в receipts или
  внешнюю публикацию.
- Закрытый held-out audit сравнивает Wiki и исходные holders на одинаковых
  вопросах. Wiki принимается только при не худшей корректности/chronology и
  материально меньшем количестве чтений или context tokens; confident ответ на
  no-gold вопрос — hard failure.
- Полный backfill имеет inventory/coverage/build receipts и короткий agent
  route: сначала Wiki, holders — только для проверки evidence.
- Только подтверждённые переносимые выводы для будущего cross-project compiler
  записываются в `observations/README.md`; локальная хроника и гипотезы туда не
  попадают.

## Не входит

- Realtime capture, hooks, watcher или подмена `1chat-recall`.
- Удаление, редактирование или архивирование `_ops/chat-recall/**`.
- Возобновление Graphiti ingest; его артефакты остаются внешним baseline.
- Stock SDK/server/Compile OpenViking и локальные compatibility shims к ним.
- Публикация исходных цитат, персональных данных или Wiki наружу.
- Перенос кода OpenViking в иной продуктовый owner.

## Вехи

| Веха | Проверяемый результат |
| --- | --- |
| 1. Контракты | Frozen corpus map, compiler seam, pinned OpenViking IA/prompt, LLM route, acceptance и privacy/recovery contracts не противоречат друг другу |
| 2. Compiler | Детерминированный pipeline, semantic generation, validators, resume state и receipts проходят узкие tests на representative sample |
| 3. Full build | Весь frozen snapshot обработан; coverage manifest не содержит молчаливых пропусков |
| 4. Normalize | Layered Wiki, каталог, cross-links и recurrence/chronology прошли механические инварианты и выборочную ручную сверку |
| 5. Acceptance | Blind held-out сравнение подтвердило correctness и экономию чтения/context; agent route и rebuild handoff записаны |

## Stop rules

- Full build не начинается, пока representative sample не проходит exact-fact
  validators и semantic audit.
- LLM output с отсутствующим record ID, выдуманным provenance, изменённым
  count/chronology или неподдержанным claim отклоняется, а не чинится молча.
- Если official prompt/IA нельзя использовать с проверяемым provenance или
  приемлемой лицензионной границей, работа останавливается перед semantic
  generator.
- Если held-out audit не показывает пользы против holders, Wiki не становится
  рекомендуемым agent route, даже если build технически завершён.

## Principles trace

- Владелец выбрал собственный batch compiler вместо broken stock runtime и
  потребовал использовать именно OpenViking prompts, IA и layered projection.
- Existing frame дополняется: один plan owner и один derived experiment;
  `_ops/chat-recall/` не дублируется и остаётся источником доказательств.
- `observations/` владеет только переносимыми experiment learnings; он не
  дублирует plan status, implementation truth или страницы Wiki.
- Self-report writer’а не является приёмкой: каждую существенную границу
  проверяет независимая рука или исполняемый validator.
- Максимальный fan-out ограничен реальными независимыми зонами; writers
  запускаются только после согласования read-only контрактов первой волны.

## Происхождение требований

- Решение о маршруте, локальном плане, root-orchestrator, максимальных фоновых
  Luna Max-тредах и вложенных субагентах:
  `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.
- Там же владелец потребовал сохранять самые важные наблюдения отдельно как
  сырьё для будущего инструмента конвертации цитат во всех проектах.
- Неизменяемость holders и source-bound evidence: `_ops/AGENTS.md`.
- Upstream prompt и IA: официальный OpenViking
  `examples/compile/ov-compile-skills/llm-wiki/SKILL.md`; точную версию обязана
  зафиксировать веха 1.
- Отрицательный stock-runtime evidence и положительный typed-evidence probe:
  прежние returns этой папки и `experiments/openviking-chat-recall/artifacts/`.
