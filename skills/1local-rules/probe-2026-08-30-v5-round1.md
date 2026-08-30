# Realistic probe v5 · round 1

Exact probed candidate SHA:
`48ce6a752569625136d2b0ecc5240e5450ea7877d3a03d4fc685b7d006333607`.

Clean-room executor получил Atlas-case с owner, Claude/Codex projections,
project sync route, global security boundary, exact approval и partial sync
failure.

## Наблюдаемая траектория

Use/skip/near-miss сработали правильно.

До approval mutation не выполнялась.

После exact approval использовался только project route.

Partial sync failure не был объявлен завершением; прямой projection edit и
новый source tree не использовались.

Retire с exact absent approval завершился только после доказанного отсутствия
owner и обеих projections.

## Находки и решения

Обязательный registry и неясный конфликт project sources приняты как дефект и
исправлены.

Неясная граница runtime-owned metadata принята: terminal check теперь сравнивает
общую поверхность, объявленную самим проектом.

Generic rollback после partial failure не добавлен: terminal invariant уже
блокирует ложное completion, а допустимое восстановление принадлежит
конкретному project route и authority.

Отдельная ветка sync-failure не добавлена по той же причине; она не меняет
terminal verdict и без project contract могла бы предписать неразрешённую
mutation.
