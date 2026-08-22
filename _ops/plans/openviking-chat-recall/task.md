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

Исходные holders остаются неизменяемым evidence и логом изменения мысли.
Библиотека — производная, проверяемая и полностью пересобираемая поверхность
только актуальных итоговых знаний в
`experiments/openviking-chat-recall/`.

## Критерии успеха

- Frozen inventory адресует каждую запись snapshot по source path, record ID,
  timestamp и digest; для каждой записи есть ровно один итог: использована,
  отклонена валидатором или пропущена с явной причиной.
- Детерминированный слой единолично владеет membership, exact count,
  first/latest и provenance. Эти evidence-поля не обязаны появляться в теле
  Wiki и сами по себе не доказывают, какая позиция актуальна.
- Semantic claim отделён от source history: canonical claim/evidence запись
  содержит дистиллированное знание, область применимости, lifecycle-status и
  source record IDs. Wiki печатает только итоговое знание и адреса исходных
  цитат; она не ссылается на project knowledge corpus и не дополняет слова
  владельца чтением упомянутых им файлов. Модель может предложить status или
  supersession, но validator не принимает их без адресуемой опоры.
- Смысловой compiler использует зафиксированный snapshot официального
  OpenViking LLM Wiki Skill для L2: `index.md`, `entity`, `concept` и только
  обоснованные `method`, `comparison`, `analysis`, `summary`. Пустые типы и
  source-by-source пересказы не создаются ради симметрии.
- Каждая страница отвечает на один самостоятельный retrieval-вопрос. Новый
  claim обновляет страницу только когда supporting quote сама отвечает на её
  H1-вопрос; соседняя тема требует `create` или адресного `split`, а не удобного
  накопления в наиболее близком файле. Source link без page-fit не доказывает
  смысловую принадлежность claim-а странице.
- Source scene, `context-note` и названный владелец ограничивают applicability:
  локальное решение про конкретный skill, artifact или каталог не становится
  универсальным методом без отдельной source-backed опоры. Paraphrase может
  сжимать формулировку, но не расширять предмет.
- Typed claims обязаны покрывать каждый current-batch record со статусом
  `used`, но не считаются полным представлением страницы: independent audit
  проверяет против evidence весь proposed prose, включая H1 и frontmatter.
- Semantic will writer-а имеет одного версионированного owner-а:
  `experiments/openviking-chat-recall/prompts/wiki-writer.v1.md`. После
  одобрения владельцем exact prompt его path и SHA-256 фиксируются в input
  manifest, changeset и receipt. Plan владеет acceptance, но не копирует
  writing rules; ручные сообщения модели не становятся скрытой второй версией
  prompt.
- Source fidelity проверяется не только у material claims, но у каждой
  serialized surface: title/H1, description, body, check/boundary, source-link
  label, coverage reason и index cue. Каждая такая поверхность адресует source
  record либо claim, сохраняющий actor, subject, scope, modality и relation;
  короткая производная поверхность может опустить деталь, но не расширить,
  усилить или изменить связь.
- Layer compiler отдельно использует зафиксированный OpenViking Context Layers
  contract и его semantic prompt templates: для каждой semantic directory
  bottom-up создаются L0 `.abstract.md` и L1 `.overview.md`, а L2 остаётся
  полным набором source-backed Wiki pages. Официальные ориентиры длины не
  становятся нашим target или acceptance gate.
- Происхождение, upstream commit, digest и граница лицензии фиксируются для
  Wiki Skill и Context Layers/prompts раздельно; локальные добавления не
  выдаются за upstream behavior.
- Повторы сводятся в одно актуальное знание. Exact count, первая/последняя
  фиксация и полный путь изменения остаются в evidence manifest и holders;
  Wiki не пересказывает историю по умолчанию. Конфликт или неразрешённая
  актуальность остаются видимыми как status, а не сглаживаются в уверенный факт.
- При новом frozen snapshot Wiki пересобирается как replaceable projection:
  новые цитаты могут заменить итоговое знание, а superseded формулировка не
  остаётся рядом ради истории. История решения принадлежит только holders и
  evidence manifest; append-only lifecycle для Wiki запрещён.
- Количество Wiki-страниц, длина каждого файла и итоговый объём Wiki не имеют
  лимита или целевого диапазона: границы страниц следуют самостоятельным
  retrieval-вопросам, а объём — полноте знания. Ожидаемое владельцем
  5–10-кратное итоговое сжатие измеряется только после полного backfill как
  наблюдение, но не управляет writer-ом и не даёт PASS/FAIL.
