# Evidence — session-context, 2026-08-14

## Реальный корпус

- Backfill-снимок содержал 142 session holder-а и 140 уникальных session ID. Для
  него прочитаны до конца 139 завершённых transcript: 83 Codex rollout и 56
  Claude JSONL; текущая 140-я сессия велась из live transcript.
- После backfill обычный capture создал ещё два holder-а. Финальный corpus
  содержит 144 holder-а и 142 session ID; в каждом holder-е ровно одна
  однострочная `session-context`.
- Две пары duplicate holder-ов получили одинаковую карточку своей общей
  сессии. Исторические quote-records не переписаны: текущий diff 140
  исторических holder-ов меняет только frontmatter; тело меняется лишь у
  текущей сессии через обычный capture.

## Отброшенные маршруты

- Повтор одной file-card в каждом record испортил real-corpus hybrid `hit@5` с
  `0.70` до `0.55`; ablation без карточек вернула `0.70`.
- File-level RRF, складывающий evidence разных quote одной сессии, также дал
  `0.55`: общий файл не означает один общий тезис.
- Card fallback только при полностью пустом record lexical оказался почти
  мёртвым: на 20 pinned queries record-index дал хотя бы одно OR-совпадение во
  всех 20 случаях.

### Historical fallback, superseded 2026-08-17

Следующий контракт и его проверки описывают промежуточный runtime, а не
текущее поведение:

- Карточки не входили в record BM25 или embeddings; одна lexical card на файл
  образовывала отдельный `session_candidates` и включалась только по новому
  query-термину. При пустом `records` тот же маршрут создавал fallback record;
  `--timeline` разворачивал записи выбранных файлов.
- Codex suite: 77 tests, `OK`; Claude suite: 76 tests, `OK`.
- Real mixed queries нашли gold sessions: `skillrouter инструкция`,
  `mantineprovider компоненты`, `skillsbench исследование`.
- Card-only `skillrouter` вернул нужный файл первым и как fallback record, и
  в `session_candidates`.

Текущий контракт отменяет fallback record: card-only default сохраняет
`records=[]`, а найденные файлы живут только в `session_candidates`.

## Проверки

- Pinned 20-query regression после разделения маршрутов: lexical `hit@5=0.30`,
  hybrid `hit@5=0.70`, delta `+0.40`. Общий acceptance-порог `0.90` остаётся
  красным; эта возможность его не маскирует.
- Corpus check показывает 19 прежних diagnostics — duplicate holder и unmarked
  approximate. Число records не заморожено: параллельный обычный capture
  продолжал пополнять corpus во время аудита. `--check --strict` закономерно
  завершается с code 1.

## MAVO Russian-first probe, 2026-08-16

- Корпус: 123 holder-а; 93 metadata-only Russian-first перевода и три
  последующих source-grounded дополнения карточек.
- Слепой evaluator прочитал 20 исходных transcript, не видел
  `session-context` и не запускал retrieval.
- Старые английские карточки: BM25 top-5 3/20; Russian-first: 15/20;
  прежний novel-only gate: 1/20.
- Двухкорневой lexical admission: top-5 16/20 и 0/6 отсутствующих тем.
- E5 внутри admission-tier: тот же top-5 16/20, но точный p10 ухудшился
  с 1-го до 4-го места; поэтому карточный E5 удалён.
- Естественный quote-поиск на трёх свежих случаях дал ранги 6, 23 и 1:
  при `--limit 8` видимы два из трёх.
- В p19 назначенный gold не попал в top-5, но читатель, слепой к gold и
  ranking report, прочитал все пять holder-ов целиком и нашёл три прямо
  релевантных и два смежных. Single-gold остаётся retrieval-прокси, а не
  продуктовой приёмкой.

## Разделение record/file routes, 2026-08-17

- Воспроизводимая blind-20 фикстура:
  `tests/blind_mavo_short2_cases.json`. Её 20 holder-ов были выбраны, а source
  sessions прочитаны в Codex task `01a00846-8a4c-7791-9378-41208c55c0ed` до
  использования `session-context`; фикстура хранит точные natural queries и
  gold-файлы.
