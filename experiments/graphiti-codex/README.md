# Graphiti + Codex

Эксперимент превращает source-bound цитаты владельца в производную временную
базу знаний Graphiti. Дословная цитата, её время и Markdown-адрес остаются
evidence; извлечённый Graphiti-факт — недоверенное производное знание, которое
всегда возвращает к одному или нескольким исходным episodes.

Официально обоснованный метод ingestion и порядок будущих исправлений живут в
[`docs/PROC — Operational Procedure — Graphiti quote ingestion.md`](docs/PROC%20%E2%80%94%20Operational%20Procedure%20%E2%80%94%20Graphiti%20quote%20ingestion.md).

## Граница

- `graphiti-core[falkordblite]==0.29.3`: стабильный upstream без форка;
- embedded FalkorDBLite: локальный файл `.data/graphiti.db`, без Docker и
  отдельного graph server;
- Codex CLI: `gpt-5.6-luna`, reasoning effort `max`, ChatGPT login, JSON Schema,
  ephemeral/read-only вызовы;
- `intfloat/multilingual-e5-small` через FastEmbed: локальные embeddings;
- deterministic pass-through reranker: не создаёт скрытый OpenAI API-вызов;
- Graphiti telemetry выключена до импорта библиотеки.

Это убирает Zep API, `OPENAI_API_KEY`, внешний embedding API и OpenAI reranker.
Но обработка **не offline**: текст цитат уходит в OpenAI через уже
авторизованный Codex/ChatGPT аккаунт. В обычные логи prompt и stderr не пишутся.

Holder-файлы — входной корпус. Одна точная цитата добавляется одним
`add_episode()` и входит в saga своей исходной сессии. `episode_body` хранит
точный текст, `source_description` — путь и строку holder-файла,
`reference_time` — исходную точную дату. Bulk ingestion намеренно не
используется: он не выполняет edge invalidation, необходимую для коррекций
владельца.

## Установка

```bash
cd experiments/graphiti-codex
uv sync --python 3.12
uv run graphiti-codex doctor
```

`doctor` проверяет ChatGPT login, наличие `gpt-5.6-luna/max`, локальную
embedding-модель и embedded FalkorDBLite. Если multilingual E5 уже подготовлен
для `1chat-recall`, эксперимент переиспользует его content-addressed cache.

## Вертикальный проход

Из корня `agentic-research`:

```bash
cd experiments/graphiti-codex
uv run graphiti-codex demo \
  ../../_ops/chat-recall/2026-08-18-151822-codex-01a0145e.md \
  --limit 3 \
  --query "Как владелец хочет превращать цитаты в базу знаний?"
```

Команда сохраняет graph database, печатает извлечённые факты и для каждого
факта — `episodes` с точной цитатой и Markdown-адресом. Повторный ingest того же
record UUID идемпотентно пропускается.

Раздельные команды:

```bash
uv run graphiti-codex ingest HOLDER.md --limit 3
uv run graphiti-codex query "вопрос к базе знаний"
```

## Проверка

```bash
uv run ruff check .
uv run pytest -q
```

Structural tests не доказывают качество Graphiti extraction. Acceptance этого
эксперимента — живой `demo`: не менее одного derived fact, у каждого
`edge.episodes` непуст, каждый episode читается обратно из embedded graph и его
`content`/`source_description` совпадают с настоящим holder-файлом.