- Пересказ и synthesis неизбежно создают новую формулировку и разрешены. Каждый
  существенный факт, причинная связь, scope, status, рекомендация и отношение
  между предметами должны адресовать supporting record IDs; неподдержанное
  утверждение удаляется, а действительно нужный вывод явно помечается как
  inference/uncertainty и называет evidence.
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
  route: Wiki — для актуальных итоговых знаний; source-quote addresses — для
  provenance; holders — для точных слов, истории и неразрешённой актуальности.
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
| 4. Normalize | Layered Wiki, каталог, internal links и source-quote provenance прошли механические инварианты; project-corpus links отсутствуют; cumulative compression измерена диагностически |
| 5. Acceptance | Blind held-out сравнение подтвердило correctness и экономию чтения/context; agent route и rebuild handoff записаны |

## Подробная карта исполнения

Ось разреза — зависимая цепочка доказательств. Следующий этап получает только
принятый и адресуемый выход предыдущего; зеленый downstream не перекрывает
провал upstream.

    G0 frozen semantic contract
      → F1 frozen snapshot
      → F2 deterministic evidence
      → F3 stable semantic partitions
      → C0/C1 accepted chronological Wiki checkpoints
      → T0 page-fit/split gate + deterministic replay transition
      → C2…Cn clean Luna attempt per prompt SHA, 10 holders in chronology,
        current-page rewrite
      → full coverage/resume/rebuild receipt
      → terminal L1/L0 projection over complete L2 only if it improves retrieval
      → blind matched acceptance
      → fresh-agent route or rejection

Детали принадлежат модульным карточкам:

| Волна | Карточка | Вход | Выход | Открывает |
| --- | --- | --- | --- | --- |
| 5 | [wave-5-distilled-probe](modules/wave-5-distilled-probe.md) | frozen real records + locked five-case gold | принятый claim/currentness contract; не utility verdict | deterministic foundation |
| 6 | [wave-6-snapshot-evidence](modules/wave-6-snapshot-evidence.md) | принятый semantic contract + explicit corpus commit | frozen source lock, records, coverage input, stable partitions | representative input lock |
| 6c | [wave-6c-chronological-serial-pilot](modules/wave-6c-chronological-serial-pilot.md) | F1–F3 + owner-authorized 10-holder batch | typed changeset + first candidate Wiki checkpoint + serial-route verdict | решение, заменяет ли serial fold прежний parallel semantic plan |
| 6d | [wave-6d-chronological-batch-002](modules/wave-6d-chronological-batch-002.md) | accepted batch-001 checkpoint + следующие 10 frozen holders | evidence-mapped draft → exact materialization + второй candidate checkpoint | blind findability и verdict по update/supersede |
| 6e | [wave-6e-blind-findability](modules/wave-6e-blind-findability.md) | frozen current Wiki before batch-002 draft | index-first page choices + bounded answers from a separate Luna | findability evidence independent of writer |
| 6f | [wave-6f-full-backfill-transition](modules/wave-6f-full-backfill-transition.md) | accepted batch-002 + Fresh Eyes/model-check evidence | page-fit/split contract, deterministic replay, shadow batch-003 verdict | reusable full-backfill loop |
| 6b | [wave-6b-representative-ingestion-utility](modules/wave-6b-representative-ingestion-utility.md) | historical provider-dependent route | retained input-lock and experiment evidence | superseded by Wave 6f for current backfill |
| 7 | [wave-7-semantic-claims](modules/wave-7-semantic-claims.md) | historical parallel partition route | historical design only | superseded by chronological fold |
| 8 | [wave-8-l2-library](modules/wave-8-l2-library.md) | historical parallel L2 route | historical design only | superseded by chronological fold |
| 9 | [wave-9-context-layers](modules/wave-9-context-layers.md) | complete accepted chronological L2 Wiki + pinned L1/L0 prompts | bottom-up L1/L0 sidecars | finalization |
| 10 | [wave-10-full-build-operations](modules/wave-10-full-build-operations.md) | all stage outputs and receipts | exhaustive coverage, resume/rebuild proof, private build receipt | held-out acceptance |
| 11 | [wave-11-blind-acceptance](modules/wave-11-blind-acceptance.md) | frozen candidate + locked gold | matched correctness/currentness/efficiency verdict | route decision |
| 12 | [wave-12-fresh-agent-handoff](modules/wave-12-fresh-agent-handoff.md) | terminal Wave 11 verdict: accepted route or explicit rejection | clean-session route, rebuild handoff, independent completion audit | завершение |

Wave 6f is the live route override for the frozen current-Wiki backfill. Pending
Wave 6b–9 cards remain historical designs and do not grant or block execution of
the owner-authorized visible Codex/Luna route. Their useful terminal obligations
— layered retrieval, full coverage and matched acceptance — are evaluated only
after the complete L2 Wiki exists; they are not a provider gate before each
chronological batch.

Карточка становится разрешением на исполнение только когда ее dependency gate
закрыт в status.md. До этого это подробная проекция остатка, а не permission
запускать downstream.

