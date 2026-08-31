# Независимые проверки, round 2

> Коррекция 2026-08-30: более поздний retrieval нашёл owner-решение
> 2026-08-22 сократить `1mantine-dev` до delta-only. Поэтому прежний вывод о
> возврате `help-center-map.md` и `placement.md` отменён; текущий черновик
> содержит только `audit.md` и `last-year.md`.

## Принято

- `last-year.md` был фактически always-on; route сужен до upgrade, docs mismatch
  и конкретной межверсионной неопределённости.
- Поиск начинался с уже известного компонента; core и audit теперь начинают с
  требуемого поведения и официального каталога.
- API-gap сам по себе разрешал custom; промежуточная правка заменила его
  тройным veto, но позднейшая owner-check отменила это усиление в пользу
  совокупной сложности и читаемого локального residue.
- Не было веток old-major и unresolved cohort; они добавлены.
- ~~Новый запрос не отменял прежние `help-center-map.md` и `placement.md`; оба
  маршрута возвращены вместе с новыми audit и last-year стадиями.~~
  Superseded: более позднее owner-решение 2026-08-22 отменило прежнюю пару.
- Предыдущий semantic budget был занижен; каталог обновлений и оба старых
  references сокращены до decision-changing материала.

## Доказательства

- Trajectory checker назвал три escape path: always-on changelog,
  candidate-first discovery и молчаливую потерю прежних references.
- Literal checker подтвердил эти пути, нашёл custom-gap escape, старый major без
  official-page branch и превышение active set.
- Clean executor получил правильный Mantine-first settings-form result, но не
  имел app fixture для runtime evidence.

## Остаток после обязательной остановки

Финальное сокращение сделано после второго независимого раунда, поэтому точная
версия ниже имеет structural checks Root, но не третий clean-agent run. Этот
остаток нельзя скрывать при запросе одобрения.
