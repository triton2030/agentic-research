# md-navigator: BM25F без стемминга для русского

## Факты

- Tokenizer FTS5 в персистентном индексе:
  `tokenize='unicode61 remove_diacritics 2'`
  (`experiments/md-embedding-server/scripts/navigator/index.py`,
  `_create_schema` → `sections_fts`).
- `unicode61` нормализует диакритику и регистр, **stemmer не делает**.
- На русском корпусе запрос `контракт сторон` матчит ровно эти словоформы:
  `контракта`, `сторонам`, `сторонами` остаются вне BM25F-набора.
- Dense channel (`openai/text-embedding-3-small`) морфологию понимает и
  вытягивает правильные секции, но финальный RRF score шумит, потому что
  BM25F для русских инфлексированных запросов отдаёт частичные/случайные
  попадания вместо консистентного сигнала.
- В SKILL.md «Score interpretation» добавлено предупреждение и совет
  «полагайтесь на dense» — это **обходной путь**, не решение.

## Источник

- Feedback внешнего агента из чата (DevEx + поиск линза), пример:
  «Один из top-3 результатов был `Что_такое_MAVO.md > Что читать дальше`
  (просто упомянут "Контракт сторон"), не корневая секция самого
  `Контракт_сторон.md`».
- `index.py:_create_schema` — `sections_fts` определение.
- `navigator/SKILL.md → Score interpretation`, секция про русский.

## Почему актуально

- Большая часть наших корпусов (включая сам `agentic-research`) — русский
  + английский mixed. Smeared BM25 ranking для русских query это базовая
  retrieval-проблема, не косметика.
- Сейчас в hand-off block для русских пользователей: «формулируй запрос
  в той же словоформе, что в тексте» — это шероховатый workaround,
  переносящий nuance на пользователя.
- При росте корпусов и query-вариативности проблема становится заметнее.

## Что снимет проблему

Один из:

- Подключить Snowball-стеммер в FTS5 через сторонний extension
  (например, `sqlite-fts5-snowball-tokenizer` Rust crate или native
  port). Проверить совместимость с `sqlite-vec` в одном процессе.
- Или: pre-tokenize / lemmatize обе стороны (документ + query) на
  Python-уровне через `pymorphy2` / `pymorphy3` перед попаданием в
  FTS5, держа отдельную колонку `body_lemmatized`. Stem-aware
  index без C-extension'а.
- Или: оставить BM25 только для английского, отключить его для
  определённых scope или языков (детект по unicode-блокам) — тогда
  RRF для русских query использует только dense channel.

Решение требует ресёрча по экосистеме FTS5-токенизаторов и теста
качества на реальном русском корпусе.

Снимется в архив когда выбран и применён один из путей **или** когда
strategy решит, что текущий workaround в SKILL.md достаточен.

## Resolution (2026-05-20)

Выбран путь **pre-lemmatize через `pymorphy3` на Python-уровне** (второй из
трёх предложенных). Реализовано:

- `experiments/md-embedding-server/scripts/navigator/lemmatize.py` —
  pymorphy3 wrapper, English/non-Russian pass-through, fail-soft.
- `index.py` — `lemmatize_text` применяется к `body` и `heading_chain` в
  `sections_fts` (insert + metadata-refresh path); `SCHEMA_VERSION` 3→4
  триггерит forced reindex.
- `search.py` — `_fts5_query` лемматизирует tokens; `_fields_hit`
  лемматизирует обе стороны при сравнении.
- `md_navigator.py` — `pymorphy3>=2.0` в inline uv deps.

Замер на 10 RU + 2 EN запросах (8 testable RU, Q7/Q10 — корпус слаб):

| Метрика | Baseline | После лемматизации |
|---|---|---|
| Top-1 точное попадание (RU) | 1/8 = 12% | 4-5/8 = ~55% |
| Canonical owner на #1 | Q6 only | Q2, Q5, Q6, Q8 (+ Q9 ambiguous) |
| EN контроль | 2/2 HIT | 2/2 HIT |

