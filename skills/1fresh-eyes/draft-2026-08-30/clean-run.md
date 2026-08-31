# Exact clean runs — 1fresh-eyes — 2026-08-30

## Identity

Обе пробы получили exact candidate fingerprint
`19defa11a49eb7d632157f88bf85279d3843efd96dabccce8006cb35b5228f59`.
Они были read-only и не меняли candidate, official owners или installed
projections.

## Panel trial

До заморозки исполнитель прочитал только `codex/**` exact candidate и
candidate `product-frame.md`. В четыре пакета были назначены разные зоны:

- Ladder — project GOAL/Product Frames и exact owner speech;
- Solvent — official runtime и прежние receipts/trials;
- Prospector — immutable `1skill-creation` baseline и authoring guide;
- Premortem — git/static evidence и исторические failure traces.

Пакеты были заморожены до первого отчёта, не содержали rationale, желаемого
verdict или материалов других линз.

Claude bridge:

- первая auth-проба вернула `auth_probe_failed`;
- прямая диагностика затем подтвердила `loggedIn: true`, `claude.ai`,
  first-party Max subscription;
- повторный вызов не вернул terminal report, фактическую model family или
  session id в bounded window.

Результат: `panel_incomplete`. Exact global terminal rule остановил проход до
`ladder`, `solvent`, `prospector` и synthesis. Локального заменителя отчёта и
голосования не было. Это доказывает terminal barrier, но не happy path четырёх
отчётов.

## Named trial

Новый clean executor прочитал только root candidate, `packet.md`,
`steering.md` и Product Frame. Для явно названного `profile: auditor` он
заморозил один neutral packet и запустил ровно один fresh agent:

- id: `/root/exact_named_run/native_auditor`;
- type: `auditor`;
- context: `fork_turns: none`.

Premortem, `ladder`, `solvent`, `prospector`, panel и synthesis не запускались.
Correction не потребовалась: native auditor проверил все заданные измерения и
вернул родной `incomplete`. Его сильнейший gap — нет immutable run ledger,
связывающего exact fingerprint с четырьмя terminal reports, correction chain,
synthesis и handback.

Named short-circuit подтверждён наблюдаемым запуском `1 agent / 0 panel / 0
synthesis`. Содержательная оценка осталась native и не была переформатирована
контроллером.

## Verdict

Exact candidate корректно проявил две failure semantics: честный terminal stop
у panel и один native handback у named. Полный panel happy path, cross-family
receipt и non-voting synthesis exact версии не доказаны. Approval и install
до повторной panel-пробы после восстановления Claude bridge не обоснованы.

## Completed precursor panel

Поздний повтор на тех же байтах `19def…` восстановил штатный bridge и завершил
полный путь: Claude Opus 5 Premortem, Ladder, Solvent, Prospector, реальная
same-stream correction Solvent и non-voting synthesis. Адресуемый receipt —
[`panel-run-19def.md`](panel-run-19def.md).

Этот успешный путь стал входом семантического сокращения. Exact final candidate
отдельно получили два независимых checker-а. Начатый дополнительный exact
panel run остановлен до результата как третье доказательство вне текущей
owner-границы.
