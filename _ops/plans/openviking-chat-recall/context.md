---
эпик: "самостоятельный experiment: openviking-chat-recall"
kind: context
записано: 2026-08-21
---

# Контекст — почему собственный compiler

## Материальная проблема

`chat-recall` сохраняет точные слова владельца в датированных holders, но это
руда прошлых высказываний, а не готовая текущая картина знаний. Повторы и
поздние коррекции заставляют агента каждый раз заново собирать применимый факт
из многих источников.

Нужная поверхность — не ещё один индекс цитат, а производная библиотека:
актуальные концепты, методы, сравнения и анализ с короткими слоями чтения.
Каждый claim ссылается на исходные цитаты, но Wiki не пересказывает chronology,
count или путь появления знания и не проверяет знания проекта вне цитат.

## Выбранная граница

```text
_ops/chat-recall/**                  immutable source evidence
        ↓ deterministic inventory + typed facts
compiler manifests                  membership / counts / timestamps / provenance
        ↓ semantic resolution + validation
canonical claims + provenance       current knowledge / applicability / quote IDs
        ↓ official Wiki Skill, local batch execution
L2 typed Wiki pages                 final knowledge / quote addresses / internal nav
        ↓ official Context Layers contract + semantic prompts
L0/L1 directory sidecars            bottom-up progressive reading
        ↓ blind retrieval audit
recommended agent route or rejection
```

OpenViking здесь — источник двух проверяемых технологий организации знания, а
не runtime dependency. LLM Wiki Skill владеет semantic page graph и L2; core
Context Layers владеет L0/L1, bottom-up generation и progressive reading. Наш
код владеет snapshot, typed evidence, execution envelope, validators,
resume/rebuild и receipts. Оба upstream owner-а фиксируются отдельно.

## Почему отказались от stock runtime

Три независимые проверки разделили прежнюю гипотезу:

- exact deterministic evidence работает;
- official prompt/IA на typed input дал полезную Wiki для blind reader;
- PyPI SDK, bundled server, VikingBot и Compile не образовали совместимую
  поверхность.

Повторные `⚡ UNEXPECTED` поэтому изменили верхнюю модель: исправлять очередной
SDK mismatch дороже и рискованнее, чем отделить доказанно полезную часть
OpenViking от сломанной инфраструктуры. Владелец явно утвердил это изменение.

Вторая верхнеуровневая коррекция пришла в Wave 4: L0/L1/L2 не являются частью
LLM Wiki Skill. Skill прямо запрещает генерировать `.abstract.md` и
`.overview.md`, потому что в stock-системе ими владеет Compile/runtime. Core
Context Layers отдельно описывает эти sidecars. В custom compiler мы заменяем
runtime, поэтому воспроизводим оба официальных контракта, не смешивая их
provenance.

## Единственная истина и приватность

Wiki никогда не становится владельцем слов пользователя или второй копией
project canon. Она может быть удалена и заново построена из frozen source
snapshot. Claim-запись manifest/receipt перечисляет использованные record IDs,
а Wiki-страница даёт адреса этих цитат. Полные цитаты раскрываются только при
проверке и не копируются во все слои.

Если цитата упоминает документ, код или другое знание проекта, semantic writer
не открывает этот источник и не добавляет найденное содержание. Wiki хранит
только то, что владелец сказал, в максимально сжатой и структурированной форме;
internal Wiki navigation не является ссылкой на project canon.

Хронология принадлежит holders и evidence manifest. Она участвует во
внутреннем выборе актуального claim, но не становится рассказом на
Wiki-странице. `latest` не равно `current`: применимость, отмена и конфликт
требуют semantic judgment, адресуемой опоры и отдельной проверки. После нового
snapshot затронутые страницы переписываются, superseded текст исчезает из Wiki,
а полная история остаётся в holders.

External LLM route до full build обязан явно описать, какие данные покидают
машину, какие секреты используются и как гарантируется отсутствие содержимого
holders в logs/receipts. Если приемлемого route нет, semantic generation не
запускается.

## Проверяемая польза

Гладкая Wiki не является результатом. Итоговая библиотека должна помочь
слепому агенту восстановить актуальное знание не хуже holders, но меньшим
числом чтений или меньшим context. Исторический вопрос должен переводить
агента к исходным holders, а не заставлять Wiki имитировать архив. Exact facts
проверяются кодом; currentness, смысл и удобство — закрытым matched audit с
no-gold и supersession controls.

Размер — cumulative диагностический результат, не gate отдельного batch.
После обработки всего корпуса ожидается, что current Wiki составит примерно
10–20% source quote text: source растёт с каждой новой десяткой, а Wiki
переписывает и объединяет существующие знания. Полезность, полнота и быстрый
поиск имеют приоритет над ratio; меньший объём не заполняется искусственно.

## Переносимые наблюдения

`observations/README.md` — узкий журнал подтверждённых выводов, которые меняют
контракт будущего project-independent compiler. Это не дневник эксперимента:
запись принимается только с direct evidence, границей переноса и объяснением,
какое будущее решение она меняет. Текущий ход, task IDs, локальные имена файлов
и непроверенные идеи остаются в status, returns или `_ops/findings/`.

Root единолично принимает такие записи после независимой проверки returns.
Субагенты могут предложить не более одного candidate observation, но не правят
этот owner.

## Отвергнутые маршруты

- **Ждать stock OpenViking.** Не решает текущий static corpus и связывает
  outcome с недоказанно совместимым runtime.
- **Дать LLM весь корпус одним prompt.** Смешивает точные факты и интерпретацию,
  скрывает пропуски и не даёт возобновляемого build.
- **Сделать только embeddings/search.** Ускоряет нахождение цитат, но не создаёт
  документов дистиллированного знания.
- **Сделать source-by-source summaries.** Дублирует физическую структуру
  holders вместо семантической библиотеки и не экономит сборку знания.
- **Печатать count/first/latest/evolution на каждой Wiki-странице.** Дублирует
  источник и превращает knowledge surface в исторический отчёт. Эти данные
  остаются в manifest/holders и раскрываются только по запросу проверки.
- **Разрешить Wiki-agent читать упомянутые в цитатах project files.** Создаёт
  новое знание из project corpus и превращает производную память слов владельца
  во второй, быстро устаревающий канон.
