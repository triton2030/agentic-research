# Description Char-Budget Post-Edit Only

## Observation

При добавлении фраз в matcher `description` модель часто считает длину
**после** Edit, а не до. Pattern: «прикинул в уме что войдёт» → Edit →
запуск `wc -m` / Python YAML parse → превышение 1024 → второй раунд
cuts.

Cycle:

1. User signal: «добавь триггеры X, Y, Z».
2. Модель идёт в Edit, добавляет phrases.
3. Post-edit measure — Claude 1027, Codex 1029 (over limit by 3-5).
4. Модель выбирает фразы которые можно убрать.
5. Second Edit.
6. Post-second-edit measure — ОК.

Два прохода вместо одного. Pre-edit calc дешевле — `python3 -c "print(len(yaml.safe_load(open('SKILL.md').read().split('---',2)[1])['description']))"` занимает 50ms.

Связано с **anchoring** (опираюсь на «должно войти» вместо реального
count) + **anti-mental-model**: 1024 chars не интуитивны на глаз,
особенно с RU symbols (UTF-8 2-byte per char).

## Counter

- 2026-05-20 [Claude Opus 4.7]: правка matcher `1md-navigator` с
  добавлением 5 verb-triggers («посмотри / найди / изучи / сравни /
  прочти»). Не сделал pre-edit calc: ожидал что input bumped с
  ~62 chars и я в зоне 1019+62=1081, что over. Сделал Edit, измерил
  post → 1027/1029, потом второй раунд cuts (drop «концепт-граф»,
  сократил `Verbs (md-scope by default):` → `Verbs (md):`). Two-pass
  вместо one-pass.

## Possible upgrade

Перед любой substantive правкой `description` блока — **mandatory
pre-edit calc** через Python YAML recipe из `1skill-architect`. В
матрице: текущая len + estimated new phrases в chars vs 1024 budget.
Если estimated > 1000 — сначала освобождать место, потом добавлять.

Связано с `cross-runtime-skill-sync-skip` (когда правишь в двух
runtimes — calc делается для обеих копий до Edit).
