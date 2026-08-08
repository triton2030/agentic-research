# Gate 3 — Инстанцируй Steering Cell

Понятие cell и контрастивная демонстрация механизма — [`steering-cell.md`](steering-cell.md), до пункта 1.

1. Выбери один representative future case, где trigger возникает естественно,
   старый ход правдоподобен, а разница видна до финального самоотчёта.
2. Назови точный fork: наблюдаемый момент, в котором доступны старая и нужная
   траектории.
3. Прогони этот момент через реально загружаемую old/default chain, не добавляя
   proposed rule задним числом.
4. Запиши первый наблюдаемый natural act; не подменяй его скрытым состоянием или
   поздним объяснением агента.
5. Назови видимый сигнал, делающий этот act правдоподобным, и конкретный harm,
   который он запускает.
6. Запиши первый target act, source check, comparison, artifact или decision
   rule, который должен стать естественным вместо него.
7. Сверь target с owner meaning: пример иллюстрирует правило, но не создаёт его.
8. Сформулируй одно изменение `natural first act → target first act`; несколько
   независимых изменений означают несколько repairs или слишком широкий scope.
9. Для load-bearing meaning, success criteria либо design root/subtree routing
   используй [`audit-meaning-criteria.md`](audit-meaning-criteria.md)
   как conditional depth, а не копируй его protocol сюда.

**Результат gate:** полная steering cell `fork + natural act + plausibility +
harm + target act + changed rule`. Акты не различаются → durable steering delta
не доказана.
