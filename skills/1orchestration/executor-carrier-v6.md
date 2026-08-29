# Executor carrier — draft-v6 probe

## Scope and owners

- Outcome: evidence-backed audit of `draft-v6/references/brief.md` against the two named live chat-recall owners.
- Owner A: `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-29-152721-codex-01a04d0e.md` — central orchestration function.
- Owner B: `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-29-152644-codex-01a04d0d.md` — task-file/brief exception and mandatory owner reads.
- Target: `/Users/triton/Documents/GitHub/agentic-research/skills/1orchestration/draft-v6/references/brief.md`.
- Write boundary: this carrier only; nested worker has no write ownership.

## Provisional brief

- `goal/outcome`: independently map every material owner criterion to exact text/address in the target.
- `done_when`: complete criterion-by-criterion pass/fail map with addressable quotations and gaps.
- `read`: Owner A, Owner B, and Target at the exact paths above.
- `delta`: evaluate only this target; do not read review/refactor/evidence/history; make no edits; return evidence to root.

## Active-unit ledgers

- Worker: 14 units; one bounded comparison, low coupling, one-return horizon; verdict `manageable`.
- Root: 18 units; medium coupling, but the carrier externalizes sequence/state; verdict `manageable`.

## Shape and launch map

- Shape: root plus exactly one staged ordinary read-only worker.
- Capability basis: local file reading and bounded textual evidence mapping are sufficient; no specialized controller, external search, or write access is required.
- Order: carrier launch transition → spawn → mandatory wait → return/barrier transition → root verification → acceptance transition → integration transition.
- Barrier: integration is forbidden until the mandatory worker return is received.
- Return channel: nested final response containing exact criterion addresses, pass/fail verdicts, and gaps.
- Acceptance owner: root executor; root separately verifies load-bearing claims.

## Transition 1 — launch authorized

- State: `ready_to_launch`.
- Basis: both ledgers are manageable; one-worker shape is sufficient and required by the scenario; recovery ledger now exists before launch.
- Evidence: draft-v6 route completed through `carrier.md`; launch map is recorded above.
- Next dependent move: spawn exactly one nested read-only worker with the provisional brief, then wait for its mandatory return.

## Transition 2 — worker launched

- State: `waiting_at_mandatory_barrier`.
- Actor: `/root/executor_v6/brief_owner_audit`.
- Contract: independently read exactly Owner A, Owner B, and Target; map every material owner criterion to exact target text/address with `pass`/`fail`; report gaps; no writes.
- Evidence: one successful `spawn_agent` return naming `/root/executor_v6/brief_owner_audit`; no other nested actor was spawned.
- Next dependent move: wait for the mandatory final evidence packet. Root verification and integration remain barred until it arrives.

## Transition 3 — mandatory return received, barrier held

- State: `return_received_root_verification_pending`.
- Basis: the worker returned an addressable criterion map and an overall `fail`; root has not yet accepted it.
- Barrier status: held. Root verification is the next move; integration remains forbidden.
- Exact nested return:

