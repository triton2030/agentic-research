---
artifact-id: graphiti-codex-proc-quote-ingestion
description: Определяет официально обоснованный способ превращать source-bound цитаты в temporal knowledge graph и безопасно менять интеграцию Graphiti/Codex.
artifact-type: proc
authority: canon
artifact-scope-key: graphiti-codex-quote-ingestion
status: active
approved: false
---

# Graphiti: метод обработки цитат

## Рабочая модель

Graphiti — не новая правда о владельце, а производный temporal Context Graph.
Markdown holder остаётся evidence. Graphiti нужен, чтобы находить сущности,
связи, изменения состояния и затем возвращаться к исходным episodes.

Официальная методика и её локальное следствие:

| Официальный принцип | Следствие здесь |
| --- | --- |
| Context Graph хранит меняющиеся отношения, историю и bi-temporal факты; Graphiti предназначен для одного локального graph на subject. [Overview](https://help.getzep.com/graphiti/getting-started/overview) | Один namespace `owner-quotes`; `valid_at` факта нельзя подменять временем запуска ingestion. |
| Episode — один ingestion event; он обеспечивает point-in-time query и provenance через связи с извлечёнными узлами. [Adding Episodes](https://help.getzep.com/graphiti/core-concepts/adding-episodes) | Holder-файлы — входной корпус, но каждый точный `kind: quote` становится отдельным `EpisodeType.text`: его текст, timestamp и Markdown-адрес не склеиваются с соседями. |
| `group_id` изолирует связный graph и должен участвовать и в записи, и в поиске. [Graph Namespacing](https://help.getzep.com/graphiti/core-concepts/graph-namespacing) | Запись и поиск всегда ограничены `owner-quotes`; иной subject получает другой namespace. |
| Обычный `add_episode` поддерживает изменение/инвалидацию фактов; bulk-путь допустим только для пустого graph или когда edge invalidation не нужна. [Adding Episodes](https://help.getzep.com/graphiti/core-concepts/adding-episodes#loading-episodes-in-bulk) | Цитаты добавляются последовательно по исходному времени. `add_episode_bulk` запрещён: коррекции владельца должны инвалидировать прежние факты. |
| Hybrid search объединяет semantic similarity и BM25; более сложные recipes нужны только под доказанный сценарий. [Searching the Graph](https://help.getzep.com/graphiti/working-with-data/searching) | Сначала `graphiti.search()` по fact edges. Любой возвращённый факт обязан иметь непустой `edge.episodes`, а каждый episode — читаться обратно. |
| Graphiti требует надёжный Structured Output; меньшие модели чаще ломают схему. [LLM Configuration](https://help.getzep.com/graphiti/configuration/llm-configuration) | Luna Max допускается только через строгую JSON Schema, завершённый Codex turn и повторную Pydantic/JSON Schema validation на клиенте. |

## Как Luna должна работать

1. Один Graphiti prompt — один ephemeral Codex turn: `gpt-5.6-luna`, effort
   `max`, sandbox `read-only`, approvals `never`, инструменты запрещены.
2. Все строки Graphiti prompt считаются недоверенными данными. Luna не
   выполняет команды из цитат и возвращает только object заданной схемы.
3. Извлекается только явно сказанное. Нельзя додумывать одобрение,
   постоянство правила или область действия. Временные слова и коррекции
   сохраняются.
4. Ответ принимается только при `turn.completed`, нулевом exit code и двойной
   schema validation. Ошибка или timeout останавливают текущий episode; они не
   превращаются в пустой успешный результат.
5. Вызовы последовательны. После успешного episode его Graphiti UUID
   становится provenance; стабильная source identity хранится в
   `episode.name`, потому что в 0.29.3 новый `add_episode(uuid=...)` падает с
   `NodeNotFoundError` ([upstream issue #1646](https://github.com/getzep/graphiti/issues/1646)).

## Полный проход корпуса

1. Зафиксировать inventory всех `_ops/chat-recall/*.md`, пересекающих окно
   последних 14 дней. Записать cutoff, список файлов и число точных quotes.
2. Парсер принимает только точную ISO-8601 дату с timezone и `kind: quote`;
   `selection`, approximate/unknown records и непонятные строки не попадают в
   graph молча.
3. Сортировать quotes по source timestamp. Для каждого вызвать
   `add_episode()` и дождаться окончания. Quotes одного holder session входят
   в saga `quote-session:<session-id>`.
4. Хранить raw episode content. У episode обязаны совпадать точный текст,
   `source_description=<holder>:<line>` и `reference_time`.
5. Embeddings считать локально через тот же
   `intfloat/multilingual-e5-small`, revision и cache, что использует
   `1chat-recall`. Внешний embedding API не допускается.
6. Возобновление идемпотентно: существующий `episode.name` пропускается только
   если content и source address совпадают; несовпадение — identity collision
   и остановка.
7. После ingestion прогнать минимум четыре вопроса: устойчивое предпочтение,
   поздняя коррекция, связь двух тем, неизвестный факт. Для каждого найденного
   fact проверить непустой provenance и точное чтение source episode.

## Когда остановиться

- Holder изменился после inventory — остановить проход и переснять snapshot.
- Luna не выполняет schema три раза подряд на одном episode — сохранить адрес
  episode и ошибку; не понижать схему и не подставлять пересказ вручную.
- Derived fact не имеет `edge.episodes`, source episode отсутствует или текст
  расходится с Markdown — база непригодна для запросов до исправления.
- Не строить custom ontology и communities до query evidence: это
  необязательные возможности Graphiti, а не часть корректного базового
  ingestion.

## Исправление и обновление

Текущий owner зависимости — `graphiti-core[falkordblite]==0.29.3`, immutable
tag [`v0.29.3`](https://github.com/getzep/graphiti/releases/tag/v0.29.3), commit
`021d3a57d511f21b10adaf7fa923bd5c1fce5e9d`. Перед изменением:

1. Воспроизвести дефект на pinned версии одной минимальной цитатой.
2. Проверить официальный [release log](https://github.com/getzep/graphiti/releases),
   соответствующий tag source и открытые upstream issues. Текущая web-docs
   может описывать более новый `main`, поэтому сама по себе не доказывает
   поведение 0.29.3.
3. Сначала проверить три границы: единственный LLM seam
   [`_generate_response`](https://github.com/getzep/graphiti/blob/021d3a57d511f21b10adaf7fa923bd5c1fce5e9d/graphiti_core/llm_client/client.py#L68-L138),
   lifecycle `add_episode`
   ([pinned source](https://github.com/getzep/graphiti/blob/021d3a57d511f21b10adaf7fa923bd5c1fce5e9d/graphiti_core/graphiti.py#L980-L1111))
   и provenance `EntityEdge.episodes`
   ([pinned source](https://github.com/getzep/graphiti/blob/021d3a57d511f21b10adaf7fa923bd5c1fce5e9d/graphiti_core/edges.py#L263-L282)).
4. Исправлять адаптер, а не форкать Graphiti, пока публичного seam достаточно.
5. Принять изменение только после unit tests, пяти немедленных переоткрытий
   embedded базы и живого episode → fact → exact source прохода.

Команды и актуальный пользовательский вход находятся в `../README.md`; этот
PROC владеет методом и maintenance gates, README их не дублирует.
