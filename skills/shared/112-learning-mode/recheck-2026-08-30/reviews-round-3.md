# Независимые проверки — раунд 3

Проверялась exact candidate с SHA-256 `SKILL.md`
`9908cba1175e7d03c4dedaa9051cbd87fad389da3e2f2e7ce9a7d31d9d2adc0a` и
`references/activation.md`
`7f9f42bd890d118655cbbadf729fa57eac6462a33a1735676c706cfcf34949a4`.
Это второй и последний повтор шагов 3–10 `check-approve.md`.

## Literal checker — PASS

Материальных находок нет. Независимый счёт: activation — 19 с полным evidence,
максимум 20 в смешанной ветке; первое сессионное решение — 19 с методом, 20 в
no-method ветке; поздняя развилка — 16/17; закрытие — 9. Manual trigger,
русский body/reference, локальная цель, ссылка, trigger examples, continuity и
отсутствие official install прошли.

## Clean behavioral probe — core trajectory PASS, один residual

После timeout при уже созданном downstream order агент до действия применил
метод Шерлока «сначала факты, потом теория», поднялся к цели «заказ ровно один
раз», сравнил status lookup с повторным create, назвал prediction/falsifier и
продолжил одним read-only lookup. Activation выполнен один раз; рутинные шаги
не получили повторный ritual; отсутствие результата честно `не проверено`.

Residual probe: агент без evidence назначил lookup timeout
`max(2 × прежний timeout, 120 секунд)`. Candidate не предписывает число; это
утечка обычного профессионального суждения. Универсальное правило из одного
примера не добавлено.

## Trajectory checker — один terminal material residual

Строки `candidate/SKILL.md:39-41` говорят о «применимом методе», который не
изменил бы выбор, тогда как `:48-49` разрешают отрицательную ветку только при
отсутствии применимого метода. Это оставляет escape: метод мог подтвердить уже
выбранный ход, но агент объявит, что тот ничего не изменил.

Минимальная следующая правка checker-а, не внесённая после исчерпания повторов:

> если нет, назови просмотренный корневой scope и один различающий факт,
> показывающий, почему в нём нет метода, способного подтвердить или изменить
> выбор; не подбирай метод задним числом

## Terminal verdict

`exact candidate retained; not accepted`. No-change опровергнут наблюдаемой
пробой первого раунда, но последнюю candidate нельзя выдавать за прошедшую
trajectory acceptance. Official owner/projections/live не менялись.