> Проверены только три заданных файла, без изменений.
>
> Обозначения:
>
> - `O1` — `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-29-152721-codex-01a04d0e.md`
> - `O2` — `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-29-152644-codex-01a04d0d.md`
> - `B` — `/Users/triton/Documents/GitHub/agentic-research/skills/1orchestration/draft-v6/references/brief.md`
>
> ### Central orchestration function
>
> Все критерии ниже происходят из `O1:20`.
>
> | Критерий владельца | Адрес в `brief.md` | Вердикт |
> |---|---|---|
> | Декомпозировать когнитивную работу в более выполнимые задачи — «развития когнитивной работы на более выполнимые списки задач» | Нет текста о декомпозиции, списке или разбиении работы. | **fail** |
> | Анализировать, сколько вещей actor должен удерживать — «проанализировать, сколько вещей он должен держать в голове» | `B:11` лишь говорит, что одна выдержка «считается в active set»; анализа всего набора нет. | **fail** |
> | Оценивать число влияющих инструкций наряду с субъективной сложностью — «помимо субъективной сложности… оценивать количество инструкций» | Нет сложности, подсчёта или сопоставления факторов. | **fail** |
> | До brief прочитать всё, что влияет на качество — «обязательно должен прочитать все, что может повлиять» | `B:3`: «root прочитал owner map» не устанавливает ни полноту, ни обязательность чтения всех влияющих owners. | **fail** |
> | Правильно сформулировать цель actor-а | `B:6`: «`goal/outcome` — состояние, которое должен сделать истинным actor». | **pass** |
> | Задать acceptance evidence | `B:7`: «`done_when` — evidence, которое доказывает outcome». | **pass** |
> | Обеспечить соблюдение **всех** критериев принятия | `B:7` определяет `done_when`, но не требует полноты покрытия всех критериев. | **fail** |
> | Не перегружать известными из owners деталями | `B:9–10`: «только task-specific информация»; «Доступный owner не пересказывай». | **pass** |
> | Передавать только delta, которой нет в файлах | `B:9`: «`delta` — только task-specific информация, отсутствующая в owners». | **pass** |
> | Обязательно назвать файлы/адреса, которые actor должен прочитать | `B:8`: «`read` — адреса принятого owner ledger-а». | **pass** |
> | После формирования brief оценить общий instruction load | `B:11` учитывает только отдельную выдержку; шага оценки общего load нет. | **fail** |
> | Использовать порог около 20 единиц | Числовой порог отсутствует. | **fail** |
> | Учитывать снижение исполнения примерно до 75% сверх порога | Зависимость качества от нагрузки отсутствует. | **fail** |
>
> ### Task-file / brief exception и mandatory owner reads
>
> | Критерий владельца | Адрес в `brief.md` | Вердикт |
> |---|---|---|
> | Уверенный бюджет — до 20 единиц (`O2:24`) | Порог отсутствует. | **fail** |
> | Делить работу по границе «одна задача — один агент» (`O2:25`) | `B:6` использует единственное `actor`, но явной границы one-task/one-actor нет; соседний смысл не засчитан. | **fail** |
> | В самой задаче повторять самые важные инструкции (`O2:25`) | `B:10–11` лишь разрешает выдержку, если её уже требует receiving owner; обязательного повторения critical context нет. | **fail** |
> | Task-файл предназначен агенту и рассматривается как его prompt (`O2:26`) | `B:3–4` описывает brief, «достаточный для первого решения», а не task как prompt полного выполнения. | **fail** |
> | У задачи обязательно есть цель (`O2:27`) | `B:6`: обязательное поле `goal/outcome`. | **pass** |
> | Actor должен опираться на цель при выполнении (`O2:27`) | Наличие поля не устанавливает цель как управляющий ориентир выполнения. | **fail** |
> | У задачи есть критерии выполнения (`O2:27`) | `B:7`: `done_when` с доказательством outcome. | **pass** |
> | У задачи есть ограничения (`O2:27`) | Поля или правила для constraints нет. | **fail** |
> | Явно выделять самые важные файлы (`O2:28`) | `B:8` требует адреса owner ledger, но не отбор «самых важных». | **fail** |
> | Читать только релевантные файлы, а не всю документацию (`O2:28`) | Ограничения чтения по релевантности нет. | **fail** |
> | Встраивать несколько конкретных критически важных строк (`O2:28`) | `B:10` упоминает «требуемую… выдержку», но не требует выбрать несколько critical lines. | **fail** |
> | Сохранить исключение из delta-only для критичных owner-инструкций (`O2:25,28`) | `B:10` делает исключение только условным — когда выдержку уже требует receiving owner; общего task/brief exception нет. | **fail** |
> | Отбирать информацию по принципу surprise (`O2:29`) | `B:9` отбирает по отсутствию в owners; это другой критерий, явного surprise нет. | **fail** |
> | Подсвечивать load-bearing условия качественного выполнения (`O2:29`) | Нет отдельного требования выделить критичные условия качества. | **fail** |
>
> `B:10–11` всё же содержит полезную механику: разрешённая owner-выдержка сохраняет адрес и входит в `active set`. Но она не заменяет обязательное исключение владельца: task/brief должен сам повторять наиболее важные инструкции.
>
> Процессные решения `O1:18–19` и `O2:19–23,30` не оценивались как контракт `brief.md`: они относятся к scope рефактора, языку planning-family, approval и внешней проверке.
>
> **Итог: fail.** Brief фиксирует полезное ядро `goal / done_when / read / delta`, но пропускает центральную функцию orchestration: cognitive decomposition, полный mandatory owner read, подсчёт active instruction set, порог около 20 и реакцию на превышение. Критичнее всего, строгий delta-only в `B:9–10` не содержит обязательного task/brief-исключения для дублирования самых важных owner-инструкций.

