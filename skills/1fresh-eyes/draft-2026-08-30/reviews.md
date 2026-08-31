# Independent reviews — 1fresh-eyes — 2026-08-30

## Входы

- Immutable `1skill-creation` snapshot:
  `baseline-1skill-creation-9bf/**` →
  `9bf11f64b436d313d979cba822b684f502e8e40e5f15a12f78cbd914ca29a518`.
- Reviewers: отдельные clean-window instruction checker и trajectory checker;
  выводы друг друга до terminal ответа им не показывались.
- Round 1 candidate:
  `2688fc52f8aa0ec7aebe3f98abc6c2b6040c8ffcc289f01d72eea9b4d39e45e5`.
- Round 2 candidate:
  `3aa8e5321a0d8d2e4edcf5fcf54996ed9746af6ccf0a74d87077499d1740d12c`.
- Current post-repeat candidate:
  `19defa11a49eb7d632157f88bf85279d3843efd96dabccce8006cb35b5228f59`.

## Instruction checker

Round 1 findings:

- самостоятельные предикаты были скрыты в длинных строках — принято как
  форматная правка без новых стадий;
- active sets `23–30` превышали threshold — число сохранено как residual, но
  микростадии отклонены по прямому owner-boundary против вредного буквализма;
- четыре предложения в трёх целях — исправлено до трёх;
- Product Frame теряла explicit Fresh Eyes trigger — исправлено;
- owner-цитата о трёх агентах могла запретить named mode — ограничена
  `mode: panel`;
- steering не маршрутизировал missing check и неоднозначно останавливался —
  trigger сужен до обязательного проверочного элемента, stop уточнён;
- одинаковые evidence paths не имели terminal trace — добавлен
  `panel_incomplete`.

Round 2 findings:

- packet-stage `panel_incomplete` не доходил до controller stop — исправлено;
- stage map не отражала новые outputs и counts — исправлено в `authoring.md`;
- часть независимых предикатов всё ещё делила строки — разнесено без новых
  смыслов;
- source zone могла совпасть с `Main уже читал` — явно запрещено.

Verdict: буквальные дефекты двух разрешённых rounds локально исправлены;
post-repeat exact candidate не получает третий independent audit по repeat-cap.

## Trajectory checker

Round 1 эталон:

`обычное продолжение → trigger → neutral frozen anchor → four isolated paths
or one native specialist → verified non-voting handback or honest stop`.

Findings приняты:

- непроверенный decision-changing claim и неразличимые evidence paths теперь
  дают terminal `panel_incomplete`;
- невозможность назвать четыре релевантные зоны теперь останавливает panel, а
  не запускает ритуальное дробление;
- missing `falsifier` / source anchor маршрутизируется в retained correction.

Round 2 finding:

- retained correction могла остановиться без типизированного выхода — добавлен
  `correction_incomplete`, который controller превращает в named blocker либо
  `panel_incomplete`.

Verdict: эталонная траектория сохранена; последний terminal seam исправлен
после второго repeat и проверяется structural checks + exact clean run, но не
третьим independent reviewer.

## Не принято

- Дробление controller-а на микростадии ради `≤20`.
- Новый `lane-contracts.md`, повторяющий владельцев role definitions.
- Требование разных verdicts вместо разных evidence paths.
- Scoring, majority vote, confidence thresholds и автоматическая acceptance.

## Поздний owner-критерий простоты

`_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:33` запретил
переусложнять refactor. Exact candidate `f0dd…` был остановлен до завершения
clean-run: terminal routing повторялся в нескольких ветках, а `named.md`
оставался отдельным малым runtime-файлом.

Новая форма:

- поглотила повторные stops одним global terminal rule;
- удалила `named.md` и runtime-цитаты;
- вернула tool calls из механически раздробленных строк в один exact interface;
- сохранила пять самостоятельных references;
- добавила только no-delegation seam, потому что clean-run фактически наблюдал
  два nested Claude launches в session `e1057e0b-5ce6-419c-82bd-e2fdf7267d5c`.

Эта exact версия требует новой bounded пары reviews и clean-run; прежние
verdicts остаются loss evidence, но не acceptance новой версии.

## Simple candidate reviews

Round 1 на `0c927ffa…`:

- trajectory reviewer снял требование четырёх never-read zones: paths теперь не
  копируют только текущий рабочий корпус Main;
- instruction reviewer ограничил panel handback panel-режимом, вернул
  unavailable named blocker и wrong-premise correction, уточнил derivation
  конечного результата, удалил `Кругов пройдено`, заменил undefined `stable`
  terminal-состоянием и потребовал full packet для нового correction-потока.

Round 2 на `773a939d…`:

- trajectory findings: none;
- instruction reviewer нашёл только порядок unavailable-check, stale
  synthesis trigger и несинхронные history counts/maps. Check перенесён в
  packet-stage; trigger и evidence синхронизированы.

Repeat-cap исчерпан. После второго review изменены только найденные им
unavailable-check order, synthesis trigger и evidence counts/maps. Третья
reviewer-пара exact `19def…` не запускается, поэтому буквальное требование двух
independent checkers на последнем байте остаётся непокрытым.

## Exact behavioral trials

- Panel clean-run exact `19def…` честно завершился `panel_incomplete`: Claude
  bridge после успешной auth-диагностики не вернул terminal report и
  session/model receipt в bounded window. Нативные линзы и synthesis не
  запускались после terminal barrier.
- Named clean-run exact `19def…` запустил ровно один fresh `auditor` с
  `fork_turns: none`; panel, Premortem и synthesis отсутствовали. Родной
  результат — `incomplete`: доказательств полного panel happy path нет.

Обе пробы подтверждают честный stop и named short-circuit, но не доказывают
полный cross-family panel happy path. Exact candidate поэтому не готов к
approval или installation.

## Completed panel and semantic compression

Штатный `claude_ask` позднее вернул Opus 5 report на exact `19def…`; после него
три clean native lenses завершились, а source-bound ошибка Solvent была
исправлена в том же потоке. Полный receipt — `panel-run-19def.md`.

Non-voting handback выбрал узкое semantic compression. Runtime candidate стал
`65628c153ddf0b70baf34d1676bc90d9733842fbd0c46f012104e148be9b0e43`.
Изменены только commander's intent и пять выводимых reminders; roster, exact
runtime bridges, freeze-order, evidence separation, bounded waves, retained
correction, source verification, terminal outputs и named short-circuit не
изменены.

`65628…` получил первую новую checker-пару:

- trajectory checker — findings `none`, все обязательные runtime-свойства
  сохранены;
- instruction checker — exact counts и семь runtime-находок: пять
  неоднозначностей приняты, duplicated correction route сжат, буквальное
  возвращение owner quotes отклонено по поздней owner-границе простоты.

Instruction repeat `c66d6…` нашёл три scope-шва; они исправлены без новых
условий. Candidate `822c0…` получил финальную независимую пару на exact bytes:

- trajectory checker — findings `[]`;
- instruction checker — findings `[]`, fingerprint `822c0…`, YAML 13/13,
  runtime links 10/10 и все active sets `≤20`.

Completed panel `19def…` остаётся наблюдаемым causal input семантического
сокращения. По последнему owner-критерию exact final acceptance дают две
независимые проверки; дополнительный panel run новых байтов не требуется.
