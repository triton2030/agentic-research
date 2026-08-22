---
эпик: "самостоятельный experiment: openviking-chat-recall"
режим: Execution
kind: task
создано: 2026-08-21
пересобрано: 2026-08-22
---

# Библиотека знаний из chat-recall

## Цель

Полностью преобразовать frozen snapshot `_ops/chat-recall/` в удобную агентам
библиотеку актуальных знаний по OpenViking IA. Исходные holders остаются
неизменяемым evidence и историей; Wiki — удаляемая и воспроизводимая проекция
того, что владелец сказал, решил, предпочёл, предложил или оставил
неопределённым.

Готовый результат содержит полный L2 Wiki, bottom-up L1/L0, deterministic
manifests/receipts и blind-доказательство, что агент находит актуальное знание
не хуже, чем в holders, при меньшем числе чтений или context cost.

## Текущие владельцы

| Смысл | Единственный owner |
| --- | --- |
| Семантика Wiki writer-а | `experiments/openviking-chat-recall/prompts/wiki-writer.v2.md`; v1 остаётся rejected history |
| Полный контракт и путь до конца | этот `task.md` |
| Зачем выбран маршрут | `context.md` |
| Текущий frontier | `status.md` |
| Прошлые решения и эксперименты | `HISTORY.md` |
| Frozen evidence | `experiments/openviking-chat-recall/artifacts/full-build/frozen/` и `experiments/openviking-chat-recall/artifacts/full-build/evidence/` |
| Manifest/preflight | `experiments/openviking-chat-recall/scripts/build_owner_wiki_batch.py` |
| Mechanical validation/materialization | `experiments/openviking-chat-recall/scripts/materialize_chronological_changeset.py` |
| Единственная текущая Wiki chain | `experiments/openviking-chat-recall/artifacts/chronological-v1/` |

`modules/**` и `artifacts/chronological-pilot/**` — addressable historical
evidence. Они не управляют новой работой и не являются semantic prior.

## Система

```text
frozen chat-recall holders
        ↓ deterministic chronological slice
10 новых holders + их evidence records
        ↓ Luna Max по versioned prompt
candidate changeset над current Wiki
        ↓ mechanical check + independent semantic audit
accepted materialized current Wiki
        ↓ повторить до полного L2 corpus
bottom-up L1/L0
        ↓ coverage/rebuild + blind matched audit
recommended agent route или честный FAIL
```

### Что читает writer одного batch

Batch `N` получает только:

1. versioned prompt, manifest, output contract и preflight;
2. следующие десять целых frozen holder-файлов и только их evidence rows;
3. `index.md` и потенциально подходящие страницы принятой current Wiki.

Writer не читает прежние holders, прежние quotes и targets старых source
links. Current Wiki уже является сжатым prior knowledge. Deterministic builder
передаёт page SHA, prior record IDs и готовые source-link targets, необходимые
для сохранения provenance без повторного чтения старых цитат.

Project instructions и named owner contracts относятся к control plane. Они не
являются Wiki evidence, не растут вместе с номером batch и не разрешают broad
historical recall scan. До batch-002 read-set audit обязан доказать границу:
`10 новых holders + current Wiki`, а не `все обработанные holders`.

### Что пишет writer

- только `batch-NNN/changeset.json` со статусом `candidate`;
- complete proposed Markdown для `create/update`;
- claims ledger до prose, exact coverage и repetition/conflict metadata;
- ни current Wiki, ни receipt, ни Git state.

Каждая material surface — type/path, title/H1, description, body, source label,
coverage reason и index cue — сохраняет owner attribution, subject, scope,
modality и relations. Wiki пишет по-русски от третьего лица и не превращает
owner quote в объективный факт или универсальный императив.

Тематическая близость record-а к странице не считается page fit: каждый `used`
record прямо отвечает точному H1. Named skill/project/runtime и
`кандидат | идея | вопрос | правило` не обобщаются и не усиливаются на соседних
surfaces. `first/latest` repetition IDs вычисляет deterministic слой в manifest
order; writer их не угадывает. Reject reason проверяется по полному holder
context, а не по одной строке quote.

### Как проходит один batch

1. Root строит manifest и preflight; hashes и prior tree проверяются до Luna.
2. Новая visible `gpt-5.6-luna/max` получает один bounded batch без worktree.
3. Luna читает разрешённые inputs, пишет candidate и запускает только
   deterministic `--check-only`.
4. Root/Opus независимо проверяет source → claim → все page surfaces → index.
5. FAIL отбрасывает candidate целиком. Root исправляет versioned prompt или
   deterministic contract и запускает новую Luna с нуля; repair того же
   candidate запрещён.
6. PASS меняет status candidate → accepted; deterministic materializer пишет
   exact Wiki/receipt. Root проверяет tree/coverage, коммитит и пушит checkpoint.
7. Root обновляет `status.md`, при изменении системы — `task.md/context.md`, и
   архивирует завершённую visible task.
8. Только accepted checkpoint становится prior следующего batch.

Batch-агенты работают последовательно. Параллельные writers по разным эпохам и
merge их Wiki запрещены: более новая цитата может переписать уже созданное
знание.

Новый record, который добавляет или меняет claim принятой страницы, обязан
быть виден в answer-body, а не только в `description`, `## Источники` или
metadata. Рост provenance без body-delta допустим только для доказанного
семантического повтора уже выраженного current knowledge; validator фиксирует
этот случай отдельно. Первый непустой `update/no-change` в batch-002 обязан
пройти этот falsifying gate до продолжения backfill.

