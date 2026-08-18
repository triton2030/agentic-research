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
| `add_episode()` и `EpisodeType.message` | Чтение holder-файлов; `Owner: <quote>` + optional `Agent: <context>` |
| Официальные prompts, extraction, entity/edge resolution и temporal fields | `CodexLLMClient` через официальный `_generate_response` seam |
| `episode.name` и внутренний Graphiti UUID | Stable source identity в `episode.name`; UUID создаёт Graphiti |
| `Graphiti.search()`, `SearchFilters` и stock `EDGE_HYBRID_SEARCH_RRF` | Namespace `owner-quotes`; explicit current/as-of view |
| `CrossEncoderClient` seam | Fail-closed client: не вызывает OpenAI и не подделывает rank |
| Graph driver lifecycle | Embedded FalkorDBLite database under `.data/` |
| Embedder seam | Локальный `intfloat/multilingual-e5-small` через FastEmbed |

Graphiti сам владеет prompts, extraction, deduplication, temporal invalidation и
search recipes. Adapter не передаёт custom ontology или extraction instruction,
не синтезирует facts и не добавляет собственный resolver.

## Ожидаемый эффект Graphiti

После последовательного ingest внутри графа остаются исходные message episodes,
а Graphiti автономно строит entity nodes и time-stamped relationship facts.
Поздние сообщения могут инвалидировать прежние связи, не удаляя историю.
Обычный `search()` объединяет semantic similarity и BM25 через штатный RRF.
Публичный query дополнительно передаёт штатный temporal `SearchFilters` и
возвращает только facts, действующие в один явно названный момент. Это не
обещание пересказать каждую строку: фраза, из которой Graphiti не извлёк
relation, может остаться только episode.

Если у quote-record есть `context-note`, он передаётся рядом второй штатной
message-парой `Agent: <context>`. Это обычный episode body, а не отдельная
архитектура, metadata scope или источник вручную созданных facts.

Graphiti messages сериализуются для Codex без добавленной adapter-инструкции:
исходные `role` и `content` сохраняются. Codex запускается как
`gpt-5.6-luna`, reasoning effort `low`, ephemeral, read-only, approvals never.
Shell, memory, apps, browser/computer и остальные workspace-tools явно
отключены, а каталог skills не добавляется в model context: один Graphiti call
может дать только один terminal schema-answer;
response schema валидируется и CLI, и локальным Pydantic.

Episodes ingest-ятся строго последовательно: следующий `add_episode()`
начинается только после полного завершения предыдущего, поэтому видит его
entities, edges и invalidation. Внутри одного episode Graphiti штатно запускает
независимые extraction/resolution операции через `semaphore_gather`; adapter
разрешает не более четырёх одновременных Luna turns. Параллельные episodes
одного `group_id` и `add_episode_bulk` не используются.

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

`doctor` проверяет ChatGPT login, наличие `gpt-5.6-luna/low`, локальные
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
Каждая реплика передаётся как документированный conversational message
`Owner: <quote>`; необязательный контекст — следующей парой `Agent: <context>`.
Custom prompt и ontology не добавляются.
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
uv run graphiti-codex query "что было актуально раньше?" \
  --as-of 2026-08-10T12:00:00+05:00 \
  --database .data/graphiti.db
```

Без `--as-of` query фиксирует текущее время. Он использует официальный temporal
filter `(valid_at <= as_of OR NULL) AND (invalid_at > as_of OR NULL)` и повторно
проверяет каждый edge перед публичным ответом. Поэтому fact, который Graphiti
уже пометил `invalid_at`, не может попасть в текущий ответ; исторический ответ
возможен только через явный `--as-of`.

`query` возвращает `as_of`, а для каждого результата — только `kind`, `fact`,
`valid_at` и `invalid_at`. В нём нет raw quote, Markdown path/address, source
link, `sources` или episode IDs. Private проверка живёт только внутри
demo/tests и не является query API.

Граница гарантии: temporal filter защищает от уже инвалидированных facts. Если
штатная Graphiti resolution не распознала две реплики как изменение одной
relation и не выставила `invalid_at`, adapter не подменяет это собственной
семантикой.

Date-only record получает `reference_time`, равномерно интерполированный между
временем предыдущего и следующего известных session-файлов. Если одной границы
нет, используется граница календарного дня `Asia/Almaty`. Исходный holder не
переписывается, порядок строк сохраняется, а operational event явно помечает
такую метку как `record.approximated`. Timed record без timezone остаётся
ошибкой. `kind: selection` не является quote episode.

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
