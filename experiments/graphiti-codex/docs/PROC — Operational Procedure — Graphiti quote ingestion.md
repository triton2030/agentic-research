---
artifact-id: graphiti-codex-proc-quote-ingestion
description: Определяет upstream-метод Graphiti 0.29.3 и тонкую локальную границу Codex, embeddings, reranker, FalkorDBLite и явного source reader.
artifact-type: proc
authority: canon
artifact-scope-key: graphiti-codex-quote-ingestion
status: active
approved: false
---

# Graphiti: тонкий adapter

## Рабочая модель

Graphiti — производный temporal Context Graph, а не новая source of truth.
Holder остаётся исходным evidence. Один точный record становится одним
`EpisodeType.message` в документированном формате `Owner: <quote>`; Graphiti сам
извлекает entities и relationships, разрешает
их с существующим graph и хранит temporal facts, связанные с episode через
`edge.episodes`.

Пользовательская база знаний не является складом дословных цитат. Обычный query
возвращает только derived fact fields. Quote text, holder path/address, source
links, `sources` и episode IDs не входят в пользовательский ответ. Их можно
проверить только во внутреннем one-shot validator demo/test.

## Upstream и adapter

| Upstream `graphiti-core==0.29.3` | Adapter |
| --- | --- |
| `add_episode()` и `EpisodeType.message` | Reader holder-файлов; формат `Owner: <quote>` |
| Официальные prompts, extraction, entity/edge resolution и temporal fields | `CodexLLMClient` через `_generate_response` seam |
| `episode.name` и внутренний Graphiti UUID | Source identity в `episode.name`; UUID создаёт Graphiti |
| `Graphiti.search()` и basic `EDGE_HYBRID_SEARCH_RRF` | Namespace `owner-quotes` |
| `CrossEncoderClient` seam | Fail-closed implementation без OpenAI или fake rank |
| Embedder seam | Локальный `intfloat/multilingual-e5-small` через FastEmbed |
| Graph driver | Embedded FalkorDBLite lifecycle |

Adapter не форкает и не переписывает Graphiti extraction, deduplication,
temporal invalidation, episode semantics или search recipes. Вызов
`add_episode()` не получает `custom_extraction_instructions`, custom ontology,
`entity_types` или `edge_types`. Adapter не синтезирует facts и не вводит
coverage-метрики.

## LLM boundary

1. Graphiti формирует официальный список `Message` и response model.
2. Adapter сериализует этот список для одного ephemeral Codex CLI turn. `role` и
   `content` проходят без добавленной adapter-инструкции и без переписывания
   prompt. Output schema передаётся CLI через штатный `--output-schema`.
3. Invocation фиксирован на `gpt-5.6-luna`, reasoning effort `max`, sandbox
   `read-only`, approvals `never`, ephemeral process.
4. Ответ принимается только после `turn.completed`, нулевого exit code и
   повторной Pydantic/JSON Schema validation. Ошибка или timeout остаются
   ошибкой episode; ручной результат не подставляется.

## Explicit source reader

CLI принимает только явно названные holder-файлы и, при необходимости,
стабильные quote UUID/`episode.name` через `--record-id`. Reader:

1. Берёт только строки quote-record с полным ISO-8601 timestamp, временем и
   timezone.
2. Пропускает `kind: selection`, потому что это не episode.
3. При tolerant-чтении пропускает legacy approximate record и печатает его
   address/reason как diagnostic; timestamp не выдумывается. При прямом строгом
   `read_quotes()` такой record остаётся ошибкой.
4. Сортирует выбранные exact records по source timestamp.

Reader не строит corpus inventory, не сканирует не переданные holders, не создаёт
window/count/hash manifest и не управляет retry/progress receipt.

## Episode ingestion

Для каждого выбранного record adapter последовательно ожидает один stock
`Graphiti.add_episode()` с:

```text
name=stable source identity in episode.name
episode_body=Owner: <exact quote text>
source_description=holder address
reference_time=source timestamp
source=EpisodeType.message
group_id=owner-quotes
```

`saga`, custom instructions и custom ontology не передаются. Graphiti сам
создаёт внутренний episode UUID и сам владеет extraction/resolution/temporal
behavior. Повторный ingest читает существующие episodes по `episode.name`:
совпавшие content/address дают `skipped_existing`, collision останавливает
операцию с точным адресом ошибки.

`reference_time` — время исходной цитаты, не время ingest. Поздний episode не
заменяет и не удаляет ранний. Когда штатная resolution распознаёт изменение той
же связи, прежний derived edge получает `invalid_at`, новый — `valid_at`; оба
source episodes сохраняются. Если relation не извлечена или противоречие не
разрешено к той же связи, один лишь более поздний timestamp ничего не отменяет.

Успешный operational результат содержит только `added_count`,
`skipped_existing_count` и `derived_facts_count`. Source address появляется
только в diagnostics или collision/error, не в успешном knowledge output.

## Search boundary

Обычный query вызывает:

```python
graphiti.search(query, group_ids=["owner-quotes"], num_results=limit)
```

Это штатный basic `EDGE_HYBRID_SEARCH_RRF` Graphiti. Adapter сериализует
`EntityEdge` только в:

```json
{
  "kind": "derived_fact",
  "fact": "...",
  "valid_at": "...",
  "invalid_at": "..."
}
```

Обёртка CLI содержит query и список facts, но не содержит raw quote, path,
source link, `sources` или episode ID.

Basic RRF search не вызывает `CrossEncoderClient.rank`. Adapter всё равно
передаёт fail-closed implementation, чтобы другой search recipe не сделал
неявный OpenAI-вызов и не получил фальшивый порядок: такой вызов завершается
явной ошибкой. Это не меняет stock basic search.

## Private live validator и gates

Demo/test может после stock search один раз пройти `edge.episodes` через
`EpisodicNode` и проверить только provenance integrity: episode UUID существует,
его content/address/time совпадают с поданным record. Validator не оценивает
форму или «качество пересказа» fact и не добавляет пользовательские поля.

Acceptance adapter:

- `uv run ruff check .`;
- `uv run pytest -q`;
- `uv run graphiti-codex doctor`;
- пять немедленных reopen cycles embedded database;
- свежий live vertical на 1–3 records через stock `add_episode` и stock `search`;
- public JSON без provenance и private test на сохранённый `edge.episodes`.

Полный corpus намеренно не загружается до этого acceptance. После него он
остаётся следующей операцией исходной пользовательской цели и запускается тем
же явным последовательным ingest выбранных holder-файлов и record IDs, без
добавления отдельной corpus-системы/control plane в adapter.

## Upstream reference

- [Graphiti overview](https://help.getzep.com/graphiti/getting-started/overview)
- [Adding episodes](https://help.getzep.com/graphiti/core-concepts/adding-episodes)
- [Graph namespacing](https://help.getzep.com/graphiti/core-concepts/graph-namespacing)
- [Searching the graph](https://help.getzep.com/graphiti/working-with-data/searching)
- [Pinned v0.29.3](https://github.com/getzep/graphiti/releases/tag/v0.29.3)
- [Pinned `add_episode` source](https://github.com/getzep/graphiti/blob/021d3a57d511f21b10adaf7fa923bd5c1fce5e9d/graphiti_core/graphiti.py#L980-L1111)
- [Pinned `EntityEdge.episodes`](https://github.com/getzep/graphiti/blob/021d3a57d511f21b10adaf7fa923bd5c1fce5e9d/graphiti_core/edges.py#L263-L282)
