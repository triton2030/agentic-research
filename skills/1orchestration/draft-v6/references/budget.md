# Оценка когнитивной нагрузки

Вход: active-unit ledger actor-а готов. Выход: verdict `manageable` либо
`decompose` с основанием.

1. Оцени count, coupling и горизонт удержания ledger-а.
2. `≤20` обычно `manageable`; coupling или длинная траектория могут понизить
   verdict раньше, а число не является hard cap.
3. Невыполнимый set получает `decompose`.
