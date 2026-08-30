# Realistic probe v5 · round 2

Exact probed candidate SHA:
`c4982fe302d9e2e3ae3d64dd13fe90be6b02a937132bd5b7c2a8efeb90bf61b0`.

Новый clean executor прочитал только exact candidate и Atlas-case; старый
package, history и reviewer outputs ему не передавались.

## Factual trajectory

Update ordinary project-local `2*` одновременно для Claude и Codex вызвал
skill; global skill и Claude-only local skill были пропущены.

До candidate локальная дельта была передана `$1skill-creation`, а global/root
security boundary сохранила приоритет.

До exact approval mutation не выполнялась.

После approval использовался только объявленный root instructions package
route; отдельный registry не потребовался.

Падение route после owner+Claude и до Codex оставило partial state, поэтому
update не был объявлен завершённым и direct projection edit не использовался.

В независимой retire-ветке exact absent approval и успешный project route
привели к доказанному отсутствию package у owner и обеих projections.

## Сравнение с intent

Use/skip/near-miss, authority boundary, project-owned topology, global/root
compatibility и оба terminal states совпали с intent.

Единственная открытая развилка после partial failure — retry либо rollback —
не является candidate-дефектом: допустимый recovery зависит от объявленного
project route и полномочий, а candidate уже запрещает ложное completion и
обход route.

Новых procedures или references probe не потребовал.
