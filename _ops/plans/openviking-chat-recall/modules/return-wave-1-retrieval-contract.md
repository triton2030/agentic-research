---
kind: module-return
волна: 1
роль: independent-reviewer
thread-id: 01a023c3-ee43-7c73-964a-08b22a2d1b17
состояние: locked
записано: 2026-08-21
---

# Return — locked retrieval contract

Reviewer зафиксировал вопросы и gold до чтения будущей Wiki. OpenViking
runtime/output не читался; репозиторий reviewer не менял. После появления Wiki
этот denominator нельзя подстраивать.

## Exact questions

1. Сколько отдельных записей владельца требуют перед работой искать
   существующие продуктовые рамки, и каковы самая ранняя, самая поздняя и
   действующая формулировки этой позиции?
2. Каковы самая ранняя и самая поздняя записи владельца о сохранении его цитат
   с датами?
3. Как владелец разрешает соотносить буквальное сохранение цитаты и её лёгкое
   сокращение, и что при этом нельзя переписывать?
4. Какая позиция владельца применяется, если более поздняя реплика меняет более
   раннюю?
5. Какие действия и доказательства нужны перед применением найденной позиции
   владельца, и когда следует воздержаться от вывода?
6. Что для владельца важнее: записать новый важный сигнал или улучшить поиск
   старых цитат?
7. Почему доступ к файлу, его чтение, пересказ правила и самоотчёт не доказывают
   соблюдение, и какой наблюдаемый след нужен?
8. Как перед решением совместить цель проекта, общие продуктовые рамки и истину
   конкретного скила, не создавая второй источник правды?
9. Какую задачу владелец хочет решить с помощью OpenViking для chat-recall и
   какие границы этой работы он обозначил?
10. Какую роль Graphiti должен играть при работе с этим корпусом, что именно
    нужно проверить у его результатов и как сопоставлять его с другими
    маршрутами чтения?
11. Какой именно системный промпт stock OpenViking и какая русскоязычная
    конфигурация компиляции выбраны владельцем?

## Closed gold

Все адреса ниже относительно `_ops/chat-recall/`.

1. Recurrence/first/latest Product Frames:
   `2026-08-06-141534-claude-481c094d.md`,
   `2026-08-08-135137-claude-457be55d.md`,
   `2026-08-09-124507-codex-019fe57b.md`,
   `2026-08-12-163448-claude-1d2d9841.md`,
   `2026-08-21-005222-claude-8e9b40bf.md`.
2. Earliest/latest dated capture:
   `2026-07-22-105500-claude-d8a832a4.md`,
   `2026-07-25-124728-codex-019f983d.md`,
   `2026-08-01-164842-claude-d2c4b3e7.md`,
   `2026-08-14-124028-codex-019fff2e.md`,
   `2026-08-20-222832-codex-01a02036.md`.
3. Literal quote versus shortening:
   `2026-07-22-105500-claude-d8a832a4.md`,
   `2026-08-01-164842-claude-d2c4b3e7.md`,
   `2026-08-14-124028-codex-019fff2e.md`,
   `2026-08-20-222832-codex-01a02036.md`.
4. Current versus historical:
   `2026-07-31-005511-codex-019fb495.md`,
   `2026-08-09-030700-codex-019fe36a.md`,
   `2026-08-12-000000-claude-2649459a.md`,
   `2026-08-18-133335-claude-d89e3d9a.md`,
   `2026-08-20-222832-codex-01a02036.md`.
5. Retrieval/application/full-holder/abstain:
   `2026-07-31-005511-codex-019fb495.md`,
   `2026-08-14-124028-codex-019fff2e.md`,
   `2026-08-18-133335-claude-d89e3d9a.md`,
   `2026-08-20-222832-codex-01a02036.md`.
6. Capture-first priority:
   `2026-07-29-201852-codex-019fada0.md`,
   `2026-08-03-232246-codex-019fc8d8.md`,
   `2026-08-20-222832-codex-01a02036.md`.
7. Evidence versus false confidence:
   `2026-08-08-135005-claude-dfa9fb5c.md`,
   `2026-08-08-135137-claude-457be55d.md`,
   `2026-08-20-222832-codex-01a02036.md`.
8. GOAL/Product Frames/skill truth:
   `2026-08-06-141534-claude-481c094d.md`,
   `2026-08-09-124507-codex-019fe57b.md`,
   `2026-08-12-163448-claude-1d2d9841.md`,
   `2026-08-14-122215-claude-2e4e5183.md`.
9. OpenViking outcome/boundary:
   `2026-08-21-133152-codex-01a0236d.md`.
10. Graphiti baseline/limits:
    `2026-08-18-151822-codex-01a0145e.md`,
    `2026-08-19-023138-codex-01a016c7.md`,
    `2026-08-19-122330-claude-01a016c7.md`,
    `2026-08-19-135233-codex-01a01922.md`.
11. Gold `∅`: правильный ответ — `abstain` с явным gap.

## Matched budget

Для каждого arm и вопроса:

- два независимых run;
- `gpt-5.6-luna/max`, одинаковые русский prompt и output schema;
- максимум три discovery operation и шесть evidence reads;
- максимум 120 секунд, 12 000 provider-reported input tokens;
- один ответ, максимум 400 output tokens или 250 слов;
- gold, plan и ответы конкурентов руке не показываются;
- query rewriting и selective retry после результата запрещены.

```json
{
  "answer": "...",
  "status": "current|historical|mixed|not_found|abstain",
  "claims": [{"text": "...", "sources": ["..."]}],
  "recurrence": {"count": null, "first": null, "latest": null},
  "confidence": "high|medium|low|abstain",
  "gaps": []
}
```

Внутренний ID без traceable source address не считается provenance.

## Scoring и gate

На вопрос:

```text
score = 100 × (
  0.50 factual + 0.20 provenance
  + 0.20 chronology/currentness + 0.10 calibration
)
```

Wiki проходит только если:

- factual ≥ 90%; chronology/currentness ≥ 90%; provenance ≥ 80%;
  calibration ≥ 90%;
- нет hard failure;
- total не ниже source holders более чем на пять percentage points;
- median tokens, time или evidence reads лучше source holders минимум на 25%;
- ни одна material cost dimension не хуже source holders более чем на 10%;
- Wiki не хуже Graphiti по chronology и false-confidence control.

Hard failure:

- questions/gold изменены после Wiki;
- inventory или compile receipt неполны;
- truncated result, непрочитанный holder или later-holder gap выдан за proof;
- historical позиция применена как current;
- recurrence/first/latest не имеют traceable provenance;
- no-gold control получает уверенный ответ;
- internal IDs выданы за evidence;
- превышен operation/token/time budget;
- stock Wiki не сохраняет recurrence, contradiction или source traceability.

При hard failure полный backfill не начинается.

## Scope и gaps reviewer-а

- Snapshot: 183 Markdown-файла = `README.md` + 182 holders; 1 076 records:
  916 exact, 160 approximate, 0 unknown.
- 34 records с diagnostics; warnings: `repair-backlog-present` и
  `approximate-or-unknown-time-present`; strict digest exit 1.
- Полностью прочитаны 28 holders, включая весь gold/evaluation union;
  остальные 154 — coverage gap, не доказательство отсутствия данных.
- Два поздних параллельных holder-а не добавлены в closed gold:
  `2026-08-21-145624-codex-01a023be.md` и
  `2026-08-21-145843-codex-01a023c1.md`.
