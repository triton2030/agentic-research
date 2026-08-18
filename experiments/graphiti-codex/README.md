# Graphiti + Codex

Тонкий локальный adapter для `graphiti-core==0.29.3`: явные source-bound
records превращаются в штатные Graphiti message episodes, а query возвращает derived
fact layer. Holder остаётся исходным evidence; он не выдаётся как knowledge
answer.

Методическая граница описана в
[`docs/PROC — Operational Procedure — Graphiti quote ingestion.md`](<docs/PROC — Operational Procedure — Graphiti quote ingestion.md>).

## Upstream и adapter

| Upstream Graphiti 0.29.3 | Локальный adapter |
| --- | --- |
| `add_episode()` и `EpisodeType.message` | Чтение holder-файлов; формат `Owner: <quote>` |
| Официальные prompts, extraction, entity/edge resolution и temporal fields | `CodexLLMClient` через официальный `_generate_response` seam |
| `episode.name` и внутренний Graphiti UUID | Stable source identity в `episode.name`; UUID создаёт Graphiti |
| `Graphiti.search()` и stock `EDGE_HYBRID_SEARCH_RRF` | Namespace `owner-quotes` |
| `CrossEncoderClient` seam | Fail-closed client: не вызывает OpenAI и не подделывает rank |
| Graph driver lifecycle | Embedded FalkorDBLite database under `.data/` |
| Embedder seam | Локальный `intfloat/multilingual-e5-small` через FastEmbed |

Graphiti сам владеет prompts, extraction, deduplication, temporal invalidation и
search recipes. Adapter не передаёт `custom_extraction_instructions`, custom
ontology или entity/edge types, не синтезирует facts вручную и не вводит
coverage thresholds.

## Ожидаемый эффект Graphiti

После последовательного ingest внутри графа остаются исходные message episodes,
а Graphiti автономно строит entity nodes и time-stamped relationship facts.
Поздние сообщения могут инвалидировать прежние связи, не удаляя историю.
Обычный `search()` объединяет semantic similarity и BM25 через штатный RRF и
возвращает найденные facts. Это не обещание пересказать каждую строку: фраза,
из которой Graphiti не извлёк relation, может остаться только episode.

Graphiti messages сериализуются для Codex без добавленной adapter-инструкции:
исходные `role` и `content` сохраняются. Codex запускается как
`gpt-5.6-luna`, reasoning effort `max`, ephemeral, read-only, approvals never;
response schema валидируется и CLI, и локальным Pydantic.

## Reranker boundary

Публичный query использует `Graphiti.search()` — штатный basic
`EDGE_HYBRID_SEARCH_RRF`. Этот рецепт не вызывает `CrossEncoderClient.rank`.
Поэтому adapter передаёт Graphiti fail-closed client: если другой код выберет
cross-encoder recipe, он остановится с явной ошибкой вместо внешнего OpenAI
вызова, тяжёлой модели или pass-through ранжирования. Это не изменение basic
search algorithm.

## Установка

```bash
cd experiments/graphiti-codex
uv sync --python 3.12
uv run graphiti-codex doctor
```

`doctor` проверяет ChatGPT login, наличие `gpt-5.6-luna/max`, локальные
embeddings, fail-closed reranker seam и embedded FalkorDBLite. Codex inference
не offline: episode content отправляется через уже авторизованный Codex/ChatGPT
аккаунт. Внешний embedding API и OpenAI reranker не используются.

## Малый live vertical

До любой полной загрузки корпуса запускается свежий проход на 1–3 явных
records:

```bash
uv run graphiti-codex demo \
  ../../_ops/chat-recall/2026-08-18-151822-codex-01a0145e.md \
  --limit 3 \
  --query "Как владелец хочет превращать цитаты в базу знаний?" \
  --database .data/small-vertical.db
```

Команда последовательно вызывает stock `add_episode`, затем stock `search`.
Каждая точная реплика передаётся как документированный conversational message
`Owner: <quote>`, чтобы субъект оставался явным без custom prompt или ontology.
Она делает one-shot private provenance check и падает при отсутствии
`edge.episodes` или несовпадении episode content/time,
но stdout содержит только operational counts и public facts.

Повторный ingest той же source identity в `episode.name` идемпотентно
пропускается. Совпавшие content и source address обязательны; collision —
ошибка. Graphiti UUID не используется как record identity.

`reference_time` всегда равен времени самой цитаты. Более поздний episode не
переписывает ранний: если Graphiti распознаёт обновление той же связи, он
оставляет оба episodes, а прежнему derived fact назначает `invalid_at` и создаёт
новый fact со своим `valid_at`. Простая хронологическая близость сама по себе не
означает отмену.

## Явный ingest и query

```bash
uv run graphiti-codex ingest HOLDER.md --limit 3 --database .data/graphiti.db
uv run graphiti-codex ingest HOLDER.md --record-id <quote-uuid>
uv run graphiti-codex query "вопрос к базе знаний" --database .data/graphiti.db
```

`query` возвращает для каждого результата только `kind`, `fact`, `valid_at` и
`invalid_at` (в обёртке результата — сам query и список `facts`). В нём нет raw
quote, Markdown path/address, source link, `sources` или episode IDs. Private
проверка живёт только внутри demo/tests и не является query API.

Approximate record без полного времени и timezone не ingest-ится. При tolerant
чтении явного holder он пропускается с machine-readable address/reason; точный
timestamp не выдумывается. `kind: selection` также не является quote episode.

## Проверка

```bash
uv run ruff check .
uv run pytest -q
uv run graphiti-codex doctor
```

Acceptance этой тонкой границы — unit tests, пять немедленных reopen cycles
embedded database и свежий live episode → derived fact → private provenance.
Полный корпус остаётся следующей операцией исходной пользовательской цели после
этого acceptance. Он запускается тем же явным последовательным ingest выбранных
holder-файлов и record IDs; отдельная corpus-система/control plane для этого не
добавляется.
