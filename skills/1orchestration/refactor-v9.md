# Семантический проход 1orchestration — v9

Status: `terminal ready candidate; official заморожен`.

## Owner boundary

- `_ops/chat-recall/2026-08-29-163434-codex-01a04d4a.md:35` разрешает
  исправлять recheck-кандидаты до готовности без переусложнения.
- Текущий запрос запрещает установку этой будущей exact версии.
- Active set считается по реально действующему режиму и сохраняющимся
  обязательствам; reference-дробление ради числа запрещено.

## Commander's intent

Функция: перед поручением или разделением перегруженной работы дать каждому
участнику выполнимый связный набор, сохранив у root общую цель, owners и
доказуемую приёмку.

Уникальный контекст: root один видит общий путь; поручение добавляет нагрузку
и actor-у, и root, поэтому лишнее деление может ухудшить исходную проблему.

Три цели: выполнимые наборы с допустимым root-work; source-bound brief без
второго канона; только актуальный all-pass открывает зависимость.

## Один semantic pass

v8 перечислял capability, actor/root estimates, unit definition, soft `20`,
root-work, discard boundary, complexity gate и re-estimate как отдельные
runtime-решения. Первая v9-редакция ошибочно склеила те же предикаты в длинный
шаг и получила буквальный count `43`. Исправленная редакция убрала каталог
форм и подняла выбор в одну цель: делегировать только через простейшую
способную границу, которая реально освобождает часть набора участника.

Сохранены явными только невыводимые швы:

- четыре поля brief;
- отдельная оценка каждого actor-а и следующего решения root;
- независимо забываемая единица и мягкий ориентир `20`;
- capability каждого actor-а и следующего решения root;
- проверка current evidence и all-pass barrier;
- возврат к первому неактуальному результату после изменения основания.

References не добавлены: prepare, choose, accept и invalidate — короткие
условные режимы одного решения, а не самостоятельные knowledge-пакеты.

## Предварительный mode-specific count

Считаются уникальные одновременно применимые условия body; повтор цели в её
точном интерфейсе второй единицей не считается. Task/source units прибавляются
отдельно для конкретного участника.

| Режим | Вход → выход | Active units |
| --- | --- | ---: |
| prepare brief | известна работа → source-bound brief | 8 |
| choose root-work | brief готов → выполнимый root-набор | 9 |
| choose direct | brief готов → один способный actor и root gate | 9 |
| choose split | brief готов → меньшие наборы и root gate | 9 |
| accept return | возврат есть → dependency open/closed | 4 |
| upstream change | основание изменилось → затронутая цепочка current | 4 |

`split` не умножает instruction units тела по числу actor-ов; реальные
task/source units считаются отдельно для каждого actor-а и root. Если такой
набор превышает мягкий ориентир, candidate требует другую выбранную форму, а
не reference ради числа.

## Preservation map

| v8 смысл | v9 адрес | Решение |
| --- | --- | --- |
| root читает всё влияющее | шаг 1 | сохранён |
| outcome/done/evidence/read/delta | шаг 2 | evidence объединено с done_when |
| capability + actor/root estimates | цель 1 + шаг 3 | сохранено |
| active unit + soft 20 | шаги 4–5 | сохранено |
| root-work | цель 1 | выводимо: без полезной границы root не делегирует |
| boundary реально снимает units | цель 1 | сохранено |
| simplest justified form | цель 1 | сохранено |
| re-estimate changed form | шаги 3 и 6 | новая форма возвращает к своей оценке |
| authority owners | цель 2 | сохранено через addresses/no-second-canon |
| current evidence + all-pass | цель 3 | сохранено одной точкой приёмки |
| upstream currentness | цель 3 + шаг 6 | сохранено |

## Agent-default audit снятых строк

- Discard-rule возвращён после trajectory-контрпримера: выполнимый split мог
  дублировать sources и добавить reconciliation. Goal capability этого не
  предотвращает.
- Без runtime complexity-rule простейшая форма остаётся прямой целью, а
  authoring counterfactual принадлежит `1skill-creation`. Runtime actor не
  должен повторно аудировать дизайн скила.
- Без отдельного re-estimate-rule оценка относится только к выбранной форме;
  сменившаяся форма не имеет действующей оценки и не удовлетворяет шагу 3.
- Evidence каждого `done_when` и root all-pass оставлены разными швами: brief
  может перечислить ожидаемое evidence, не проверив его актуальное состояние.

## Falsifiers

- Checker показывает independently violable смысл v8, который v9 не выражает
  ни целью, ни оставшимся швом.
- Чистый исполнитель принимает форму без отдельной оценки actor/root, считает
  `20` hard cap, делит без уменьшения набора либо открывает dependency без
  актуального evidence каждого обязательного критерия.
- Любой реальный режим требует больше `20` уникальных body units до добавления
  task/source units.

## Terminal check

Exact manifest:
`66549ef96831892b5c96ac152b0de923c0fcde45da7a992b3b38ce65bb600dfe`.

- Trajectory checker: findings `[]`; mode-count
  `prepare 8 · root-work 9 · direct 9 · split 9 · accept 4 · upstream 4`.
- Clean executor: `behavior_pass`; в реалистичном case каждый actor/root
  остался ниже `20`, weak return не открыл dependency, source change вернул
  только затронутую цепочку.
- Literal checker: четыре принятые неоднозначности — outcome общей цели вместо
  поручаемого результата; уже полученное вместо требуемого evidence;
  назначенный вместо предполагаемого actor-а; `передающий` вместо любого
  участника, реально сбрасывающего units.

По `check-approve.md` это второй repeat. Candidate не изменён после terminal
verdict; residue передан явно, новый цикл автоматически не запускается.

## Новый bounded wording repair

По отдельному поручению оркестратора применены только четыре ранее принятые
локальные коррекции:

- `outcome` сужен до поручаемого результата, связанного с общей целью;
- brief называет требуемое evidence, а не требует уже полученное;
- до выбора формы оценивается каждый предполагаемый actor;
- unit-release допускает любого участника, а не только передающего.

Архитектура, поля, цели, references и предварительные mode counts не менялись.

## Terminal wording-repair check

Exact manifest:
`e92af4190ce42843eb5c47a2f2a6099cbb5f68305dee783d5799d14926a48acd`.

- Literal checker: findings `[]`.
- Trajectory checker: findings `[]`.
- Clean executor: `behavior_pass`; required evidence в brief и obtained
  evidence при acceptance не смешаны.
- Mode counts обоих checker-ов совпали:
  `prepare 8 · root-work 9 · direct 9 · split 9 · accept 4 · upstream 4`.

Candidate готов к предъявлению exact bytes. Установка этим циклом запрещена.
