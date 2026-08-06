# Gate 2 — Выбери Одного Owner-а И Класс Delta

1. Для candidate rule назови полный scope наблюдаемого trigger-а, не папку, где
   текст случайно найден.
2. Выбери самый узкий existing owner, который покрывает trigger целиком и
   загружается до нужного акта.
3. Оставь один source of meaning: competing copies удали, перемести или замени
   pointer-ом. Короткий refresher допустим только в другом lifecycle moment и
   продолжает ссылаться на того же owner-а.
4. Проверь соседние owners: proposed rule не должен незаметно присвоить их
   authority или создать второй способ разрешить тот же конфликт.
5. Классифицируй delta как `local fact / owner pointer`, `behavioral rule` или
   `hard invariant`.
6. Если нужная форма требует split/merge/move/new instruction container,
   остановись до edits: целевой контейнер принадлежит `1ia-audit`.

**Результат gate:** `chosen owner + owned scope + delta class + duplicate
repair`. Нет одного owner-а или устойчивой delta → delete/no-op, не wording.

Далее: `gate3-cell.md`; определение cell — `steering-cell.md`.
