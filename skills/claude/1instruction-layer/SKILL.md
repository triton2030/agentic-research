---
name: 1instruction-layer
description: >
  Use when writing or auditing durable `AGENTS.md`, `CLAUDE.md`, path rules or
  repo-local instruction files; a plausible rule can otherwise load from the
  wrong owner or be obeyed in form while leaving the same agent decision
  unchanged. Recover the effective chain and design the smallest
  trajectory-changing delta; prose is not enforcement.
---

# Слой Инструкций

## Продукт И Мера

`1instruction-layer` превращает устойчивую local truth или повторяющийся провал
в одну поддерживаемую intervention для будущего агента. Проверь три product job
и чини только проваленные:

1. **Load:** нужный текст реально входит в effective chain в нужный момент и
   ведёт к одному owner-у.
2. **Steer:** на representative развилке он меняет первый наблюдаемый акт или
   decision rule, а не только словарь ответа.
3. **Prove / enforce:** проверка различает старую и новую траектории; то, что не
   может зависеть от reasoning, передано внешнему gate-у.

Мера продукта — меньше повторных коррекций и неверных веток при минимальном
prompt- и maintenance-cost. Способность пересказать правило, гладкость wording
и заполненный шаблон доказывают только видимость текста, не steering.

- **Audit/review/diagnose:** findings, evidence и exact proposed repair без edits.
- **Change/fix:** scoped repair и проверка изменённого контракта.

Instruction prose не исполняется как код: она делает одни продолжения
правдоподобнее других. Дорогой или необратимый invariant должен опираться на
permission, hook, validator, test или approval у runtime owner-а.

## Развилка До Wording

Естественный shortcut автора — сжать правильное намерение в лозунг: «думай
стратегически», «будь внимателен», «всегда проверяй». Это выглядит достаточным,
потому что смысл узнаваем человеку, но не задаёт модели точный момент, источник
решения или следующий акт; прежний default легко остаётся неизменным. `MUST`,
длинное rationale или self-check не чинят этот causal gap сами по себе.

До wording собери одну **steering cell**:

- **Fork:** наблюдаемый момент будущей задачи, где продолжения расходятся.
- **Natural continuation:** какой первый акт cold-start агента правдоподобен без
  delta и какой вред он создаёт; описывай поведение, не скрытое состояние.
- **Target continuation:** какой первый наблюдаемый акт, decision rule, source
  check или outcome должен стать естественным вместо него.
- **Control:** достаточно ли текста или ставка требует внешнего gate-а.

Cell — authoring scaffold, не обязательный формат целевой инструкции. Gate 3
инстанцирует её после подтверждения chain и owner-а; в целевой текст попадают
только load-bearing trigger, rule, owner/source, exception и stop. Если развилку
и изменившийся акт назвать нельзя, durable delta пока не доказана.

## Controller: Не Перепрыгивай Gate

Этот controller владеет методом мышления; references владеют только условной
глубиной. Держи компактное рабочее состояние
`admission → chain map → owner → steering cell → control → exact delta → proof`.
Каждый gate должен породить свой наблюдаемый результат до следующего. Пропустить
gate можно только когда его результат уже прямо подтверждён текущим evidence;
гладкий финальный текст не заменяет промежуточное различение.

Не смешивай три разных failure-а instruction hierarchy: сначала определи, какие
директивы реально относятся к задаче; затем разреши их precedence и meaning;
только потом проверяй, реализовалось ли решение в поведении. Успех позднего шага
не доказывает предыдущий. После evidence, опровергшего material premise, chain
или owner, сделай clean re-anchor: отбрось зависящие от них выводы и draft,
собери компактное состояние из подтверждённых owner facts и перестрой
downstream-решение, а не исправляй скомпрометированное рассуждение на месте.

Рабочие результаты — decision traces, не требование раскрывать приватную
chain-of-thought. Не публикуй их как длинную анкету, если пользователь не просил
audit report; они должны изменить решение и проверку, а не раздуть ответ.
Найденная слабость LLM сама по себе не заслуживает нового prose-rule:
классифицируй mitigation как `cognitive operator`, `external scaffold/evidence`
или `deterministic enforcement` и добавляй её только в принадлежащую точку.

