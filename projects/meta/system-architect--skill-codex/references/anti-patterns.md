# Anti-patterns — Чему Я Не Верю

Это не абстрактные запреты. Это короткий список ошибок, которые ломают архитектурное мышление.

## Spine Errors

- **Failure scan до capability inventory.** Это проектирование в темноте. Сначала надо знать, какие рычаги уже стоят на машине.
- **Force Fields в эпилоге.** Если силы появляются после решения, они не проектируют дизайн, а оправдывают его задним числом.
- **`1 failure -> 1 prescription` как default.** Это инженерная санитария, но ещё не архитектура. Архитектура ищет leverage.
- **Add-only answer без `Minimize pass`.** Если ничего не удалено и ничего не отказано, почти наверняка система стала тяжелее.

## Capabilities

- **Предположению о capability по текстовому упоминанию.** `README сказал` не равно `реально установлено`.
- **Новому skill до отказа от существующих слоёв.** Skill — дорогой слой, не default answer.
- **Внешнему поиску до локального capability audit.** Часто решение уже стоит в repo или в installed surface.

## Prescriptions

- **Prescription без backlink.** Тогда правило нельзя отрефакторить и нельзя похоронить.
- **Prescription без sunset signal.** Это archaeology by construction.
- **Сильному новому слою ради одиночного симптома.** Сначала докажи class, потом строй защиту.

## Folder Discipline

- **Удалению папки без Chesterton's fence probe.**
- **Folder verdict без якоря в Stage, Goal или preference.**

## Questions

- **Вопросам без EVPI.**
- **Формату "согласен с моим анализом?"** Это sycophancy trap.
