# Evidence — прогон рефактора 2026-08-09

Сценарий обоим агентам (sonnet, сухой прогон): «составь план миграции
каталога шаблонов на новую схему», тревога владельца — потеря персонализаций.

## Со скилом (SKILL.md + references)

- до файлов: chat-recall → принципы через `1use-principles` → проба режима →
  «да» владельца на обоснование;
- создаёт контракт + `context.md`; тревога — в Проблему с адресом recall,
  отпавшие ходы — с причиной;
- запреты названы верно (происхождение, без хроники, ссылка вместо копии);
- противоречащее свидетельство → перечитать контракт → классифицировать →
  пересобрать затронутую часть, не патчить → возврат в Wayfinding при новом
  материальном неизвестном.

## Контроль без скила (чтение skills запрещено, 0 tool uses)

- создаёт только `task.md`; «второй файл не создаю» — замысел остаётся в чате;
- «да» до файла знает из проектных инструкций, но триаду обоснования не несёт;
- при противоречии — останавливает ветку и эскалирует; пересборки затронутой
  части и цикла классификации нет.

Дельта скила: `context.md` с границей допуска и цикл
классификация → пересборка существуют только со скилом. Сжатие тела
(~26 → ~12 носителей) поведение не потеряло: детали агент вытянул из
владельцев-references по указателям.

Оговорка: первый прогон (до рефактора, той же парой) имел загрязнённый
контроль — агент сам нашёл скилл на диске; этот контроль чист.

## Ревью третьей семьи (Kimi k3, Hermes, session 20260809_181132_c1713a)

Вердикт: «годен с правками» — пять тезисов владельца покрыты, но два места
были декларациями без механизма. Принято пакетом Р1–Р5 («да» владельца):

- Р1: допуск строки context.md получил процедуру «назови owner-а, у которого
  проверил отсутствие; не можешь — ссылка»;
- Р2: жёсткий переход и цикл modes читают «контракт и context.md»;
- Р3: правка чужого контракта по памяти — строка в карте сбоев (снят
  принятый риск cut.md);
- Р4: «Отпавшие ходы» — мёртвую ветку вычёркивай, блок не хроника;
- Р5: путь к архиву перекосов в decompose.md был мёртвым; починен на
  найденный `~/Documents/GitHub/agentic-research/...`.

Каждый дефект перед принятием сверен чтением первички, не принят на веру.

## 2026-08-18 — рефактор «карта эпиков»

Support envelope: Claude Fable 5 (оркестратор) + Claude fresh windows
(линзы) + Codex gpt-5.6-sol xhigh (советник, premortem-история); Obsidian
1.13.7 (Bases-проба).

Проверено исполняемо: Bases-проба (base:query вернул карту/затыки/вопросы;
скриншоты v1–v6); sync_simple_projections --check зелёный после записи.
Проверено чтением: две аудит-линзы (полное чтение 20 файлов законов каждая),
панель 4 линз, счёт инструкций (~119 → ~140 при двух новых функциях, дубли
сняты). Не проверено: routing голой фразой; comparator-прогон «создай план»
старый-vs-новый — первым живым использованием станет создание карты эпиков
MAVO; до него поведенческие claims считаются кандидатными.

## 2026-08-22 — terminal repair и внешний runtime

- Historical comparator: task `01a0236d-cbaf-72e1-95dd-0832b58fd23b` под
  прежним контрактом повторял waits без module return и называл внешний Codex
  task active из plan-status, хотя live platform этого не подтверждала.
- Codex clean-window falsifiers по installed projection:
  1) источник не разрешает handle → lifecycle только `unknown`, отправка и
  restart не разрешены; 2) два repairs не закрыли модуль → blocker в
  `status.md`, owner-only продолжение → `questions.md`; технический blocker
  без owner-choice вопроса не создаёт.
- Claude clean-window falsifiers: `claude-opus-5`, `xhigh`, blocking
  `claude_ask`, local read-only tools, `warnings=[]`; installed Claude
  projection дала те же решения в обоих runtime- и handoff-сценариях.
- Два независимых architecture-аудита нашли и закрыли потерю старого handoff
  «стоп, блокер владельцу»; corrected suffix принят обоими без структурных
  находок.
- Distribution: `sync_simple_projections.py 1planning --check` подтвердил
  shared owner, tracked Codex/Claude и обе installed projections.
