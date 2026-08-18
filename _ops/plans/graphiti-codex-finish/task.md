---
эпик: "самостоятельный experiment: graphiti-codex"
kind: task
---

# Graphiti + Codex — завершение

## Цель

Получить законченный `experiments/graphiti-codex`: stock
`graphiti-core==0.29.3` обрабатывает двухнедельный корпус цитат,
но вместо его API-LLM использует изолированную `gpt-5.6-luna/low`,
а вместо внешних embeddings — локальную модель chat-recall.

Root `_ops/GOAL.md` не владеет runtime-экспериментами; поэтому эта работа
явно помечена как самостоятельный experiment без второй project-wide
карты эпиков.

## Критерии успеха

- Ingest и search идут через штатные `Graphiti.add_episode()` и
  `Graphiti.search()`; custom ontology, свой resolver и свои fact-классы
  отсутствуют.
- Episode содержит штатные message-pairs: `Owner: <quote>` и
  необязательную `Agent: <context-note>`; отдельной архитектуры
  контекста нет.
- Luna получает только Graphiti messages + schema, не имеет tools,
  skills, memory и write-прав и возвращает ровно один schema-valid ответ.
- Одна реальная пара «старая позиция → новая позиция» доказывает
  stock invalidation: current-query не возвращает старое, явный
  historical query возвращает.
- В новую базу загружены все 692 цитаты текущего tracked snapshot за
  2026-08-04..2026-08-18: 667 точных и 25 date-only с детерминированным
  `reference_time` внутри окна соседних sessions; загрузка последовательна,
  но внутренние Luna-turns ограничены пулом.
- Финальный аудит задаёт current и historical вопросы; public output
  не содержит цитат, holder paths, links и episode IDs.

## Не входит

- Tuning или переписывание Graphiti prompts, extraction, resolution, invalidation
  и search recipe.
- Custom ontology, `RECORD_SCOPE`, `record_type`, свои summaries, coverage
  thresholds, saga/receipt/control-plane.
- Параллельные episodes одного owner-corpus и `add_episode_bulk`, потому что
  они ломают последовательную temporal invalidation.

## Происхождение требований

- Только замена LLM provider → владелец,
  `_ops/chat-recall/2026-08-18-151822-codex-01a0145e.md:48`.
- Цитата + необязательный контекст агента в одном episode → владелец,
  `_ops/chat-recall/2026-08-18-151822-codex-01a0145e.md:47`.
- Полный двухнедельный корпус до запросов → владелец,
  `_ops/chat-recall/2026-08-18-151822-codex-01a0145e.md:32`.
- Current не считает вытесненное актуальным → владелец, текущий чат;
  официальные Graphiti `reference_time`, `valid_at`, `invalid_at`.
- Для date-only records порядок важнее времени суток, а реалистичное время
  выводится из окна соседних sessions → владелец,
  `_ops/chat-recall/2026-08-18-151822-codex-01a0145e.md:51-52`.
- Форма episode и custom-надстроек нет → official
  `Adding Episodes`, раздел multi-turn message episodes.
- Выбор границы → записанный ответ owner выше; `agentic-research:P-003`
  не даёт подменить цель локальным усложнением; `P-005` и `P-004`
  сохраняют live proof. Контрось проверена: ни P-001..P-008, ни
  `_ops/GOAL.md` не требуют добавить свою knowledge-architecture.

## Условия входа

- Зафиксирован `graphiti-core==0.29.3`; меняется pinned upstream —
  пересобрать только compatibility boundary.
- Stock Graphiti должен сам извлечь и инвалидировать выбранную
  реальную пару. Если не делает, адаптер не подменяет upstream-семантику:
  полная загрузка останавливается, а предел фиксируется как evidence.

## Режим

Execution. Ось разреза — зависимая цепочка наблюдаемых состояний:
узкая граница → live proof → полная база → query audit. Эта ось материальна:
следующее состояние не имеет смысла без предыдущего.

1. Узкая граница: удалены custom ontology, `RECORD_SCOPE`,
   relation-классы и фильтры; остались LLM/embedder/storage adapters и
   штатные episodes/search.
2. Live proof: lint/tests/doctor + одна реальная temporal пара на свежей
   базе; current/history и public no-provenance output доказаны.
3. Полная база: один последовательный background ingest 692 цитат
   в новую DB через Luna/low; checkpoint служит resume.
4. Query audit: текущие цели, устойчивые предпочтения, точечные
   директивы, изменённая позиция current/history; затем принятая DB становится
   основной experiment-базой.

## Стыки

- Граница adapter → live proof съедобна, когда code diff не содержит
  custom knowledge semantics.
- Live proof → corpus ingest съедобен, когда stock Graphiti инвалидирует
  реальную пару.
- Corpus ingest → audit съедобен, когда episode count равен 692 и нет
  ingest errors.

## Инварианты волны

- Не расширять архитектуру за пределы provider/embedder/storage adapter.
- Не выдавать сырые цитаты и их source addresses в public query.
- Не заменять Graphiti invalidation своим verdict.
