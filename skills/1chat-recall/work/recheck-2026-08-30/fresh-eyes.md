# Fresh Eyes — checkpoint простоты

Статус: pre-metadata-repair review history; не проверяет manifests из
[reviews.md](reviews.md) и не является approval текущего candidate.

Якорь решения: ведёт ли трёхчастный candidate к исходной пользе — надёжной
записи после полной карты тем, короткому keyword-context и повторному поиску —
либо работа уже обслуживает собственную проверочную форму.

## Независимые отчёты

- Premortem (Claude Opus 5): `fatal_signal_present · alternative`. Topology
  держится, но metadata и validator были привязаны к `$PWD`, а operational
  keyword-context ослаблен. Falsifier — clean Capture в чужом target root с
  коротким noun-phrase context. Следствие — локально исправить target root и
  context, не менять topology.
- Ladder: `ladder_holds · unchanged`. Три функции ведут от literal Capture и
  decision-scoped Retrieval к цели проекта — следующая сессия применяет
  доказанную позицию без повторного объяснения. Falsifier — fresh session
  пропускает карту, пишет narrative context или удерживает завершённую стадию.
- Solvent: `dissolve · alternative`. Самостоятельный Restoration и optional
  verifier не имели наблюдаемого counterfactual harm; application Retrieval уже
  принадлежит исходной работе и её authority. Falsifier — без Restoration агент
  создаёт новый profile/owner либо не способен применить evidence к явно
  заказанной работе.
- Prospector: `different_class_exists · next`. ADR подтверждает chronology, но
  ошибочно смешал бы evidence и current truth; Wikidata подтверждает structured
  metadata, но её schema-governance дороже локальной карты; progressive
  disclosure Agent Skills подтверждает body + один mode reference. Falsifier —
  fresh instance требует несколько references или не находит запись по
  естественной переформулировке.

## Синтез

Выбран `next`: оставить Capture/Retrieval/Integrity, исправить target root и
keyword-context, убрать standalone Restoration и optional verifier, затем
выполнить clean-run. `Unchanged` отвергнут из-за наблюдаемого target-root
дефекта. Более крупная перестройка отвергнута: независимые функции и
progressive disclosure сохраняют верхнюю цель.

Legacy-корпуса без `topics.md` вынесены в отдельную находку; candidate только
fail-closed предотвращает новую запись с непроверенной темой.

## Narrow repair checkpoint — 2026-08-30

`1fresh-eyes/trajectory-critic` вернул `next` и обозначил четыре остатка.
Рекурсивная проверка provenance и парные adversarial ветви закрыли вложенный и
смешанный marker cases в том же Codex test. Реальные native probes теперь
адресованы transcript path + SHA, command и output SHA; поэтому прежний receipt
про «native store unavailable» заменяется наблюдаемым current-runtime trace.

Неизвестный carrier без wrapper или marker остаётся неразличимым с прямым
`user.text`: positive direct marker отсутствует в текущей native схеме, поэтому
его нельзя безопасно отвергать без потери owner speech. Этот residual вынесен в
`1findings`, а не превращён в новую runtime-стадию. Trigger surface проверяется
тремя представительными фразами (use / skip / near-miss), без расширения
описания функцией или результатом. Official, tracked и installed projections
не входят в candidate write scope.

Trajectory checker дополнительно обнаружил, что поздняя отмена могла попасть в
Capture без связи со старой записью. Это закрыто явной передачей проверенного
`--supersedes` либо `--contested` в шаге Capture; helper уже владел этой схемой,
поэтому topology и active-set не выросли.

## Retrieval freshness checkpoint — 2026-08-31

Owner добавил обязательную видимость времени: найденная цитата теперь несёт
абсолютную `date` и относительный `age` в часах или днях. В decision-scoped
query explicit verified `supersedes` скрывает отменённую запись; `--timeline`
показывает обе записи, чтобы не потерять хронологию. Это две существующие
ветви Retrieval, а не новый режим или reference. Чистый корпус подтвердил
новую цитату как единственную decision position и обе датированные записи в
timeline; тест оставляет межscope-ранжирование за пределами этой функции.
