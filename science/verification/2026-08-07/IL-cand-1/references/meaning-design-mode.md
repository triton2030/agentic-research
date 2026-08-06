---
read-when: "Пишешь или переписываешь root/subtree instruction или её routing, а не только аудитишь существующую."
---

# Инструкция От Будущих Задач (Design Mode)

Шаги 1-3 протокола (`meaning-protocol.md`) остаются обязательной evidence-базой.

Открывай, когда пишешь или переписываешь root/subtree instruction или её
routing, а не только аудитишь существующую. Это тот же протокол, направленный
вперёд; шаги 1-3 остаются обязательной evidence-базой.

1. **Evidence сначала, всегда.** Rewrite стартует от живых owners, артефактов
   зоны и прошлых traces/corrections; greenfield — от parent/root instruction
   и intended owner. «Новая зона — читать нечего» не бывает.
2. **Representative probes.** Сформулируй будущие задачи/вопросы, с которыми
   cold-start агент реально придёт в зону. Число — по риску: 2-3 для малой
   зоны, шире для global/risky/уже регрессировавшей surface. Probes — evals,
   не контент: их текст никогда не вставляется в инструкцию.
3. **Из probes — минимальный routing.** Для каждой probe выведи первый шаг,
   который инструкция обязана дать just-in-time — обычно owner +
   read-before-edit; validation/escalation добавляй, только когда probe их
   реально требует. Ориентируй, не погружай: указатель к owner-у вместо
   предзагрузки знаний зоны.
4. **Момент загрузки.** Subtree file не ориентирует агента до своей загрузки:
   маршрут к subtree owner живёт в root/parent chain, а сам subtree file несёт
   self-contained guidance уже после загрузки. Topology и placement —
   `placement-scope.md`, не здесь.
5. **Проверка теми же probes.** Bounded check: для каждой probe убедись, что
   effective chain даёт верный первый шаг; при сомнении — один чистый
   cold-start прогон. Probe без ответа = недостающая delta или неверный owner,
   не повод вставить ответ текстом.
