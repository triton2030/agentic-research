# Карта сохранности после полного черновика

## Сравниваемые версии

- Zero-based reconstructed draft:
  `reconstructed/SKILL.md`, SHA-256
  `3aec2d5b9e85483179efd304c5d2c26c2c9b397af31f4f6d36af1d34fd664a5b`.
- Последняя exact candidate, остановленная с findings:
  `candidate/SKILL.md`, SHA-256
  `361faf00c670aa1e2e631c1d09b408c4aa5b3669d1f924f40cd2080c081989e4`.
- Действующий official owner:
  `skills/shared/1readable-code/portable/SKILL.md`, SHA-256
  `1bcb9e27fd2e355a2b74501063fec476c105bd2423cbefae5ad66438eda5a42a`.

## Preservation map

| Смысл или поведение | Zero-based результат | Official owner | Вердикт |
| --- | --- | --- | --- |
| Automatic use при переходе к программированию | Тот же `description` | Присутствует | Сохранено без изменения |
| Реактивный task focus скрывает верхнюю картину | Явно восстановлено FAST и clean-room исполнителем | Явно названо в Уникальном контексте | Сохранено |
| CTO/architect view будущей системы | Первая цель и контекст | Контекст и первая цель | Сохранено |
| Известные практики как короткие handles, не tutorial | Восстановлены `strategic programming`, `conceptual integrity`, `deep modules` | Те же три handles | Сохранено; clean-room список particulars снят |
| Дополнительная цена ради будущей формы окупается более дешёвыми следующими изменениями | Clean-room восстановил мотив шире | Official называет future-cost мотив | Не сохранено точно: candidate ошибочно распространил метрику на любую текущую цену |
| Вероятная будущая правка локальна и читаема | Вторая цель | Вторая цель | Сохранено |
| Материальная неопределённость не скрыта | Третья цель и внешний gate | Третья цель и conditional subagent | Сохранено |
| Очевидная работа без ceremony | Третья цель и контекст | Anti-ritual контекст | Сохранено без отдельной инструкции |
| Fresh view только при material uncertainty или прямом запросе | Восстановлено clean-room исполнителем | Точный conditional runtime mechanism | Сохранено |
| Внешний взгляд влияет на решение до edit | Agent-defaults подтвердил необходимость | Strongest justified objection до правки | Сохранено как anti-ritual seam |
| Contract choice не присваивается readable-code | Требуется соседняя функция, но clean-room не знает runtime handle | Оба точных runtime-соседа | Сохранено как невыводимый seam |
| Стратегический tradeoff проверяется своей ценой | Общее условие выхода | Conditional same-cost falsifier | Сохранено в более проверяемой форме |
| Русский instructional body | Reconstructed body содержит обычные англоязычные слова | Official body оставляет английскими только устойчивые имена | Official точнее |
| Короткий English trigger-only description | 113 символов | Candidate: 167 символов, общий trigger и runtime near-miss boundary | Смысл сохранён; routing 6/6, но launch-units нужно разнести по строкам |
| Локальные цели самостоятельных references | Самостоятельных стадий нет | References отсутствуют | Неприменимо; декоративные файлы не созданы |

## Поглощено commander's intent

- молчаливый стратегический проход;
- тест ближайшего подтверждённого изменения;
- fast path без церемонии;
- общая проверка целостности результата.

Эти поведения выводятся из Уникального контекста и трёх целей; отдельные строки
увеличивали бы активный набор без нового выбора.

## Снято из clean-room draft

- каталог `information hiding`, `cohesion`, `dependency direction`, ownership,
  blast radius, reversibility и YAGNI — tutorial вместо short method handles;
- узкий trigger «только перед первой правкой» и исключение read-only review —
  не поддержаны owner-словами об automatic use при любом переходе к
  программированию;
- «без лишней поверхности» как отдельная цель — уже выводится из deep modules
  и расширяет owner-контракт;
- мета-заголовок «Невыводимые механизмы» — authoring rationale не нужен
  пользователю скила.

## Revised verdict после первого checker-round

`change-candidate`: reconstructed draft сам по себе не добавил функции, но
буквальный checker обновлённого `1skill-creation` нашёл нарушения в official
форме. Исправленная версия живёт только в `candidate/`; official owner,
tracked и installed проекции не изменены. Verdict станет доказанным только
после повторных независимых checker-ов и реалистичной clean-пробы exact
candidate SHA.

## Terminal verdict после двух повторов

`stopped-with-findings`: no-change опровергнут, но exact candidate ещё не
доказан. Automatic trigger, named-practice handles, conditional fresh view,
runtime-neighbor route, same-cost closure, русский body и candidate-only gate
сохранены. Остались три минимальные формулировочные правки:

1. ограничить future-cost правило дополнительной ценой, вносимой только ради
   будущей формы;
2. заменить bare `Анализ` на `Дополнительный стратегический анализ`;
3. начать contract near-miss instruction в folded `description` с новой строки.

После любой из этих правок SHA изменится; до нового полного checker/probe cycle версию
нельзя предъявлять на approval и нельзя писать в official owner/projections/live.

## Новый owner-критерий простоты

Решение владельца от 2026-08-30 19:25 +05:00 открыло новый bounded pass после
прежнего stop-boundary. Exact candidate SHA-256:
`6aa4ec3785d3c57d2cec142c92e4541dc52e114225661f9c5ffee7382e9496c7`.

| Owner-смысл | Новая форма | Статус до проверки |
| --- | --- | --- |
| Automatic use на любом writing/changing code | Короткий 78-character English description с функцией | Сохранён |
| Reactive task focus → CTO/architect future view | Первый абзац контекста и первая цель | Сохранён |
| Named practices вместо tutorial | Три handles и явная граница «не учебник и не процедура» | Сохранён |
| Полное professional judgment | Стратегическая изменяемость не подменяет safety/correctness/performance/compatibility/requirements | Исправлена потеря прежней candidate |
| Цельная система и локальная читаемая будущая правка | Вторая цель | Сохранён |
| Ясная работа без ритуала; uncertainty не скрыта | Цель соразмерности | Сохранён без отдельной стадии |
| Contract choice не присваивается readable-code | Точная runtime-граница до решения | Сохранён |
| Fresh view только после material uncertainty или owner-request | Одна conditional boundary | Сохранён |
| Не переусложнять process | Strongest-objection и same-cost stages сняты; references нет | Новое owner-решение внедрено; нужен falsifying clean-run |

Это ещё не approvable verdict: нужны два независимых checker-а и clean-run exact SHA.

## Terminal preservation verdict

`candidate-ready-for-exact-approval`: два независимых checker-а не нашли потерь,
routing прошёл 6/6, а clean-run подтвердил, что снятие strongest-objection и
same-cost stages не потеряло их полезную функцию. Агент вывел comparator, falsifier и
negative checks из commander's intent и обычного professional judgment.

Сохранены все owner-смыслы и материальные runtime-границы. Official owner, tracked
projections и live packages не изменены; exact approval ещё не дан.
