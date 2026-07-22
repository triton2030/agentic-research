---
description: "Cohort-based recovery for accumulated edge inflation, owner loops and missing hard dependencies."
---

# Graph Recovery

Открывай, когда граф уже накопил ошибки — navigation-inflation, петли
владения, пропущенные межслойные связи, разошедшиеся ручные списки — и нужен
восстановительный аудит, а не правка одного файла. Это отдельный маршрут с
конечной cohort и повторяемыми замерами; «корпус в целом проверен» без
denominator-а — симуляция.

## Порядок

1. **Baseline.** Зафиксируй до правок:
   - structural state: scoped `md check`, `md cycles`, `md health`;
   - распределение цены: `md preflight` на стратифицированной выборке файлов —
     прямые держатели и каскад depth 2 (`edit_plan.must_update`);
   - самые дорогие хабы (много входящих edges);
   - стратифицированная выборка edges по жанрам (15–25);
   - sentinel claims: несколько ИЗВЕСТНЫХ смысловых зависимостей (в т.ч.
     межслойных), по которым потом мерить recall.

2. **Сначала owner-дефекты, потом thinning:**
   - смысловые owner-петли (slots в
     [`semantic-edge-audit.md`](semantic-edge-audit.md));
   - router-as-source: hard edge на файл-роутер, который сам ничем не владеет;
   - два канона одного инварианта.

   Все три — `owner-conflict` → `1ia-audit`. Резать edges до разрешения
   владения — закреплять неправильного владельца.

3. **Hub-first edge audit.** Входящие edges самых дорогих хабов — через
   admission test: `keep` / `reverse` / `downgrade` / `remove` /
   `owner-conflict` / `deferred`, каждый вердикт с X/Y и body addresses.
   Похожесть и размер каскада сами по себе не вердикт.

4. **Missing-edge audit.** Для каждого sentinel claim — claim + consumer
   probes ([`section-blast-radius.md`](section-blast-radius.md)). Sentinel set
   обязан покрывать разные типы потребителей (интерфейс, деньги, обещания,
   право), не только тематические разделы. Similarity не становится edge без
   чтения тела и X/Y.

5. **Duplicate-truth audit.** Найди body-секции, претендующие на реестр
   держателей/consumers; сравни с вычисляемым reverse graph; расхождение —
   `duplicate-truth`, representation-решение (generated view / навигация /
   удаление) — у `1ia-audit`.

6. **Повторный замер на той же выборке**, теми же линейками:
   - доля navigation-inflation;
   - размер прямого и depth-2 каскада (медиана и хабы);
   - recall sentinel claims (найдены / retrieval failure);
   - цена: прочитано кандидатов на один подтверждённый missing edge;
   - сохранность настоящих hard contracts (не перерезали живое).

## Стоп

Не «граф чист», а:

- выбранная cohort полностью audited, неохваченный остаток назван;
- у каждого edge-вердикта есть X/Y evidence;
- sentinel gaps найдены либо честно зафиксирован retrieval failure;
- owner-conflicts разрешены или переданы `1ia-audit`;
- повторный замер сравнён с baseline.
