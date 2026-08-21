---
kind: module-card
волна: 3
роль: writer
модель: gpt-5.6-luna
thinking: max
---

# Модуль — typed-evidence probe

## Outcome

На двух замороженных кластерах проверить seam: exact evidence
компилируется детерминированно, а OpenViking official LLM Wiki Skill
создаёт из него удобный сводный слой без потери точных фактов.

## Ownership

- Пишет только `experiments/openviking-chat-recall/**`.
- Не один в кодовой базе: не откатывать чужие правки, адаптироваться к
  текущему `main`.
- `_ops/chat-recall/**`, `_ops/plans/**`, global skills и upstream — read-only.
- `build_inventory.py` остаётся owner замороженного file inventory.
  Новый `build_typed_probe.py` владеет только typed records и их
  deterministic validation.

## Frozen input

### Cluster A — retrieval aid is not proof

Source SHA-256:
`501cad60b995a15ce2382ea1c4f264f4c3f22a0e1450dda2fbe4d891c58016ff`.
Ровно четыре record: строки 20, 26, 31 и 35 frozen holder
`2026-08-14-124028-codex-019fff2e.md`.

- Exact count: `4`.
- First: `2026-08-14T07:45:46.732000+00:00`.
- Latest: `2026-08-17T17:46:29+05:00`.
- Current meaning: search/card/hit выбирает holder для полного чтения и
  не доказывает позицию владельца.

### Cluster B — current OpenViking outcome

Source SHA-256:
`c92addebb7e56454bb848a935f2bdfe6408f9b6949248c1ca56dd06ec0502443`.
Ровно пять direct owner record: строки 18–22 frozen holder
`2026-08-21-133152-codex-01a0236d.md`.

Wiki должна сохранить все пять обязательств:

1. слои пересказа по OpenViking для экономии токенов;
2. отдельные документы/отчёты и явный факт повторения;
3. готовая библиотека, параллельная папка и static old-folder import;
4. official system prompts и information architecture OpenViking;
5. после рефактора — проверка, насколько агентам удобно находить
   знание.

## Делает

1. Записывает машиночитаемый gold manifest с source path, SHA, record ID,
   timestamp, kind/type, exact quote и cluster membership.
2. Добавляет `scripts/build_typed_probe.py`, который проверяет source SHA,
   извлекает records без LLM и строит typed Markdown input.
3. Добавляет узкие tests на SHA drift, exact membership, count/first/latest и
   воспроизводимый output.
4. Подаёт только typed Markdown в тот же official Skill/IA/Compile route.
   Diagnostic shim допустим только для изоляции semantic seam; stock gate
   остаётся blocked и не переименовывается в pass.
5. Сохраняет input, Wiki, команды, receipt и task-owned commit.

## Не делает

- Не запускает full corpus и не строит общий wrapper.
- Не отдаёт LLM расчёт exact count/first/latest.
- Не меняет source holders, official Skill и upstream.
- Не принимает сам семантику созданной Wiki.

## Writer return

- Commit hash и exact changed paths.
- Команды и terminal evidence для tests, builder, compile и deterministic
  validation.
- Явно: stock или diagnostic route; любое отклонение от official пути.
- URI/tree результата и список созданных Wiki pages.
- Candidate без self-acceptance: корневой агент запустит blind reader.

## Gate

Probe passes только если:

- deterministic validator подтверждает ровно 4 records и exact first/latest;
- в готовой Wiki exact facts не изменены и адресуются к provenance;
- blind reader без holders/gold восстанавливает все пять обязательств
  current outcome без outcome inversion;
- no-gold/unsupported claim не получает confident answer.

Любой fail оставляет full corpus заблокированным.
