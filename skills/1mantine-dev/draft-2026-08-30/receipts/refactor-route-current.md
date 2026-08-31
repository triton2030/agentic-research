# Полный refactor route по effective 1skill-creation

## Baseline

Первоначальный THREAD_CARD закреплял fingerprint `9bf11f64…`, но 2026-08-31
действующий `1skill-creation` изменился: ориентир 20 теперь сигнал когнитивного
риска, а не автоматический blocker. Более поздний current owner-контракт
применён к этой коррекции.

`python3 skills/shared/sync_simple_projections.py 1skill-creation --check`
подтверждает соответствие tracked owner и установленных projections текущему
effective baseline.

## FAST

Функция: в Mantine-задаче заменить generic frontend prior выбором по текущей официальной public surface установленной когорты.

Момент: implementation, debugging, review или upgrade уже относится к Mantine UI.

Желаемое поведение: public handle проверяется раньше custom-кода; итог минимизирует совокупную сложность; audit доказывает полноту в названном scope.

Owner evidence: `_ops/chat-recall/2026-08-30-170320-codex-01a0528c.md:17-21`.

## Clean-room Reimplementation и Zero-based Design

Чистый исполнитель `/root/mantine_zero_clean` получил только новый commander's intent и запрет читать старый либо текущий пакет.

Он независимо восстановил три runtime-файла: короткое тело, audit public surface и conditional recent-updates.

Его обязательные функции совпали с FAST: current official source, public-before-custom, aggregate complexity, readable local residue, scoped audit и rolling 12-month delta.

Он снял каталоги components/props, generic frontend handbook, постоянный полный changelog, package-specific references, agents, scripts и обязательный полный audit любой локальной правки.

Сохранённый смысловой вывод чистого исполнителя: core должен начинаться с поведения и resolved cohort; audit завершается coverage-map; recent-updates передаёт только релевантную дельту; оба reference не активны одновременно.

## Loss map

| Старый либо owner-смысл | Состояние в candidate | Причина |
| --- | --- | --- |
| Одинаковая resolved-версия `@mantine/*` | сохранён | первый core-шаг |
| Текущая официальная документация вместо памяти | сохранён | unique context, первая цель и `llms.txt` route |
| Public component/capability before custom | сохранён | вторая цель и highest-handle решение |
| Forms, hooks, managers, Styles API и package-specific возможности | поглощён | audit ищет релевантные packages, components и capabilities, не держит вечный каталог |
| Отдельный audit | сохранён | `references/audit.md` с named scope и stop condition |
| Новые изменения последнего года | сохранён | rolling window пересобирается по официальному release-index на каждом вызове, включая patch releases |
| Tailwind interaction | сохранён условно | current official Mantine styles page читается только при Tailwind/CSS-layers interaction |
| Подробные v7→v8 и v8→v9 ловушки | снят как embedded snapshot | exact migration guide и installed public types надёжнее стареющего пересказа |
| `help-center-map.md` и `placement.md` | снят | owner-решение 2026-08-22 supersedes прежнюю пару; chronology сохранена в `cut.md` |
| Читаемость и редкое custom-исключение | сохранён без усиления | aggregate complexity плюс readable local residue соответствует owner-цитате, triple veto снят |
| Проверяемый результат | усилен | receipt требует exact source и `check → observed result`, иначе `unknown` |
| Явный раздел цели | восстановлен | поздняя owner-коррекция требует вынести commander's intent в runtime, а не оставлять его только в history |

Подробная карта поглощений и снятий находится в [`../../cut.md`](../../cut.md).

## Переиспользованные проверки

FAST и ранние loss decisions сохранены в `origin.md`, `cut.md` и `reviews-round1.md`.

Два прежних checker rounds сохранены в `reviews-round1.md` и `reviews-round2.md`.

Два прежних clean probes сохранены в `clean-run-round1.md` и `clean-run-round2.md`.

Текущий clean probe `/root/mantine_clean_r3` независимо снял raw grid, field `useState`, homemade toast и 1:1 button wrapper через public Mantine handles; без app fixture runtime evidence честно осталось `unknown`.

Terminal check-approve, exact hash, verdicts и residue сохранены в [`../reviews-terminal.md`](../reviews-terminal.md).

## Follow-up: simplicity and handoff repair — 2026-08-30

Новый owner-критерий («не переусложнять процесс») проверен через `$1fresh-eyes`:
trajectory-critic назвал прежние шесть стадий method-as-goal и рекомендовал
оставить core плюс два условных gate. Исторический terminal receipt признан
невалидным для closure текущих байтов: его file hashes покрывали другую версию.

Независимый recall подтвердил commander intent: official Mantine public surface
остаётся источником истины, audit — отдельный cold path, version delta —
условный, а custom — редкое readable-local исключение.

Clean-room / Zero-based follow-up получил только обновлённый intent и вернул
ровно три runtime-файла: короткий `SKILL.md`, `references/audit.md` и
`references/last-year.md`. Runtime не содержит approval, installation,
orchestration или механического дробления active set.

Текущий candidate поглощает `window`/`confirmation` в один version gate и
`scope`/`candidates`/`decision` в один audit gate. Handoff-инварианты исправлены
буквально: version reference возвращает self-contained delta, сохраняющую
исходный task packet и resolved/confirmed cohort; audit получает
`audit_input` с required behaviors, cohort, named scope и current solution.

## Follow-up: восстановление цели — 2026-08-31

Владелец указал, что runtime-раздел цели был потерян
(`_ops/chat-recall/2026-08-30-170320-codex-01a0528c.md:21`). Уникальный контекст
снова описывает именно конфликт generic prior с Mantine, а две зонтичные цели
сохраняют official/full-use/less-code/readability outcome и редкое
aggregate-complexity custom-исключение. References и порядок gates не менялись.

## Install approved — 2026-08-31

Владелец безусловно одобрил переписать и установить показанный exact candidate
(`_ops/chat-recall/2026-08-30-170320-codex-01a0528c.md:23`). Tracked owner в
registry отсутствует, поэтому новый source tree не создавался. Codex и Claude
live packages установлены ровно из трёх approved runtime-файлов; оба aggregate
совпадают с candidate `9ffc82e60afe2a3974bff1912ed2b2e51038b827976ad7a22a87937f03df2c06`.