### Gate 0 — Допусти Durable Работу

1. Назови mode: `audit` не меняет files; `change` разрешает только scoped repair.
2. Отдели одноразовое условие задачи от правила, которое должно пережить thread.
3. Для durable candidate назови основание: stable local fact, recurring
   correction/failure или hard invariant.
4. Выпиши material premises, уже принятые request-ом, старым текстом или твоим
   подходом за истину. Если отрицание premise меняет scope, owner или repair,
   проверь её по независимому owner evidence либо пометь `unknown`; сильный
   framing, повтор и уверенность автора не являются evidence.
5. Для неизвестной необходимой premise явно выбери одно: `insufficient
   evidence`, ограниченное обратимое assumption или blocker. Не достраивай её
   правдоподобным reasoning-ом и не продолжай только потому, что задача допускает
   красивый ответ.
6. Проверь `Load`, `Steer`, `Prove / enforce` по отдельности и отметь только
   проваленные jobs; не переписывай здоровый слой по инерции.
7. Если ещё выбирается instruction text vs skill/agent/hook/config, остановись:
   surface decision принадлежит `1skill-architect`.

**Результат gate:** `mode + one-off|durable + premise status + admitted evidence
+ failed jobs`. Неизвестна необходимая premise → явный assumption/stop; нет
durable основания или проваленного job → не добавляй правило.

### Gate 1 — Построй Effective Chain Map

1. Назови runtime и будущий task/path context: одна и та же папка может иметь
   разные chain в Codex, Claude Code или другом runner-е.
2. Перечисли только реально загружаемые global → root → relevant subtree
   instructions; отдели `file exists` от `text reaches this task`.
3. Подтверди loading, fallback, imports и truncation через
   [`claude-discovery.md`](references/claude-discovery.md), только когда они
   спорны; не переноси привычку одного runtime в другой.
4. Расположи loaded sources по precedence и назови место, где их rules
   конфликтуют, дублируются или оставляют gap.
5. Для каждого material meaning назови live semantic owner; runtime winner и
   semantic owner могут оказаться разными фактами.
6. Разреши текущий effective winner из loading + precedence, а не из имени файла
   или уверенности автора.
7. Если спорны root/subtree topology, duplicate или placement, прочитай
   [`audit-placement-structure.md`](references/audit-placement-structure.md)
   до owner-решения.

**Результат gate:** `runtime + task/path + loaded sources + precedence +
conflicts/gaps + effective winner`. Не можешь доказать loading или precedence →
назови gap; не выбирай owner из воображаемой chain.

### Gate 2 — Выбери Одного Owner-а И Класс Delta

1. Для candidate rule назови полный scope наблюдаемого trigger-а, не папку, где
   текст случайно найден.
2. Выбери самый узкий existing owner, который покрывает trigger целиком и
   загружается до нужного акта.
3. Оставь один source of meaning: competing copies удали, перемести или замени
   pointer-ом. Короткий refresher допустим только в другом lifecycle moment и
   продолжает ссылаться на того же owner-а.
4. Проверь соседние owners: proposed rule не должен незаметно присвоить их
   authority или создать второй способ разрешить тот же конфликт.
5. Классифицируй delta как `local fact / owner pointer`, `behavioral rule` или
   `hard invariant`.
6. Если нужная форма требует split/merge/move/new instruction container,
   остановись до edits: целевой контейнер принадлежит `1ia-audit`.

**Результат gate:** `chosen owner + owned scope + delta class + duplicate
repair`. Нет одного owner-а или устойчивой delta → delete/no-op, не wording.

### Gate 3 — Инстанцируй Steering Cell

1. Выбери один representative future case, где trigger возникает естественно,
   старый ход правдоподобен, а разница видна до финального самоотчёта.
2. Назови точный fork: наблюдаемый момент, в котором доступны старая и нужная
   траектории.
3. Прогони этот момент через реально загружаемую old/default chain, не добавляя
   proposed rule задним числом.
4. Запиши первый наблюдаемый natural act; не подменяй его скрытым состоянием или
   поздним объяснением агента.
5. Назови видимый сигнал, делающий этот act правдоподобным, и конкретный harm,
   который он запускает.
