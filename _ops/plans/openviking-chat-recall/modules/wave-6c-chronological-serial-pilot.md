---
kind: module-card
wave: "6c"
state: accepted-for-serial-continuation
role: chronological-serial-wiki-pilot
system-owner: root
batch-model: gpt-5.6-luna
batch-thinking: max
---

# Модуль — первый chronological Wiki checkpoint

[parent: task.md](../task.md) · probe после F1–F3 · owner-authorized visible
Codex Luna run на десяти frozen holders

## Contribution

Проверить предложенную владельцем serial topology на реальном первом batch:
одна Luna Max читает десять самых ранних полных holder-файлов, предлагает
типизированный changeset и материализует первый candidate Wiki checkpoint.
Этот probe не разрешает full backfill и не доказывает currentness будущих
batch-ей; он проверяет, можно ли без parallel merge получить компактную,
структурированную и source-bound начальную Wiki.

## Frozen input

Единственный batch manifest —
`experiments/openviking-chat-recall/artifacts/chronological-pilot/batch-001-input.json`.
Он фиксирует commit `6f98fcccdbf4b4de45ef787239ad101f70d106e2`,
ровно 10 holders, 32 records, 0 diagnostics и UTC boundary
`2026-07-26T13:05:18.283000+00:00`.

Holder — неделимая model-input единица. Порядок определяется максимальным
record timestamp holder-а после нормализации naive timestamps как
`Asia/Almaty`, затем `source_path`. Luna получает десять файлов одним batch,
не 32 отдельных вызова.

## Allowed reads

- эта карточка и batch manifest;
- только десять holder blobs из `corpus_commit`, адресованные manifest-ом;
- соответствующие строки frozen
  `artifacts/full-build/evidence/records.jsonl`;
- pinned upstream OpenViking v0.4.16 LLM Wiki Skill по адресу
  `examples/compile/ov-compile-skills/llm-wiki/SKILL.md` и его IA contract.

Project files, docs, code и знания, упомянутые внутри цитат, не открываются и не
используются как semantic source. Project-wide control instructions могут быть
прочитаны только для соблюдения процесса и не становятся Wiki evidence.

## Exact ownership

Один visible `gpt-5.6-luna/max` writer владеет только:

- `experiments/openviking-chat-recall/artifacts/chronological-pilot/batch-001/changeset.json`;
- `experiments/openviking-chat-recall/artifacts/chronological-pilot/batch-001/wiki/**`;
- `experiments/openviking-chat-recall/artifacts/chronological-pilot/batch-001/receipt.json`.

Shared scripts, tests, plans, holders, F1–F3 artifacts и прежние Wiki trees ему
запрещены. Субагенты и parallel writers в этом probe запрещены: проверяется
именно одна последовательная рука.

## Changeset contract

`changeset.json` содержит ordered operations
`create | update | supersede | no-change | reject`. Каждая операция адресует
`operation_id`, `claim_id`, `page_slug`, `page_type`, `source_record_ids`,
`reason`; `update/supersede` дополнительно называют прежний claim/checkpoint.
Для batch-001 допустимы только `create`, `no-change` и `reject`, потому что
предыдущего checkpoint нет.

Отдельный `coverage` содержит ровно одну строку на каждый из 32 record IDs:
`used | rejected | skipped`, reason и один или несколько operation IDs. Silent
skip запрещён. Один record может поддерживать несколько knowledge units, но
имеет ровно один coverage disposition.

## Wiki contract

- Использовать OpenViking page types и navigable `index.md`; пустые типы не
  материализовать.
- Wiki хранит только итоговое знание на boundary batch-001, без рассказа о
  порядке размышлений, first/latest/evolution и без копирования полных цитат.
- Каждая knowledge page перечисляет supporting chat-recall quote addresses;
  internal Wiki links разрешены. Ссылки на project knowledge corpus, URL или
  файлы, упомянутые в цитатах, запрещены.
- Claim не обогащается сведениями, которых нет в allowed quote input. `latest`
  не считается `current` автоматически; uncertainty остаётся видимой.
- Semantic/total chars и ratios измеряются отдельно как baseline diagnostics.
  Per-batch min/max и PASS/FAIL по размеру нет. После всего backfill ожидается
  cumulative Wiki/source ratio 0.10–0.20, но полезность, полнота и быстрый
  поиск не режутся ради этого ожидания; filler запрещён.

## Required receipt

`receipt.json` фиксирует input manifest SHA-256, exact holder/record counts,
time boundary, official prompt source/digest, model, output paths, operation и
coverage counts, semantic/total chars, оба compression ratios, source quote
addresses, gaps и `candidate` status. Quotes, project corpus content и hidden
reasoning в receipt запрещены.

## Root acceptance

Root принимает или отклоняет checkpoint только после проверки:

1. manifest и все десять frozen blob digests совпадают;
2. coverage содержит exact 32 records без missing/extra;
3. Wiki quote addresses входят только в batch membership;
4. project-corpus links, full quotes, history prose и unsupported knowledge
   отсутствуют;
5. каждая страница отвечает на один будущий вопрос и даёт действие/границу;
   отдельный blind reader быстро выбирает её, начиная с `index.md`;
6. per-batch ratio записан только диагностически, а final 5–10× expectation
   не объявлен доказанным до полного corpus;
7. changeset replay создаёт тот же candidate tree или gap честно остаётся
   `UNKNOWN`.

Writer self-report, красивый index и smooth prose не являются PASS. Следующий
batch не запускается до root verdict по batch-001.

## Observed verdict

Владелец одобрил текущий вид четырёх knowledge pages и `index.md`; snapshot
зафиксирован commit `6ab9cb9`. Root независимо подтвердил exact 10 holders,
32 records, 28 `used`, 4 `rejected`, 28 разрешённых source links, отсутствие
Wiki drift от snapshot и `md` без issues. Следующий chronological batch явно
разрешён тому же visible Luna writer. Независимый blind index-first reader
остаётся отдельным findability evidence и не блокирует serial writer.

## Return

Writer возвращает commit SHA, exact changed paths, counts/ratios, validation
commands и gaps. Не меняет `task.md`/`status.md` и не объявляет serial route
принятым для полного корпуса.
