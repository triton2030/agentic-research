---
kind: module-return
состояние: accepted-route
записано: 2026-08-21
---

# Fresh Eyes — дистиллированное знание вместо истории

## Вопрос

Должна ли производная OpenViking-style Wiki хранить chronology, first/latest и
evolution как часть knowledge documents или хранить дистиллированные знания,
оставляя историю неизменяемым source quotes.

Ответ меняет schemas, prompts, acceptance и следующий writer-wave.

## Прямой owner signal

Владелец уточнил: знания — это важные факты, а не история того, как к ним
пришли; для истории остаются исходные цитаты; Wiki не отменяет и не удаляет
цитаты, а является дистиллированной производной.

Source: `_ops/chat-recall/2026-08-21-133152-codex-01a0236d.md`.

## Различающиеся линзы

- **Ladder · `rederive_task`.** Chronology-heavy requirement перестал служить
  верхней цели — быстро восстанавливать текущую локальную правду. Falsifier:
  blind audit без chronology в Wiki не различает current и stale claims.
- **Solvent · `assumption_untested`.** Проверяемость не требует печатать
  историю на странице: L2 может хранить fact, manifest — temporal evidence,
  holders — полную chronology. Falsifier: агент не может раскрыть currentness
  через этот route в заданном reading budget.
- **Prospector · `different_class_exists`.** Living guidelines, Wikibase и
  static projections отделяют current claim от references/revision history.
  Переносимая форма — current claim + provenance + optional lifecycle marker,
  а не narrative evolution.
- **Claude Opus 5 Premortem · `fatal_signal_present`.** Успешная короткая Wiki
  может уверенно показывать отменённую позицию, если происхождение есть, но
  supersession не моделируется. Сигнал уже наблюдался в diagnostic v1: Wiki
  выбрала historical outcome, source arm — current.

## Проверка root

- `modules/return-wave-2-v1-diagnostic.md` действительно фиксирует hard
  current-vs-historical failure при 70 source-link occurrences.
- Текущий plan действительно требовал переносить evolution/contradictions в
  Wiki body и мерить chronology как default outcome.
- Числа Premortem `185/1080` не приняты: выполненные команды дали 184 holder-а,
  1100 records и 312 records типа `коррекция`. Ошибка числа не меняет прямой
  pilot signal.
- Recall coverage: полностью прочитаны текущий holder,
  `2026-08-18-151822-codex-01a0145e.md`,
  `2026-08-20-041346-claude-12da2cc9.md`,
  `2026-08-20-181330-claude-a7539038.md`,
  `2026-08-14-124028-codex-019fff2e.md`,
  `2026-07-25-124728-codex-019f983d.md` и
  `2026-07-22-105500-claude-d8a832a4.md`. Later-check с `--since 2026-08-18`
  нашёл свежую коррекцию текущего holder-а; выдача `truncated=true`, поэтому
  вывод ограничен названной архитектурной границей, а не всем корпусом.
- Три recall-разведчика независимо вернули адреса по границе source/Wiki,
  recurrence и supersession. Для locked supersession fixture выбран полностью
  прочитанный `2026-08-20-181330-claude-a7539038.md`: поздние записи сужают
  роль субагентов до поиска адресов и заменяют условный вызов безусловным.

## Решение

```text
holders            exact words + chronology
   ↓
evidence manifest  membership + count + timestamps + provenance
   ↓
semantic claims    distilled knowledge + applicability + lifecycle status
   ↓
Wiki L2            current/contested knowledge documents
   ↓
L0/L1              progressive reading of accepted Wiki pages
```

`latest` не доказывает `current`. Lifecycle status и supersession являются
semantic candidates с адресуемой опорой и отдельным acceptance, а не
детерминированным следствием timestamp. Superseded claims не выдаются в Wiki
как current; полная история остаётся доступна через holders.

## Следующий необходимый ход

До общей foundation/writer-wave выполнить один representative supersession
probe с locked gold:

1. stable repeated claim;
2. реально отменённая позиция;
3. contested или scope-dependent claim;
4. no-gold control;
5. history question, который обязан перейти к holders.

Pass: blind Wiki reader возвращает current distilled knowledge, не выдаёт
superseded claim за current, а provenance/history раскрывает адресно и только
по запросу. Fail возвращает ближайшую альтернативу: минимальный temporal marker
в Wiki либо chronology-heavy route, если без него currentness неразрешима.

Продолжить без изменений хуже обеих альтернатив: это прямо противоречит
свежему owner signal и масштабирует уже наблюдавшийся historical-answer defect.
