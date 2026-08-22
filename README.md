# Agentic Research

`agentic-research` помогает строить систему `skills`, hooks, prompts,
инструкций и рабочих контрактов для агентной среды, которая лучше понимает мой
контекст, действует в меру автономно и не пишет из общего знания, когда есть
локальные знания, критерии и owner-маршрут.

Точный рабочий набор моделей и их роли задаёт `_ops/GOAL.md`. Предыдущие
OpenAI-модели остаются только историческим research evidence, не рабочим
baseline.

## Как Читать

1. `AGENTS.md` — центральная инструкция для обоих агентов: что за репо, карта
   репо с владельцами правды и короткий набор правил этого репозитория. Codex
   читает напрямую, Claude — через `@AGENTS.md`.
2. [`INDEX.md`](INDEX.md) — маршруты, оплаченные прошлым поиском: где лежит
   знание, которое холодный агент стал бы искать не там. Владелец — `1index`.
3. `CLAUDE.md` — shim из одной строки `@AGENTS.md`; отдельной правды не держит.
4. `_ops/GOAL.md` — рабочий контракт проекта: что делаем, что не делаем, когда
   остановиться и вернуться к стратегии.
5. `_ops/product-frames/agentic-research{,.principles}.md` — постоянный
   product-controller для любой содержательной работы. При правке скила к нему
   добавляется `product-frame*.md` из tracked owner-папки скила
   (`skills/shared|claude|codex/<skill>/`); `skills/1<skill>/` — архив истории,
   его Frame не действует.
6. `_ops/chat-recall/` — руда source-bound выдержек слов владельца, файл на
   разговор; пишет `1chat-recall` в момент, когда прозвучало;
   `_ops/user-said/` — его замороженный предшественник, только для чтения.
7. `knowledge/` — wisdom, guides, practical guides, examples и research.
   Для написания скилов начинать с
   `knowledge/practical-guides/how-to-write-skills/`.
8. `science/` — научная программа изучения мышления ЛЛМ: тезисы с
   evidence-статусами, верификация и эксперименты; вход —
   [`science/README.md`](science/README.md).
9. `skills/shared/` — owner cross-runtime packages; `skills/claude/` и
   `skills/codex/` — runtime owners либо их tracked projections согласно
   [`skills/shared/README.md`](skills/shared/README.md). `~/.claude/skills/` и
   `~/.codex/skills/` — installed projections.
10. `_ops/findings/`, `_ops/interviews/`, `_ops/plans/` — временные рабочие
    поверхности; открывать их только когда текущая задача на них указывает.

## Подход

Главный контракт живёт в `_ops/GOAL.md`, а этот README остаётся коротким входом
для человека и свежего агента. Перед содержательной правкой агент сначала
восстанавливает цель, читает локальные owner-файлы и применяет критерии по
типу работы, а не по названию редактируемого файла.
