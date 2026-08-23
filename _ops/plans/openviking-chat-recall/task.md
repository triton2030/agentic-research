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
| Семантика пофайлового сжатия (маршрут Б) | `experiments/openviking-chat-recall/prompts/flatten-file.v1.md` |
| Семантика сборки страниц (маршрут A) | `experiments/openviking-chat-recall/prompts/wiki-writer.v4.md`; v1–v3 — rejected history |
| Проверка формы вики | `experiments/openviking-chat-recall/scripts/check_wiki.py` |
| Полный контракт и путь до конца | этот `task.md` |
| Зачем выбран маршрут | `context.md` |
| Текущий рубеж | `status.md` |
| Прошлые решения и отклонённые кандидаты | `HISTORY.md` и `artifacts/chronological-v1/batch-001/attempt-*/REJECTED.md` |
| Сухое знание пофайлово | `experiments/openviking-chat-recall/artifacts/flatten-v1/flat/` |
| Атомарность, история, откат | git: один шаг — один коммит |

`modules/**`, `artifacts/chronological-pilot/**` и весь слой changeset /
manifest / materializer — addressable historical evidence. Они не управляют
новой работой.

## Система

Два маршрута к одной цели; сравниваются на одном корпусе.

```text
197 файлов цитат  (неизменны)
        |
        |  маршрут Б, шаг 1: пофайлово, параллельно
        v
197 файлов сухого знания              <- выполнено, 2,75x
        |
        |  шаг 2: объединение по схожести темы
        v
крупные тематические файлы
        |
        |  маршрут A на чистом материале: сборка страниц
        v
вики по IA OpenViking + index
        |
        v
blind matched audit -> рекомендуемый маршрут агента либо честный отказ
```

Работа «не исказить сказанное» и работа «решить, как разложить» разведены по
шагам. Четыре кандидата маршрута A показали, что одновременно они не даются:
механизм качается между смешиванием вопросов и дроблением страниц.

### Как идёт один шаг

1. Root готовит вход: список файлов, контракт, границы.
2. Исполнитель — `gpt-5.6-luna/max` для переноса и прозы, `gpt-5.6-sol/xhigh`
   для суждения — пишет только в свою выходную папку.
3. Root кладёт результат на место сам; модель файлов проекта не трогает.
4. `check_wiki.py` судит форму, независимый аудит на `sol` — смысл.
5. Годно — коммит. Негодно — `git checkout` и правка контракта, не результата.

Параллельность допустима там, где шаг не требует общего контекста: пофайловое
сжатие гналось двадцатью прогонами. Сборка страниц последовательна по природе.

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
| 1 | Пофайловое сухое знание | 196 файлов переписаны, имена один в один, модальность из ярлыка, баланс вход/выход посчитан — **выполнено** |
| 2 | Тематические объединения | файлы сгруппированы по схожести предмета; провенанс слияния чист по `check_topics.py` — **выполнено** |
| 3 | Вики по IA OpenViking | страницы и указатель собраны, `check_wiki.py` зелёный без исключений |
| 4 | Полнота и смысл проверены | `check_coverage.py` не оставляет записи без судьбы; аудит смысла закрыт, правки применены |
| 5 | Retrieval acceptance | слепое сравнение с исходными разговорами даёт PASS либо библиотека явно отклонена |
| 6 | Переносимость | протокол по `RUNBOOK.md` применён к чужой папке `_ops/chat-recall` **без правки своего текста** |

Веха 6 добавлена 2026-08-23 по словам владельца: «У меня есть другие проекты с
такими же чат папками и вот там подобные библеотекки сжатой и структурированной
ифномрации очень помогли бы» и «мы потом это зафиксируем как рабочий протокол
чтобы делать и другие библиотеки для других проектов»
(`_ops/chat-recall/2026-08-22-140532-claude-efb50744.md`). Она же — условие
превращения протокола в скил, записанное в самом протоколе.

Прежняя веха «Operations proof» снята: её половина про квитанции удаления и
восстановления принадлежала слою заявки, который владелец снял 2026-08-22, а
откат и историю даёт git (инвариант 8). Половина про пересборку из источников
вошла в веху 6: конвейер стал скриптами, и пересборка теперь проверяется
применением к чужому корпусу.

## Не входит

- установка stock OpenViking runtime или ожидание ремонта SDK;
- realtime watcher, WebDAV, Graphiti backfill или публикация цитат наружу;
- изменение, удаление или переформатирование исходных holders;
- проектный knowledge canon внутри Wiki;
- page-per-source summaries, chronology report или полные цитаты в prose;
- параллельная генерация эпох и merge нескольких Wiki trees;
- ручное исправление rejected candidate.

## Условия входа и stop rules

- Исходные файлы `_ops/chat-recall/` неизменны; всё производное пересобираемо.
- Модель не пишет в файлы проекта: результат кладёт root.
- Два последовательных провала одного семантического класса после правки
  контракта останавливают маршрут и требуют сменить не формулировку, а
  разложение работы. Маршрут A остановлен по этому правилу после четырёх
  кандидатов.
- Параллельность разрешена только там, где шаг не требует общего контекста.
- Если аудит не показывает пользы против исходных файлов, библиотека не
  становится рекомендуемым маршрутом агента даже при полной сборке.

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
