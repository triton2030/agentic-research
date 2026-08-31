# Упрощение 1orchestration — v8

Status: `terminal checked no-change candidate; official заморожен`.

Официальный owner и projections заморожены до безусловного утверждения exact
candidate.

## Новый owner-критерий

`_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md`,
`2026-08-30T19:25:58+05:00`:

> «Еще, пожалуйста, проследи за тем, чтобы агенты не переусложняли весь
> процесс.»

Рабочая граница: runtime-сложность остаётся только при конкретном
counterfactual harm без неё; authoring/check bureaucracy в runtime не
переносится, а active-set budget не обходится размножением стадий.

## FAST и commander's intent

- **Зачем выше:** сохранить качество и общую пользу работы при передаче части
  мышления другому actor-у.
- **Функция:** перед поручением или разделением перегруженной работы получить
  актуальный source-bound brief, посильные наборы выбранных actor/root и
  доказанный результат без дополнительного control-plane.
- **Уникальный контекст:** root один видит полный путь; сама делегация добавляет
  prompt к активной работе, поэтому больше текста, стадий и агентов может
  усилить перегрузку.
- **Три цели:** brief не становится вторым каноном; выбранные actor/root
  посильны в минимальной форме; owners сохраняют authority, а зависимость
  открывает только доказанный актуальный результат.

## Clean-room и zero-based design

Тот же чистый исполнитель получил только обновлённый intent, не читал старый
пакет, v7, history или reviews и независимо выбрал один `SKILL.md` без
references. Смысловой результат:
`draft-v7-simple-cleanroom/semantic-draft.md`.

Root применил authoring-режимы:

- `skill-short-description`: сохранён более короткий уже доказанный English
  trigger; use — назначение subagent или реальное деление перегруза, skip —
  посильная root-only работа, near-miss — обычный checklist без деления.
- `behavior-protocol`: сохранены только три причинные зависимости — sources до
  brief, brief до оценки выбранных actor/root, current evidence до dependency.
- `reference-files`: references сняты; один короткий runtime-момент не требует
  независимых режимов.
- `agent-defaults`: каждая оставшаяся добавка проходит counterfactual map ниже.

## Counterfactual harm оставшейся сложности

| Добавка | Дефолт → механизм → изменяемое решение | Вред без строки | Цена строгости |
| --- | --- | --- | --- |
| Root читает sources до brief | ссылка выглядит достаточной → direct read → criteria извлекаются до prompt | owner-критерий исчезает | root платит чтением |
| `outcome` | тема выглядит целью → concrete state → actor знает, что сделать истинным | полезная, но не та работа | одно поле |
| Полный `done_when` | агент выбирает удобный subset → full local set → scope completion не угадывается | неполный результат выглядит готовым | длиннее brief |
| Evidence каждого критерия | самоотчёт выглядит подтверждением → per-criterion evidence → criterion проверяем | уверенный текст заменяет состояние | больше критериев в prompt |
| `read` | summaries выглядят каноном → exact addresses → actor читает owners | prompt становится second truth | actor тратит чтение |
| Missing-only `delta` | полезно пересказать всё → absence test → передаётся только недоступный контент | owner и prompt расходятся | root должен проверить отсутствие |
| Capability actor-а | малый набор выглядит достаточным → capability gate → actor обязан выполнить весь `done_when` | посильный, но неспособный actor | меньше допустимых actor-ов |
| Actor estimate после brief | считают только исходную задачу → post-brief estimate → prompt входит в load | скрытый overload | приблизительный счёт |
| Root estimate отдельно | worker-load заслоняет coordination → separate estimate → форма учитывает next root decision | root не сможет принять/свести | второй счёт |
| Active-unit definition | требования склеивают символически → independently-forgettable test → granularity проверяема | число занижено | приблизительность остаётся |
| Soft `20` | число выглядит законом → soft signal → verdict остаётся judgment | hard-cap создаёт вредный split | нет автоматического решения |
| Root-work | trigger выглядит обязательной delegation → explicit valid form → root может оставить работу | агент создаётся ради процесса | одна альтернатива |
| Drop-units boundary | любое деление выглядит прогрессом → discard test → split покупает cognitive reduction | coordination растёт без разгрузки | часть задач не делится |
| Harm gate сложности | completeness выглядит качеством → counterfactual test → добавка требует material benefit | skill строит собственную бюрократию | меньше страховочных правил |
| Re-estimate configuration | старая оценка выглядит reusable → configuration change gate → считаются выбранные actor/root | новый actor наследует чужую нагрузку | повтор оценки |
| Authority owners | generic skill выглядит главным → owner boundary → topology/execution не перехватываются | второй controller/runtime | меньше контроля у общего skill |
| Root evidence check | наличие expected evidence выглядит pass → actual check → факты сверяются | false acceptance | root сохраняет работу приёмки |
| All-pass dependency gate | частичный успех выглядит достаточным → barrier → downstream ждёт все обязательные criteria | ошибка каскадирует | зависимость ждёт |
| Upstream currentness | старые outputs выглядят пригодными → affected-chain refresh → brief/estimates/acceptance снова current | отменённое основание управляет ходом | адресная пересборка |

