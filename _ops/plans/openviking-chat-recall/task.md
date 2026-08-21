---
эпик: "самостоятельный experiment: openviking-chat-recall"
режим: Execution
kind: task
создано: 2026-08-21
---

# Batch compiler знаний из chat-recall

## Цель

Превратить полный статический snapshot `_ops/chat-recall/` в удобную агентам
библиотеку дистиллированных знаний: официальный LLM Wiki Skill OpenViking
задаёт L2-страницы и `index.md`; официальный Context Layers contract и semantic
prompts задают bottom-up L0/L1. Runtime OpenViking в принятом маршруте не
участвует.

Исходные holders остаются неизменяемым evidence. Библиотека — производная,
проверяемая и полностью пересобираемая поверхность чтения в
`experiments/openviking-chat-recall/`.

## Критерии успеха

- Frozen inventory адресует каждую запись snapshot по source path, record ID,
  timestamp и digest; для каждой записи есть ровно один итог: использована,
  отклонена валидатором или пропущена с явной причиной.
- Детерминированный слой единолично владеет membership, exact count,
  first/latest и provenance. Эти evidence-поля не обязаны появляться в теле
  Wiki и сами по себе не доказывают, какая позиция актуальна.
- Semantic claim отделён от source history: он содержит дистиллированное
  знание, область применимости, lifecycle-status и source record IDs. Модель
  может предложить status или supersession, но validator не принимает их без
  адресуемой опоры; точный минимальный contract закрывает representative
  probe до общей writer-волны.
- Смысловой compiler использует зафиксированный snapshot официального
  OpenViking LLM Wiki Skill для L2: `index.md`, `entity`, `concept` и только
  обоснованные `method`, `comparison`, `analysis`, `summary`. Пустые типы и
  source-by-source пересказы не создаются ради симметрии.
- Layer compiler отдельно использует зафиксированный OpenViking Context Layers
  contract и его semantic prompt templates: для каждой semantic directory
  bottom-up создаются L0 `.abstract.md` (~100 tokens) и L1 `.overview.md`
  (~2k tokens), а L2 остаётся полным набором source-backed Wiki pages.
- Происхождение, upstream commit, digest и граница лицензии фиксируются для
  Wiki Skill и Context Layers/prompts раздельно; локальные добавления не
  выдаются за upstream behavior.
- Повторы сводятся в одно актуальное знание. Exact count, первая/последняя
  фиксация и полный путь изменения остаются в evidence manifest и holders;
  Wiki не пересказывает историю по умолчанию. Конфликт или неразрешённая
  актуальность остаются видимыми как status, а не сглаживаются в уверенный факт.
- Build возобновляется после сбоя, повторный запуск на том же snapshot
  воспроизводим, секреты и полный приватный corpus не попадают в receipts или
  внешнюю публикацию.
- Закрытый held-out audit сравнивает Wiki и исходные holders на одинаковых
  knowledge-вопросах. Wiki принимается только при не худшей корректности и
  актуальности: минимум одна из осей `context tokens` или `evidence reads`
  улучшается не менее чем на 25%, а `typed reads`, tokens и reader elapsed не
  ухудшаются более чем на 10%. Исторический вопрос должен адресно
  маршрутизироваться к holders; confident ответ на no-gold или superseded claim
  как на current — hard failure.
- Полный backfill имеет inventory/coverage/build receipts и короткий agent
  route: Wiki — для знаний; holders — для точных слов, истории, проверки
  provenance и неразрешённой актуальности.
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
| 1. Контракты | Frozen corpus map, distilled-claim seam, pinned Wiki Skill, pinned Context Layers/prompts, generation route, acceptance и privacy/recovery contracts не противоречат друг другу; supersession probe пройден |
| 2. Compiler | Детерминированный pipeline, semantic generation, validators, resume state и receipts проходят узкие tests на representative sample |
| 3. Full build | Весь frozen snapshot обработан; coverage manifest не содержит молчаливых пропусков |
| 4. Normalize | Layered Wiki, каталог, cross-links, claim status и provenance прошли механические инварианты и выборочную ручную сверку |
| 5. Acceptance | Blind held-out сравнение подтвердило correctness и экономию чтения/context; agent route и rebuild handoff записаны |

## Подробная карта исполнения

Ось разреза — зависимая цепочка доказательств. Следующий этап получает только
принятый и адресуемый выход предыдущего; зеленый downstream не перекрывает
провал upstream.

    G0 frozen semantic contract
      → F1 frozen snapshot
      → F2 deterministic evidence
      → F3 stable semantic partitions
      → P0 representative end-to-end L2/L1/L0 ingestion
      → U0 matched final-route utility gate
      → S1 semantic candidates
      → S2 canonical current claims
      → L2 typed Wiki pages + catalog
      → per-depth L1 → L0, from leaves to root
      → full coverage/resume/rebuild receipts
      → blind matched acceptance
      → fresh-agent route or rejection

Детали принадлежат модульным карточкам:

| Волна | Карточка | Вход | Выход | Открывает |
| --- | --- | --- | --- | --- |
| 5 | [wave-5-distilled-probe](modules/wave-5-distilled-probe.md) | frozen real records + locked five-case gold | принятый claim/currentness contract; не utility verdict | deterministic foundation |
| 6 | [wave-6-snapshot-evidence](modules/wave-6-snapshot-evidence.md) | принятый semantic contract + explicit corpus commit | frozen source lock, records, coverage input, stable partitions | representative ingestion |
| 6b | [wave-6b-representative-ingestion-utility](modules/wave-6b-representative-ingestion-utility.md) | representative frozen subset + final L2/L1/L0 route | matched correctness/currentness/efficiency verdict | full semantic generation |
| 7 | [wave-7-semantic-claims](modules/wave-7-semantic-claims.md) | Wave 6b PASS + partitions + pinned Wiki prompt tuple | canonical claims, rejections, lifecycle evidence | L2 writers |
| 8 | [wave-8-l2-library](modules/wave-8-l2-library.md) | accepted canonical claims | typed L2 pages, catalog, validated index | context layers |
| 9 | [wave-9-context-layers](modules/wave-9-context-layers.md) | accepted L2 tree + pinned L1 prompt | bottom-up L1/L0 sidecars | finalization |
| 10 | [wave-10-full-build-operations](modules/wave-10-full-build-operations.md) | all stage outputs and receipts | exhaustive coverage, resume/rebuild proof, private build receipt | held-out acceptance |
| 11 | [wave-11-blind-acceptance](modules/wave-11-blind-acceptance.md) | frozen candidate + locked gold | matched correctness/currentness/efficiency verdict | route decision |
| 12 | [wave-12-fresh-agent-handoff](modules/wave-12-fresh-agent-handoff.md) | terminal Wave 11 verdict: accepted route or explicit rejection | clean-session route, rebuild handoff, independent completion audit | завершение |

Карточка становится разрешением на исполнение только когда ее dependency gate
закрыт в status.md. До этого это подробная проекция остатка, а не permission
запускать downstream.

## Инварианты волн

- Corpus commit, upstream tuple, prompt/config digests и output topology
  фиксируются до первой записи каждой зависимой волны.
- Root единолично владеет plan/status, shared catalog/index, final manifests,
  интеграцией Worktree commits и публикацией route verdict.
- Параллельные Luna Max writers получают только конкретный part-* или
  semantic-directory footprint; shared файлы им запрещены.
- Модель предлагает grouping, claim и lifecycle candidate. Детерминированный
  слой владеет source membership/provenance; отдельный validator принимает или
  отклоняет semantic output.
- Любой record frozen snapshot имеет ровно один coverage-disposition:
  used, rejected или skipped с причиной. Silent skip запрещен.
- Resume разрешен только для stage со статусом pass и совпавшими input,
  output, code, prompt и config digests. Drift инвалидирует stage и descendants.
- Receipts содержат IDs, counts и digests, но не полные приватные цитаты,
  секреты или corpus dumps.
- Generated-root cleanup удаляет только доказанно owned файлы внутри
  разрешенного root; path traversal и symlink escape обязаны fail closed.
- Ни writer self-report, ни гладкая Wiki, ни тест узкого fixture не закрывают
  full-corpus usefulness. Приемка принадлежит непишущим readers/auditors.

## Stop rules

- Full semantic backfill не начинается, пока representative frozen sample не
  пройдёт настоящий L2/L1/L0 ingestion и matched final-route audit. Wave 6
  deterministic snapshot/evidence может выполняться раньше этого utility gate.
- Semantic provider не получает реальные holders, пока synthetic canary не
  доказал auth, data-egress, logging, retry, cost и secret-redaction contract.
- Full-build snapshot не берется из live directory или старого inventory:
  только explicit Git commit и пересчитанный source/record manifest.
- LLM output с отсутствующим record ID, выдуманным provenance, изменённым
  evidence-полем, неподдержанным claim или superseded claim, выданным за
  current, отклоняется, а не чинится молча.
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
- Подробные карточки вытесняют хранение остатка в чате, но не создают второй
  plan owner: task.md владеет outcome и зависимостями, status.md — живым Next,
  modules — неизменяемыми заданиями конкретного момента.

## Происхождение требований

- Решение о маршруте, локальном плане, root-orchestrator, максимальных фоновых
  Luna Max-тредах и вложенных субагентах:
  `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.
- Там же позднее уточнена центральная граница: Wiki не удаляет цитаты и хранит
  дистиллированные знания и факты, а не историю того, как к ним пришли.
- Там же владелец потребовал сохранять самые важные наблюдения отдельно как
  сырьё для будущего инструмента конвертации цитат во всех проектах.
- Требование записать подробные планы, чтобы полный остаток не потерялся:
  та же запись, позднее решение текущей сессии.
- Неизменяемость holders и source-bound evidence: `_ops/AGENTS.md`.
- L2 prompt/IA: официальный OpenViking
  `examples/compile/ov-compile-skills/llm-wiki/SKILL.md`. L0/L1 contract и
  prompts: `docs/en/concepts/03-context-layers.md` и semantic prompt templates;
  точные версии и digests обязана зафиксировать веха 1.
- Отрицательный stock-runtime evidence и положительный typed-evidence probe:
  прежние returns этой папки и `experiments/openviking-chat-recall/artifacts/`.