- Residual: после технического blocker без owner-choice delegation не называет
  исполнителя следующей диагностики; `contract.md` всё же требует один `Next`.
  Это не входит в доказанный claim и не выдано за закрытое.

## 2026-08-22 — v2

Две независимые линзы (Sonnet «лишнее»: 9 находок; Opus «потерянное/выдуманное»
цитатами: 12+11 находок, вкл. самопротухающий снимок) → 28 обязательных
ремонтов → механическая сверка 28/28 applied, посторонних правок 0, grep-инварианты
чисты. Артефакты: mavo-short2 scratchpad session 591eecb1 (planning-rework-spec,
planning-repair-spec), codex runs 20260822T115943Z-dd5618b0 (draft2),
20260822T123325Z-7483dec7 (draft3+сверка).

## 2026-08-24 — epic/task split, frontier and quiet queue

Claim: an epic never derives a completion percentage from its open JIT task
set; a task retains percentage only for its current explicit 3–7-subtask
checklist, and that percentage is not task-closure evidence. The epic exposes
only closed/created inventory, and a `🔨` task is valid only inside the single
`🔨` launch-frontier; deferred and non-launch epics are not exemptions.

Live falsifier: mavo-short2 recall
`_ops/chat-recall/raw/2026-08-24-203833-codex-01a0346a.md` records the
Founder-approved causal repair after the live Render Core/dashboard failure.

Comparator: before the repair, `Дашборд.base` applied the subtask-counter
formula to epics and `Планы.base` applied it to tasks. After the repair, the
epic view renders `задач-готово/задач` as `N/M созданных`; the unchanged
subtask formula exists only in `Планы.base`. `map.md` names the open JIT
denominator as the reason and keeps epic closure separately gated by accepted
epic `evidence`.

Project falsifier: mavo-short2 `scripts/tests/test_check_map.py` first failed
against the regressed checker for queued frontier/later active epic, hidden
active tasks, and mutation before malformed-source rejection. Independent
critics then found the deferred, `запуск: false` and no-frontier bypasses; all
three new cases also failed before their guard existed. The final suite passed
26/26, while `scripts/check-map.py` validated the 13 live epics with zero
errors and warnings. The dashboard cases require no epic subtask progress,
preserve task progress and require the explicit `созданных` label. This proves
the project projection, not the skill text by itself.

Static acceptance: the final independent architecture audit returned
`architecture_ok: no structural findings`; the developer critic returned
`satisfied`; the acceptance audit returned `pass` with no blockers after its
earlier counterexample was converted into the three regressions above.

Distribution: `sync_simple_projections.py 1planning --write --install` wrote
both tracked and installed Codex/Claude projections; the separate
`sync_simple_projections.py 1planning --check` returned that every requested
projection matches its owner.

## 2026-08-25 — terminal updates, question integrity and closed-task history

Behavioral falsifiers in mavo-short2 first failed against the pre-repair
instrument for: an epic with no dated update; a dashboard-visible question
without origin/search trace; an answered question without separate
`ответ-опора`; a question without `срок`; and a dashboard that omitted both
closed tasks and question deadlines. After the repair the full
`scripts.tests.test_check_map` suite passed 35/35.

The live instrument validated 13 epics with zero errors and warnings.
`check-map.py --write` was hash-idempotent across every epic Markdown file.
A reversible mutation that made unmet dependencies rewrite `⏳` turned only
`test_deliberately_deferred_epic_overrides_dependency_blocking` red; restoring
the source restored the original SHA-256
`254bb021ac6cb9a21a61178db706cd763e5512cb6ae5932835f40224b0afa3c7` and the
test returned green.

The independent architecture critic first found two ownership leaks (question
files enumerated after dashboard filtering; one `опора` changing identity) and
then the missing project deadline projection. After all three corrections its
final recheck returned `architecture_ok: no structural findings`.

Distribution: the shared owner, tracked Codex/Claude packages and both
installed projections passed `sync_simple_projections.py 1planning --check`;
all five package locations passed the platform `quick_validate.py`. Exact
changed Markdown passed rumdl and both project Base files parsed as YAML.

Visual evidence remains bounded: Obsidian's Computer Use bridge kept a stale
main-pane frame after navigation, so no fresh pixel-level contrast claim is
made. The accidental empty note created by the failed Quick Switcher route and
its two empty directories were deleted immediately; filesystem checks and the
map instrument remained green.