## Критерии успеха

- Все 184 frozen holders адресованы: 183 record-bearing обработаны ровно один
  раз, один no-record holder учтён без выдуманного содержания; все 1101 records
  имеют `used | reject | skipped` disposition.
- Writer каждого batch читает только его десять новых holders/records и current
  Wiki; прежние quotes не перечитываются.
- Wiki использует OpenViking `index | entity | concept | method | comparison |
  analysis`; `entity/concept` — default, остальные типы проходят полный test.
- Страница отвечает на один естественный retrieval-вопрос. Соседняя тема
  получает другую страницу или named split.
- Wiki хранит только актуальный поддерживаемый итог. Дубли схлопываются;
  genuinely newer correction того же subject/scope переписывает старое знание.
  История и точные даты остаются в holders/evidence metadata.
- В Wiki есть exact links только на chat-recall citations. Project files,
  внешние источники и содержание упомянутых документов не исследуются и не
  добавляются.
- Нет hard limits на число/длину страниц или compression ratio. Финальное
  сжатие измеряется только как diagnostic.
- Complete L2 получает bottom-up L1 `.overview.md` и L0 `.abstract.md` по
  pinned OpenViking Context Layers contract; L2 writer не пишет sidecars.
- Fresh rebuild из frozen sources byte-identical по deterministic surfaces;
  crash/resume/delete-rebuild и privacy boundaries имеют receipts.
- Blind index-first audit на frozen questions и matched Wiki-vs-holders
  comparator подтверждают currentness, provenance, findability и reading cost.
- Fresh agent по одной этой triad восстанавливает следующий шаг и не открывает
  `HISTORY.md`/`modules/**` как current instruction.

## Вехи

| № | Веха | Готово, когда |
| --- | --- | --- |
| 1 | Надёжный batch-механизм | clean batch-001/002/003 приняты без repair; bounded read set доказан; prompt/manifest/materializer contract стабилен |
| 2 | Полный L2 backfill | все record-bearing holders последовательно обработаны, exact coverage и один current Wiki checkpoint |
| 3 | L1/L0 layers | sidecars созданы bottom-up по полному L2 и проходят provenance/structure gates |
| 4 | Operations proof | fresh rebuild, resume/crash/delete-rebuild, coverage и privacy receipts проходят |
| 5 | Retrieval acceptance | blind matched comparator и fresh-agent handoff дают PASS либо библиотека явно отклонена |

После accepted batch-002 проводится ранний matched-budget comparator только на
первых двадцати holders. Он не заменяет финальную приёмку полного корпуса, но
fail-closed останавливает дорогой backfill, если Wiki ещё не показывает
deduplication/currentness/findability benefit.

## Не входит

- установка stock OpenViking runtime или ожидание ремонта SDK;
- realtime watcher, WebDAV, Graphiti backfill или публикация цитат наружу;
- изменение, удаление или переформатирование исходных holders;
- проектный knowledge canon внутри Wiki;
- page-per-source summaries, chronology report или полные цитаты в prose;
- параллельная генерация эпох и merge нескольких Wiki trees;
- ручное исправление rejected candidate.

## Условия входа и stop rules

- Corpus/evidence остаются pinned к commits
  `6f98fcccdbf4b4de45ef787239ad101f70d106e2` и
  `ea569e2bf84377b17be9177065d5fb9172d26d39`; silent `HEAD` fallback запрещён.
- Два последовательных FAIL одного semantic класса после prompt bump
  останавливают full backfill и возвращают механизм в Wayfinding.
- Любой batch, который требует перечитать старые holders, останавливается до
  ремонта prior-page bindings или изоляции writer package.
- Missing prompt/input/prior hash, partial candidate или materialization до
  independent acceptance — fail closed.
- Если blind audit не показывает пользы против holders, Wiki не становится
  рекомендуемым agent route, даже при полном build.

## Стыки

- Accepted batch receipt → input следующего manifest только после commit SHA.
- Полный accepted L2 tree → единственный вход L1/L0 compiler.
- Frozen L2/L1/L0 + coverage/rebuild receipts → единственный вход blind audit.
- Blind verdict + fresh-agent handoff → terminal решение: recommend или reject.

## Происхождение требований

- Owner model Wiki, chronological batches, Luna role, source/project boundary,
  current-only rewrite, отсутствие size gates, third-person attribution,
  автономность, bounded prior reading и documentation refactor:
  `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md:35-73`.
- Неизменяемость holders и source-bound evidence: `_ops/AGENTS.md`.
- OpenViking L2 page model: pinned upstream v0.4.16 LLM Wiki Skill, digest
  записан в `wiki-writer.v1.md`.
- L1/L0 ownership: pinned OpenViking Context Layers sources, которые фиксирует
  веха 3 до generation.

## Principles trace

Владелец прямо потребовал чистую текущую систему и отдельную историю. Из
вариантов «добавить новые owners» и «пересобрать существующую triad» выбран
второй: `agentic-research:P-007` запрещает параллельную правду, P-003 требует
устранить реальное navigation friction, P-004/P-005 требуют cold-start и
исполняемых gates. Исторические modules сохранены как evidence, но больше не
управляют маршрутом.