- Quote-only file retrieval на одном снимке из 1363 records: стартовый
  `5216879cf24a` и текущий код дали одинаковый hybrid `hit@5=0.60`,
  `hit@1=0.05`, `hit@10=0.65`, `mrr@10=0.271`. Проверка стартового кода
  воспроизводится тем же `evaluate_retrieval.py` через `--digest-script`.
- Pinned agentic-research snapshot 2026-08-17 из 20 queries и 810 records:
  lexical `hit@5=0.30`, hybrid `hit@5=0.70`, `hit@1=0.45`,
  `mrr@10=0.540`; порог `0.70` пройден.
- Текущие suites: Codex 83 tests, Claude 80 tests, оба `OK`. Код runtime и
  его общие тесты между Codex и Claude byte-identical; Codex дополнительно
  владеет corpus-bound evaluator и blind fixture.
- Fresh-agent E2E открыл file-route одним четырёхкорневым повтором, прочитал
  выбранный holder от первой до последней строки и проверил более поздний
  holder. Отдельный natural+root absent-case дважды вернул пустые records,
  пустые session candidates и `selection=none`. Ещё один later-holder check
  обнаружил реальную более позднюю коррекцию Luna → Sol xhigh.

## Full-holder contract candidate, 2026-08-17

Support envelope: isolated Codex subagents, `fork_turns=none`, local tools,
read-only MAVO corpus; `gpt-5.6-sol` / high и `gpt-5.6-luna` / max. Claude:
blocking `claude-opus-5` / xhigh на синтетическом corpus; реальный owner corpus
в Anthropic не отправлялся.

- Sol real-case: top hit нёс вытесненный Luna-default; после полного чтения 12
  holder-ов / 355 строк найдена более поздняя коррекция Sol-default. Обе выдачи
  были `truncated=true`, поэтому абсолютная полнота не заявлена.
- Luna real-case с датированным later-search прочитал 10 holder-ов / 312 строк,
  нашёл ту же коррекцию и вернул `abstain`, потому что поздняя выдача осталась
  усечённой. Это прямой completion-trace честного gap, а не retrieval failure.
- Opus synthetic-case прочитал три holder-а / 10 строк; отдельный later-search
  нашёл решающий holder, отсутствовавший в исходных `records` и
  `session_candidates`. Реальный corpus не читался.

Прогоны подтверждают claim `hit → полный holder → отдельный later-search →
позиция или явный gap`. Они не доказывают полноту ранжирования и не превращают
`truncated=false` одного запроса в доказательство отсутствия скрытой
коррекции.

## Фасетный поиск и сниппет-выдача, 2026-08-18

- Пробы триггеринга голым промтом (fresh subagent, без scaffolding): явный
  recall («что я говорил про карточки сессий») исполнил полный контракт —
  полные чтения, later-search `--since`, честное закрытие capture; неявный
  момент («сократи описание скила 1md-search») скил не поднял — 0 вызовов
  скилов и 0 обращений к корпусу в транскрипте. Счёт 1:1; страховка неявного
  момента у субагентов отсутствует (корневая инструкция их не покрывает).
- Эксперимент погружения «как владелец хочет, чтобы писались файлы»:
  предписанный путь (1 естественный запрос + 1 корневой повтор, limit 8) дал
  13 holder-ов и потерял ≥3 фасета с другой лексикой («дублирование — не
  зло», пределы умного сжатия, язык скила); обе выдачи truncated (matched
  ~60); card-route не открылся речью владельца ни разу. Отсюда фасетный блок
  Retrieval; его behavioral-claim — candidate: один эксперимент на одной
  теме, внешнего случая нет.
- Query-JSON переведён на сниппет `--head` (110): полный текст остаётся в
  holder-файле, `--show` и `--timeline`. Suites: Claude 81, Codex 84, OK.
- Аудит двумя линзами 2026-08-18 (после записи — порядок 6→7/9→10 был
  нарушен, «да» владельца получено на корректировки): сведение четырёх
  носителей «hit ≠ evidence» к одному, порог «втрое» вместо «много больше»,
  смягчение overclaim про file-route, след фасетов перенесён в Завершение,
  дата эксперимента в примере.