Ни одного отдельного поля, reference или runtime-перехода без полной цепочки
нет. Metadata оправдана platform surface: `display_name` — UI discovery,
`short_description` — routing, `default_prompt` — русская invocation,
`allow_implicit_invocation` — действующий trigger policy.

## Preservation map

| Смысл predecessor/v7 | v8 | Решение |
| --- | --- | --- |
| Root читает всё влияющее | шаг 1 | сохранён; отдельная impact-map снята как выводимая из brief |
| Полный source-bound brief и only-delta | шаг 2 | сохранён интерфейс, отдельный reference снят |
| Count после brief; actor/root отдельно; capability; soft `20` | шаги 3–7 | сохранено одной приблизительной оценкой, полный ledger не режим |
| Decompose/shape/no-delegation/drop-units | цель 2 + шаги 8–11 | поглощено выбором минимальной формы |
| Specialized topology/acceptance и runtime authority | цель 3 | поглощено общей authority-boundary |
| Verify/accept/dependency/rework | цель 3 + `done_when/evidence/delta` | поглощено current evidence-gate и общей only-missing delta |
| Stale invalidation | шаг 14 | сохранена только upstream-currentness без машины состояний |
| Map/assign/execute/carrier/integrate | live controller/runtime/task owner | сняты как второй control-plane |
| Six v7 references и route-cascade | — | сняты: их логика поместилась в один runtime-момент; дробление не снижало активный набор |
| Authoring checkers/receipts/approval | history + `1skill-creation` | не встроены в runtime |

## Active set

Runtime: один `SKILL.md` и platform metadata, references отсутствуют. После
двух буквальных пересчётов консервативный уникальный active set `SKILL.md` —
`21` единица: `2` знания контекста, `1` не повторённая протоколом
authority-boundary и `18` атомарных protocol units из таблицы выше.

Source-bound/no-second-canon, selected-configuration feasibility и
current-evidence цели не считаются второй раз поверх реализующих их полей и
проверок. Codex metadata содержит `4` interface/policy declarations, но не
добавляет runtime-инструкций в body.

`21` честно оставлен на единицу выше мягкого ориентира: удаление любой из них
открывает конкретный вред из таблицы, а новый reference лишь спрятал бы тот же
одновременно применимый набор и нарушил simplicity criterion.

К нему в реальном случае прибавляются атомарные task/source units выбранного
actor-а и root. Сам skill не заявляет универсальный total: если итог около или
выше мягкого `20`, агент меняет форму только когда граница действительно
снимает единицы.

## Снятая сложность

От v7 удалены шесть references, отдельные orient/brief/count/budget/shape/accept
route-states, impact-map, discovery-gap protocol, full ledger как артефакт,
named verdict vocabulary, explicit rework route и stage-by-stage invalidation.
Остались один runtime-файл, четыре поля brief, приблизительная оценка
выбранных actor/root, authority и evidence/currentness.

## Terminal no-change verdict

Exact manifest `304feb88f1842b04fbe93af4cddf859df28c17620383941e5399cbaa51390074`
прошёл literal checker и realistic clean-run. Trajectory checker нашёл один
материальный путь побега: формула `done_when — все применимые критерии` не
называет источник полноты, поэтому агент может пропустить criterion одного
элемента `read`, проверить весь неполный список и открыть зависимость.

Обязательный Fresh Eyes разложил развилку иначе. Полная предлагаемая формула
могла вернуть удалённую impact-map как неявное соответствие каждого адреса
критерию и сделать нагрузку зависимой от числа файлов. Поэтому перед правкой
проведён адресный no-edit clean-run на текущем candidate.

Исполнитель с чистым окном получил exact package, актуальный
`1skill-creation` и применимые owner sources, но не history, reviews,
predecessor или предлагаемую правку. Он самостоятельно выделил малозаметный
языковой owner-критерий отдельным `done_when`, показал его покрытие в обоих
runtime-файлах и не смог открыть all-pass при его нарушении. Исправленный
терминальный trace сохранён в `clean-run-v8-round4.md`.

Вердикт: `no-change`. Trajectory residue не принят как runtime-находка, потому
что его предсказанный вред не проявился, а действующий commander's intent уже
меняет нужное решение. Candidate bytes и active set `21` не изменились;
impact-map, новый reference, стадия или completeness-line не добавлены.