- Next dependent move: read the routed acceptance protocol, then root-check load-bearing claims against numbered source lines.

## Transition 4 — return accepted

- State: `accepted_ready_to_integrate`.
- Acceptance verdict: `accept`.
- Basis: the return satisfies `done_when`: it covers material criteria individually, gives exact owner/target addresses, assigns `pass`/`fail`, names gaps, and reports an overall verdict. It is evidence rather than progress narration.
- Root load-bearing check:
  - Target `brief.md:6-11` directly contains `goal/outcome`, `done_when`, `read`, delta-only, no-owner-restatement, and an addressed live excerpt counted in the active set.
  - Owner A `:20` directly requires cognitive decomposition, load analysis, all influencing reads, acceptance completeness, goal quality, delta-only briefs, an approximately-20 threshold, and degraded execution above it.
  - Owner B `:24-29` directly requires the ≤20 budget, one-task/one-agent boundary, deliberate repetition of critical instructions, agent-prompt audience, goal/criteria/constraints, selected relevant files and critical lines, and surprise/load-bearing selection.
  - Those explicit requirements are absent from Target `:3-11` except for the five positive mechanisms above. Target `:10-11` is accepted only as a partial addressed-excerpt mechanism, not as the mandatory task-file exception.
- Worker authorship check: worker did not author or edit the audited target or owners and had no write ownership.
- Barrier status: crossed only now, after mandatory return and root verification.
- Next dependent move: read the routed integration protocol and synthesize the accepted evidence without editing candidate/runtime/owner files.

## Transition 5 — integration complete

- State: `complete`.
- Integrated verdict: Target `brief.md` fails the two-owner audit materially.
- Accepted passes: goal/outcome; outcome-proving `done_when`; owner-ledger read addresses; delta-only task-specific content; avoiding owner restatement; an addressed required live excerpt counted in active set. Across the worker's source-specific rows this is 7 passes of 27 rows (5/13 for Owner A, 2/14 for Owner B); repeated rows preserve separate owner provenance.
- Accepted failures: cognitive decomposition; full load analysis; subjective-complexity plus instruction-count evaluation; explicit guarantee that every influencing owner is read at this stage; completeness of acceptance criteria; post-brief overall load assessment; approximately-20 threshold and degraded-quality consequence; one-task/one-agent; mandatory repetition of critical instructions; task-file-as-agent-prompt; goal as operating reference; constraints; selecting only the most relevant files; embedding selected critical lines; explicit delta-only exception; surprise selection; load-bearing quality conditions.
- Nuance: Target `:10-11` is useful and compatible with an exception, but only preserves a quote when a receiving owner already requires it; it does not itself establish the mandatory task-file/brief exception or its selection rule.
- Overall evidence: exact nested return is preserved in Transition 3; root verification and acceptance are preserved in Transition 4.
- Files changed: this carrier only. Candidate, runtime, owner, review, refactor, evidence, and history files were not edited.
- Durable transfer: intentionally not performed because the scenario makes this carrier the only write-owned artifact and forbids candidate/runtime/owner edits.
- Gaps/blockers: no execution blocker. The only audit gap is locality: some omitted owner criteria may be implemented by other draft-v6 references, but this audit was expressly scoped to `brief.md`, so they remain failures for this file rather than claims about the whole skill.
