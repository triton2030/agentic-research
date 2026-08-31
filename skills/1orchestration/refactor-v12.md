# Минимальный repair 1orchestration — v12

Состояние: `ready exact candidate; needs installation approval`.

## Owner boundary

`_ops/chat-recall/2026-08-29-152721-codex-01a04d0e.md:24` требует автономно
вносить candidate-исправления и спрашивать владельца только перед установкой.

## Причинная дельта v11 → v12

1. Возвращён upstream rollback из установленного v10: изменение влияющего
   входа возвращает затронутую работу к первому устаревшему результату.
2. `delta` теперь прямо означает сведения, которых actor не найдёт в доступных
   файлах, а не только в уже адресованном `read`.
3. Trigger называет и момент, и функцию: cognitive work превращается в
   feasible actor loads.

Функция, Уникальный контекст, три цели, literal `read → brief → estimate`,
brief-interface, actor/root оценки, soft 20, release boundary и evidence gate
не менялись.

## Complexity verdict

V11 имел `body 20`. Rollback — отдельно нарушимая обязанность, поэтому v12
имеет `body 21`; скрывать её объединением нельзя. Reference не уменьшит набор,
поскольку rollback действует во всех runtime-формах.

## Preservation map

| Смысл | Адрес v12 | Решение |
| --- | --- | --- |
| root-CTO: польза, траектория, решения, интеграция, приёмка | цель 1 | сохранён зонтиком |
| посильные active sets root и actor/model | цель 1 + шаги 3–6 | сохранён |
| source-bound brief без второго owner-а | цель 2 + шаг 2 | сохранён |
| root читает всё влияющее до brief | шаг 1 | сохранён по позднему owner-evidence |
| `outcome · done_when/evidence · read · delta` | шаг 2 | сохранён; delta приведена к буквальной границе любых доступных файлов |
| порядок `read → brief → estimate` | шаги 1–3 | сохранён буквальными owner-фрагментами |
| actor/root fit, cognitive price и soft 20 | контекст + цель 1 + шаги 3–6 | сохранён |
| реальное уменьшение набора | шаг 7 | сохранён |
| self-report не evidence; all-pass barrier | цель 3 + `done_when` | сохранён |
| upstream invalidation и rollback | шаг 8 | восстановлен явно из v10 |

Потерь функции, owner-смыслов, конечного состояния или требуемого порядка
после repair не осталось. Ничего из `cut.md` не возвращено, кроме ошибочно
снятого rollback.

## Current agent-defaults ledger

Формат: `источник → неверное прочтение/дефолт → изменяемое решение → вред →
цена строгости → минимальная правка`.

| ID | Формулировка | Аудит |
| --- | --- | --- |
| R1 | trigger | owner-момент + routing protocol → вызвать после отправки / широкое «делегирование» → вызов только before и только для feasible-load функции → поздний или ложный trigger → более узкий routing → оставить |
| C1 | instruction layers | owner 2026-08-10:20 → считать задачу только работой → включить влияющие instruction layers → скрытая нагрузка → одно знание контекста → оставить |
| C2 | cognitive price varies | owner 2026-08-10:21 → считать все units равными → взвешивать цену → неверный actor → усложняет оценку → оставить |
| C3 | actor/model fit varies | owner 2026-08-10:21 → выбрать ближайшую модель → учитывать fit → провал слабого actor/model → ограничивает свободный routing → оставить |
| C4 | soft 20 | owner 2026-08-29:20 → превратить число в hard cap → использовать как risk signal → механический split → одна пороговая эвристика → оставить |
| G1 | root is CTO-owner | owner 2026-08-10:24,27 → root отдаёт верхнеуровневый verdict → удержать authority → потеря пользы и интеграции → root несёт постоянную ответственность → оставить зонтиком |
| G2 | feasible root/actor sets | owner 2026-08-10:23-24 → оптимизировать только worker → учитывать обе стороны → перегруженный root или actor → дополнительная оценка → оставить |
| G3 | brief is not truth owner | owner 2026-08-29:20 → prompt пересказывает files → адресовать truth → дубль и drift → brief зависит от sources → оставить |
| G4 | current all-pass barrier | v10 + observed falsifier → открыть dependency по неполному return → ждать актуальные pass → downstream на ложном основании → жёсткий barrier → оставить |
| G5 | self-report is not evidence | observed clean failure + P-005 → принять уверенное `done` → потребовать evidence → ложный pass → отчёт сам по себе недостаточен → оставить |
| P1 | read before brief | literal owner 2026-08-29:20 → actor сам прочитает → root читает influencing inputs первым → неполный brief → расход root-window → оставить literal |
| P2 | do not repeat file truth | literal owner 2026-08-29:20 → безопасный пересказ → адресовать files → второй owner → требует доступных адресов → оставить literal |
| P3 | `outcome` | owner требует правильную цель → дать тему вместо результата → назвать состояние → actor не знает done → фиксированное поле → оставить |
| P4 | `done_when/evidence` | owner требует все acceptance criteria → принять частичный done → перечислить критерии и evidence → неполная приёмка → brief длиннее → оставить |
| P5 | `read` | literal owner → назвать files без адресов → дать точные адреса → search/retrieval loss → требует подготовку root → оставить |
| P6 | `delta` | literal owner → повторить известное или сузить только до current read → дать лишь недоступное в files → лишняя нагрузка/drift → root обязан различить delta → оставить исправленную строку |
| P7 | actor estimate after brief | literal owner order → оценить неполный assignment → считать после brief → скрытые units → один обязательный estimate → оставить |
| P8 | root estimate | owner root-window → оценить только worker → проверить next root decision → root overload → отдельный estimate → оставить |
| P9 | set contents and price | owner 2026-08-10:21,23 → считать только instruction bullets → включить result/work/instructions/price → ложная лёгкость → расширяет объект счёта → оставить |
| P10 | independently forgettable unit | wave-1 count failure → считать строки/буллеты → считать смысловые units → замаскированная перегрузка → требует judgment → оставить |
| P11 | releasing boundary | wave-1 counterexample → декоративная делегация → требовать фактическое снятие units → root получает старую работу плюс integration → закрывает бесполезные поручения → оставить |
| P12 | rollback | v10 + Opus falsifier → лишь заблокировать новый ход → вернуть к первому stale result → downstream остаётся построенным на старом входе → одна общая recovery-обязанность → оставить |

Platform metadata: `display_name` — существующий runtime label;
`short_description` — точная projection R1; `default_prompt` — русская кнопка
того же before-trigger; `allow_implicit_invocation` — существующая platform
policy. Новых решений они не добавляют.