6. Запиши первый target act, source check, comparison, artifact или decision
   rule, который должен стать естественным вместо него.
7. Сверь target с owner meaning: пример иллюстрирует правило, но не создаёт его.
8. Сформулируй одно изменение `natural first act → target first act`; несколько
   независимых изменений означают несколько repairs или слишком широкий scope.
9. Для load-bearing meaning, success criteria либо design root/subtree routing
   используй [`audit-meaning-criteria.md`](references/audit-meaning-criteria.md)
   как conditional depth, а не копируй его protocol сюда.

**Результат gate:** полная steering cell `fork + natural act + plausibility +
harm + target act + changed rule`. Акты не различаются → durable steering delta
не доказана.

### Gate 4 — Выбери Control И Один Repair

1. Спроси, допустимо ли, чтобы соблюдение этого obligation зависело от качества
   reasoning. Чем дороже или необратимее пропуск, тем слабее prose как control.
2. Для hard invariant выбери permission, hook, validator, test или approval у
   live runtime owner-а; instruction оставляет route/объяснение, не изображает
   enforcement.
3. Для text-level delta сравни repairs по причине провала:
   - `keep` — owner, load, steering и evidence уже достаточны;
   - `delete` — устойчивой delta нет либо текст только дублирует meaning;
   - `narrow scope` — rule верен лишь для меньшего observable trigger-а;
   - `move to owner` — meaning верен, но лежит не в effective owner-е;
   - `replace with pointer` — truth уже существует у другого owner-а;
   - `rewrite exact wording` — owner/placement верны, но первый акт не меняется;
   - `handoff to enforcement` — цена пропуска несовместима с prose-only control.
4. Выбери один primary repair. Supporting edits допустимы только для удаления
   созданных им duplicates или broken routes, не для попутной уборки.
5. Procedure добавляй только когда order, lifecycle moment, completeness или
   хрупкость сами являются контрактом; иначе оставь outcome/decision rule.

**Результат gate:** `prose|enforcement + primary repair + почему меньший repair
не закрывает harm`. Не можешь отличить выбранный repair от меньшего → используй
меньший.

### Gate 5 — Напиши Exact Delta

1. Начни с observable trigger/scope, а не с желаемого характера агента.
2. Дай положительный default или decision rule; запрет без preferred
   continuation оставляет прежнюю траекторию доступной.
3. Переведи «осознай / будь внимателен / учти» в наблюдаемый source check,
   artifact, comparison, target act или outcome.
4. Назови owner/source и поставь load-bearing check в point of action — рядом с
   командой, phase boundary или решением, которое он должен изменить.
5. Добавь только нужные exception, fallback или escalation; exception не должен
   молча становиться вторым default-ом.
6. Назови evidence и stop, по которым future agent не объявит completion по
   пересказу правила.
7. Используй pointer по умолчанию. Refresher оставляй лишь когда повторная
   позиция меняет действие; owner meaning при этом не дублируется.
8. Добавь rationale, только если без causal link правило выглядит произвольным
   и легко отбрасывается. Добавь contrastive example, только если boundary иначе
   не распознаётся.
9. Проверь form congruence: router ориентирует, а не погружает; outcome-rule не
   репетирует ceremony; example не создаёт случайный mandate.
10. Проведи delete-first pass: убери generic caution, повторы, obsolete
    scaffolding и строки, удаление которых не меняет следующий act или evidence.
11. Если спорны introspective slogan, literal scope, negative vacuum, Hyrum,
    frame capture или accidental mandate, прочитай
    [`language-quality-audit.md`](references/language-quality-audit.md) до
    финального wording.

**Результат gate:** exact proposed/applied `trigger + positive rule +
owner/source + exception/fallback + evidence + stop` в точке действия.

### Gate 6 — Предскажи Bypass И Докажи Delta

1. До вердикта назови самый правдоподобный способ выполнить новую форму,
   сохранив старое решение: заполнить поля, процитировать rule, добавить
   self-check или отложить нужный act до финала.
2. Если bypass проходит, вернись к недостающему operator-у или point of action;
   не лечи его ещё одним `MUST` либо полем отчёта.
3. Построй различающий probe на той же representative fork: заранее назови
   expected old first act, expected proposed first act и observable scoring.
