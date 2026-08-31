# Авторские проверки — `1index`

## Цель

Зафиксировать author modes и изменения после двух checker rounds.

## Short description

`Use when costly search or a direct owner statement identifies a specific
hard-to-find location.` — 95 символов, одна English trigger-only фраза
`Use when…`; функция, маршрут, результат и exclusion отсутствуют. Use: место
подтверждено дорогим поиском или прямым словом владельца. Skip: известный
config. Near-miss: повторная ошибка без новой находки → `1context-refactor`.

## Behavior protocol

Дословного owner-порядка нет. Оставлены только невыводимые admission,
authority и falsifier; отдельный «Протокол поведения» не создан.

## Reference files и active set

Clean-room body был линейным, первый recount потребовал три стадии, а второй
recount показал, что дробление сохранило лишние predicates. Поздний simplicity
gate снял отдельное сохранение evidence и поставил проверку до записи.
Итоговый candidate self-contained; предварительная оценка active set — 19.
Финальный буквальный recount ниже эту оценку опроверг.

## Agent defaults

Оставлены три исправляемых дефолта: полезную тему индексировать без понесённой
цены; скопировать знание рядом со ссылкой; создать отсутствующий INDEX без
approval. Все остальные прежние правила сняты либо поглощены целью.

## Exact gate — `bcce2e257404327e2a3217eeb42775e1c3860959e5ae62bf0ec3165314f4c390`

Замороженный вход:

- `SKILL.md` — `b7a89154ea55b3d81685d0dd01939d333db8f9a94e531eaed57a5a36c59a8e6e`;
- Codex metadata — `4f4f7c3f8159ba19f2249680a0ec5296f0123db073d15553d803981c648116e7`.

Независимый trajectory checker: **PASS**. Две admission-ветви, per-source gate,
intent evidence, route-not-knowledge, one-hop и authority сохранились; runtime
остался одним файлом без стадий и references.

Чистая realistic probe: **PASS**. Оба дорого найденных скрытых источника
записаны маршрутами, очевидный config отклонён, знание и порог не скопированы,
causal verdict остался unknown, ремонт без evidence и authority не выполнен.
След: `skills/1context-refactor/review-2026-08-30/probe/RESULT.md`.

Независимый literal checker: **CHANGES_REQUIRED**. Строгий recount дал `26`
units для body и `31` для Codex path: цель 3 · контекст 5 · per-source admission
2 · intent evidence 2 · route schema 4 · one-hop 4 · placement/authority 4 ·
missing-INDEX branch 2; default prompt добавляет 5. Кроме бюджета, формула
«проверки одним переходом до живого владельца» не называет начало проверки
от намерения вне INDEX и допускает проверку только от уже открытого source.

Terminal verdict: **CHANGES_REQUIRED**. Candidate не принят и не устанавливался;
ещё один rewrite после exact gate не выполнялся.

## Exact gate — `6c8f0af1a15a9ac1d55a5dd442a90be343d9040ef7d6e1b53c4588b474625d4b`

После принятия `26/31` как мягкого residual исправлен только объект one-hop
проверки: маршрут проверяется от намерения вне INDEX до живого владельца
знания одним переходом.

Замороженный вход:

- `SKILL.md` — `1314f3cccb237206c2d5c1f7d5ed4837ba52a26a21bdd661957f666afe0b94c1`;
- Codex metadata — `4f4f7c3f8159ba19f2249680a0ec5296f0123db073d15553d803981c648116e7`.

Независимый literal checker: **PASS**. Recount остался `26` для body и `31`
для Codex path; уточнение one-hop не создало отдельного выбора, стадии или
обязанности. Других буквальных дефектов нет.

Независимый trajectory checker: **PASS**. Исправление закрыло путь проверки от
уже открытого source, не изменив admission, route-not-knowledge, authority и
однофайловую форму.

Повторная realistic clean probe: **PASS**. Два внешних намерения за один
Markdown-переход достигли exact source owners; очевидный config отклонён,
знание не скопировано, причинность осталась unknown, repair без authority не
выполнен. След:
`skills/1context-refactor/review-2026-08-30/probe/RESULT.md`.

Terminal verdict: **PASS / exact candidate ready for approval**. Этот gate не
менял official, tracked owners, projections или live; существующее грязное
состояние worktree сохранено.