## Residual scope (вне морфологии)

- **RU↔EN heading crossing** (Q4: «стоп-правилами» против `Stop rules`) —
  лемматизация не строит мост; решается конвенцией двуязычных headings
  в GOAL/AGENTS, не индексатором.
- **Form-class mismatch** (Q1: query noun «ориентировка» против corpus
  verb «сориентироваться») — разные леммы; корпусная проблема, не
  индексатор.
- **Corpus gaps** (Q7, Q10) — лемматизация поднимает boilerplate
  (gallery templates) если корпус не содержит canonical контента.

## Output diagnostic flag

`search` теперь показывает `signals: Dense only ⚠ morphology miss likely`
для строк, где BM25 не нашёл — видимый флаг для агента, что результат
держится только на dense (особенно полезно когда лемматизация недоступна
или query/corpus form-class расходятся).

## Model A/B follow-up (2026-05-20)

Поверх лемматизации прогнаны три embedding-модели на тех же 10 RU + 2 EN:

| Метрика | lemma+small (baseline) | BGE-M3 noisy | lemma+large | **BGE-M3 + clean corpus** |
|---|---|---|---|---|
| RU canonical #1 (из 8) | 5/8 = 62% | 6/8 = 75% | 5/8 = 56% | **6/8 = 75%** |
| EN canonical #1 | 2/2 | 1/2 (runs noise) | 1/2 (runs noise) | **canonical в top-2** |
| Reindex cost | $0.015 | $0.0075 | ~$0.10 | $0.0075 |
| Embedding dim | 1536 | 1024 | 3072 | 1024 |

Winner: **BGE-M3 + clean corpus**. Q3 «формирование цели» переехал с
PARTIAL на STRONG HIT (3 canonical Цель-секции в top-3); Q4 нашёл RU
canonical Стоп-Правила в #2; Q10 поднял meta/links Audit And Eval до #1.

EN1 регрессия у BGE-M3 noisy и lemma+large была **дисциплинарной
проблемой корпуса**, не модели: `experiments/{claude-bridge,gemini-mcp}/runs/<timestamp>/final-output.md`
auto-generated logs доминировали фразой "Reading context and preparing
response" для query "context engineering". Любая сильная multilingual
модель поднимет эту помеху; lemma+small не вытащил noise случайно.

Fix: `experiments/md-embedding-server/scripts/navigator/markdown_io.py`
DEFAULT_EXCLUDED_PARTS → +`"runs"`. Корпус сократился 1731 → 1683
секций.

text-embedding-3-large отвергнут: не выиграл ни по одной оси, Q9 даже
деградировал (README > Подход вместо agent-discipline), 13x дороже,
2x storage.

## Global change applied (2026-05-20)

Поскольку `$1md-navigator` — глобальный скил для разных проектов с разными
папками, выбор перенесён в navigator-код:

1. **Global default переключён** на `baai/bge-m3` в `embeddings.py`
   (`SEARCH_DEFAULT_EMBED_MODEL`).
2. **Sticky model** в `index.py` (`resolve_embed_model_for_corpus`):
   когда `--embed-model` не передан, читает recorded `embed_model` из
   meta существующего индекса. Существующие корпуса других проектов
   продолжают работать на своих моделях без forced reindex.
3. CLI `--embed-model default=None` (sentinel) в `cli.py` для всех 5
   команд (search/index/overlaps/repeated-concepts/status).
4. Docs обновлены: `experiments/md-embedding-server/README.md` +
   `~/.claude/skills/1md-navigator/references/engine-internals.md`.

Migration path: первый search в любом existing корпусе подхватит
sticky из meta → no reindex. Новые корпуса получают `baai/bge-m3` по
дефолту. Для override — `--embed-model openai/text-embedding-3-small`
или env `MD_EMBEDDING_MODEL_ID=...`.