4. Сравни old/default и proposed effective chain на одной задаче; не меняй
   одновременно case, model, settings и правило.
5. Для малой low-risk правки counterfactual walkthrough — design-time proxy.
   Для material/global/risky surface используй чистый cold-start with/without,
   previous-version или абляцию на непоказанном case.
6. Claim «нужная траектория стала вероятнее» требует matched runs на том же
   resolved model/settings и частоты target first act; один удачный run
   доказывает возможность, не probability shift.
7. Self-report, пересказ правила, lint и заполненный output template не являются
   behavioral evidence. Same-model critique, debate или второй проход могут
   помочь построить candidate, но не становятся независимой проверкой без
   external verifier/tool, live owner evidence либо наблюдаемого outcome.
8. Named target-model failure сверяй с
   [`llm-divergences.md`](references/llm-divergences.md); не превращай
   недатированную интуицию в постоянное свойство модели.
9. Если proof требует exact, semantic или graph evidence за пределами уже
   прочитанных instruction files, маршрутизируй его через
   [`cli-recipes.md`](references/cli-recipes.md), не дублируя чужой runbook.
10. В audit mode верни exact proposed text/delete/move и probe без edits. В
    change mode после применения проверь direct read/diff, effective chain,
    metadata/resources и smallest evidence, соответствующее реальному риску.

**Результат gate:** `predicted bypass + discriminating probe + run/proxy
evidence + claim strength + unresolved risk`. Недоступен behavioral run → назови
gap; не повышай design-time proxy до доказательства эффективности.

Контрастивная демонстрация механизма, не правило проекта:

> Слабо: «Будь внимателен к устаревшим данным». Сильнее: «Перед тем как назвать
> значение текущим, сверь его с live owner; если live evidence недоступно,
> маркируй значение unverified». Первая фраза допускает прежний первый акт и
> последующее самооправдание; вторая связывает fork, check и fallback. Ещё один
> абзац о важности точности без этого перехода форму усилит, а решение — нет.

## Triggered Repository Rules

Project-owned cold rule directory вроде `_ops/rules/**` — допустимая
instruction surface, если правило устойчиво, нужно только в редкий наблюдаемый
момент и root может надёжно маршрутизировать этот момент.

- Always-on invariant остаётся в effective `AGENTS.md`; path-local правило — в
  subtree `AGENTS.md`.
- Root содержит только `observable trigger → exact RULE`; procedure и rationale
  живут в одном RULE.
- Каждый live RULE объявляет один information job, `read-when`, target
  act/result, owner/status и stop. Его steering cell реконструируется при
  authoring, но не сериализуется целиком без необходимости. RULE без root route
  — orphan; копия его procedure в root — competing owner.
- Читай RULE только после совпадения trigger, не загружай всю папку заранее.
- Если правило должно обнаруживаться skill runtime-ом в момент действия, а root
  route недостаточен, surface decision принадлежит `1skill-architect`; жанр
  project-local `2*` — `1local-rules`.

## Boundaries

- split/merge/move/new instruction container → `1ia-audit`;
- `depends-on`, holders, anchors, cycles, broken links → `1md-graph`;
- skill/agent/hook selection, trigger/collision → `1skill-architect`;
- project scope/done/stop → `1goal`; task contract → `1planning`;
- permissions/hooks/settings/enforcement → live runtime owner.

## Вывод И Стоп

```text
Mode + durability: <audit|change; one-off|durable>
Effective chain + owner: <loaded sources, precedence, chosen owner>
Steering fork: <observable trigger; natural first act -> target first act; harm>
Control + repair: <fact|rule|invariant/enforcement; exact proposed/applied delta>
Behavioral proof + risk: <predicted bypass; probe/run evidence; unresolved risk>
```

Готово, когда effective chain и owner подтверждены, steering cell различает
старую и нужную траектории, exact repair соответствует mode, соседние owners не
конкурируют, а validation не выдаёт text compliance за changed behavior.
Остановись до edits, container/graph/runtime mutation или внешней записи, если
текущий intent их не разрешает. Если behavioral run недоступен, назови этот gap,
не повышай design-time proxy до доказательства эффективности.