## Единый top-10 holder-ов, 2026-08-19

Support envelope: локальный `GPT-5.6`; советник `claude-opus-5` / xhigh через
Claude MCP. Opus получил read-only контекст, но его Bash был запрещён;
численные claims перепроверены локально.

- Opus обнаружил два дефекта прямого суммирования record-ranks: разные лучшие
  BM25/E5-цитаты одного holder-а теряли один канал, а длинный holder занимал
  несколько соседних позиций. Реализация использует file-level MaxP по
  отдельной цитате и только ограниченную поддержку лучшего результата каждого
  канала; число цитат и длина holder-а в score не входят.
- `session-context` допускает holder через lexical gate или совпадение BM25 и
  E5 в top-5. Проверка на pinned 20 queries: пересечение непусто в 9/20
  случаев, поэтому consensus-route не мёртвый. Context-rescue ограничен двумя
  holder-ами и не вытесняет двухканальный quote-hit.
- Pinned agentic-research snapshot: 895 records, 20 queries. Lexical:
  `hit@5=0.30`, `hit@10=0.55`, `coverage@10=0.50`; hybrid: `hit@1=0.40`,
  `hit@5=0.65`, `hit@10=0.75`, `coverage@10=0.75`, `mrr@10=0.50`.
  Промежуточная file-level формула уронила hybrid `hit@10` до `0.65`;
  ограниченная поддержка с весом `0.1` вернула `0.75`, не меняя `hit@5`.
- Retrieval suites: Codex 53 tests, Claude 51 tests; полные package suites:
  Codex 89, Claude 86, все `OK`. Runtime и общие runtime tests byte-identical.
  Новый adversarial test проверяет, что стандартный query возвращает все десять
  полных holder-card даже при выводе больше прежних 8000 символов; явный
  `--max-chars` остаётся opt-in ограничением.
- Живой запрос вернул 10/10 holder-ов, полный `session-context`, относительный
  возраст, type/topic counts и `semantic_rank`; display newest-first, отбор
  остаётся семантическим. Новый vector store не добавлен: context embeddings
  используют тот же E5 и существующий content-hash SQLite cache.
- `sync_simple_projections.py 1chat-recall --check` подтвердил совпадение обоих
  tracked owners и live installs. Установленный Codex runtime повторил тот же
  результат: 10 holder-card, 8461 символ, без character truncation.

Оставшийся предел: `coverage@10` умеет считать несколько полезных holder-ов,
но текущая pinned fixture в основном single-gold; широкую человеческую оценку
многих уместных сессий эти числа не заменяют.

## Контекст чтения top-10, 2026-08-19

- Живой запрос о чтении выдачи вернул newest-first порядок с
  `semantic_rank` `1, 5, 3, 2, 6, 4, 8, 9, 7, 10`: первые четыре строки не
  равны четырём сильнейшим semantic holder-ам. Для вывода полностью прочитаны
  четыре holder-а с рангами 1–4.
- Отдельный запрос о свежести поднял недавний holder с высоким semantic rank,
  но его strongest quote оказалась про восстановление времени Graphiti, а не
  про актуальность owner-позиции. Это прямой случай, где свежесть и rank без
  содержательной связи дают шум.
- Независимый `claude-opus-5` / xhigh audit отклонил процедурные кандидаты:
  первый превратил нижний порог владельца в строгий relevance-гейт, второй
  кодировал алгоритм и выдуманную иерархию типов. Финальный блок оставляет
  контекст двух порядков, глубину три-четыре holder-а, full-holder application
  gate и независимый later-holder check без формулы отбора.
- Изменение только текстовое: ranking, CLI и tests не меняются. Behavioral
  claim ограничен наблюдаемой понятностью контракта и independent audit;
  вероятностный сдвиг поведения отдельным resampling не измерялся.
- Runtime code относительно `HEAD` не изменён; обе live-проекции содержат
  новый контекстный блок, а `sync_simple_projections.py 1chat-recall --check`
  подтверждает совпадение tracked и installed owners. `git diff --check`
  чист; `rumdl` показал только четыре прежних MD013 в фасетном блоке строк
  230/236 двух runtime-копий, новые строки нарушений не добавили.
