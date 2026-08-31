# Behavioral probe — final allowed repeat

## Tested candidate

Aggregate package hash before the final checker fixes:
`455b6a36e76e65d35b51cfe4f156249a7b9a24b9cf62adb40923a1d9c75fdb6b`.

## Input

«Используй фоновые треды, чтобы провести крупный рефактор сервиса: API,
миграции и документация лежат в раздельных файлах, но два исполнителя могут
затронуть один schema-файл; есть одна материальная архитектурная развилка. Я
хочу экономить токены».

## Actual trajectory

- Root сохранил роль технического директора и делегировал архитектурный анализ
  Sol/xhigh thread, а API, migrations и docs — Luna/max threads.
- Schema overlap был снят single-writer, поэтому environment verdict остался
  Local; Worktree не выбран.
- Mutable authors получили независимый verification outcome; monitoring был
  event-driven, а acceptance зависела от карточки, artifacts и checks.
- Все bounded threads остались unpinned и должны были архивироваться после
  integration.
- Реальные launches были корректно остановлены: probe не содержал exact paths,
  starting state и полного `done_when`.

## Findings

- Controller retained reuse, umbrella retained archive и receiver result-schema
  были недостижимы из router-а.
- Aggregate verifier против нескольких verifier threads оставлен решению
  `1orchestration`: каждый mutable outcome имеет отдельный verification slot,
  а число исполнителей зависит от когнитивной нагрузки.

Три reachability findings исправлены после этого probe. Новый independent
repeat не запущен, потому что `check-approve.md` ограничивает цикл двумя
повторами; exact post-fix evidence остаётся gap до решения владельца.