## Инварианты волн

- Corpus commit, upstream tuple, prompt/config digests и output topology
  фиксируются до первой записи каждой зависимой волны.
- Root единолично владеет plan/status, shared catalog/index, final manifests,
  интеграцией Worktree commits и публикацией route verdict.
- Root проектирует и собирает связанную систему compiler-а; тяжёлые развилки
  стратегии, архитектуры и acceptance регулярно проверяет Opus. Luna Max
  подключается только после заморозки контрактов к повторяемому преобразованию
  конкретного `part-*` в Wiki; shared файлы и системные решения ей запрещены.
- Модель предлагает grouping, claim и lifecycle candidate. Детерминированный
  слой владеет source membership/provenance; отдельный validator принимает или
  отклоняет semantic output.
- Semantic writer получает только frozen quote records, prompt/schema и
  evidence IDs. Упомянутые в цитатах project files, docs, code и иные знания
  проекта не входят в allowed read surface и не проверяются ради Wiki.
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

- Full chronological backfill идёт только по frozen F1/F2 через новую visible
  Codex Luna task на каждую clean attempt и reusable contract Wave 6f. Batch останавливается
  до записи при missing coverage, unsupported claim, unresolved currentness,
  failed page-fit/split, stale prior digest или deterministic replay mismatch.
- Semantic FAIL отбрасывает весь candidate без repair. Root исправляет один
  versioned prompt owner, меняет SHA и запускает новую Luna с чистым контекстом.
  Два последовательных FAIL одного класса после prompt bump останавливают
  backfill до пересмотра механизма root + Opus; batch N+1 не запускается.
- Representative source-bound input lock можно построить после F1–F3 без
  provider: он не содержит semantic claims, Wiki pages или private quote dump
  и сам по себе не разрешает model execution.
- External semantic provider не получает реальные holders, пока synthetic
  canary не доказал auth, data-egress, logging, retry, cost и
  secret-redaction contract. Этот stop rule не подменяет уже
  разрешённый владельцем local visible Codex route.
- Full-build snapshot не берется из live directory или старого inventory:
  только explicit Git commit и пересчитанный source/record manifest.
- LLM output с отсутствующим record ID, выдуманным provenance, изменённым
  evidence-полем, неподдержанным claim или superseded claim, выданным за
  current, отклоняется, а не чинится молча.
- Wiki page с project-knowledge link, содержанием из прочитанного вне frozen
  quote input или append-only остатком superseded знания отклоняется.
- Никакой size/compression metric не даёт PASS/FAIL и не ограничивает число
  страниц или длину файлов. После полного backfill отношение current Wiki ко
  всему quote corpus записывается только как диагностический результат;
  полноту, полезность и findability доказывает blind audit, а не размер.
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
- Fan-out ограничен реальными независимыми batch-зонами после заморозки единой
  логики. Системный дизайн не дробится между Luna-тредами; их зона —
  повторяемый quote-to-Wiki rewrite по готовому contract.
- Первые два chronological batch прошли structural, source-bound и
  index-first checks. Тем самым закрыто условие раннего owner-decision:
  после успешного pilot запустить full backfill всех holders
  (`_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:25-27`). Parallel
  part writers и merge не возвращаются: retained Luna последовательно
  переписывает current Wiki по десяти holders, а root и non-writing
  auditors держат semantic и terminal acceptance.
- Подробные карточки вытесняют хранение остатка в чате, но не создают второй
  plan owner: task.md владеет outcome и зависимостями, status.md — живым Next,
  modules — неизменяемыми заданиями конкретного момента.

## Происхождение требований

- Раннее решение о маршруте, локальном плане, root-orchestrator, фоновых Luna
  Max-тредах и вложенных субагентах:
  `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.
- Поздняя коррекция в том же holder-е уточняет роли: Luna Max предназначена
  только для понятного повторяемого пересказа цитат в Wiki; связанную систему
  проектирует root, а тяжёлую стратегию и архитектуру чаще проверяет Opus.
- Там же владелец уточнил центральный Wiki contract: страницы ссылаются на
  исходные цитаты, но не на project knowledge corpus и не проверяют упомянутые
  файлы; Wiki — не второй канон. Позднее он уточнил 5–10-кратное сжатие как
  ожидаемый финальный эффект всего backfill, а не условие каждого batch или
  terminal gate.
- Самая поздняя коррекция в том же holder-е полностью сняла ограничения и
  targets на количество страниц и длину файлов. Она оставила генеративный
  пересказ допустимым, но сделала центральным gate запрет чрезмерного
  неподдержанного придумывания.
- Последующая запись того же holder-а задаёт lifecycle: новые цитаты полностью
  переписывают затронутое знание; Wiki хранит только актуальный итог без
  истории, которая остаётся в chat-recall.
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
