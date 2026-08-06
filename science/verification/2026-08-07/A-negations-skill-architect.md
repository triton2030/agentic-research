# Инвентарь отрицаний — `1skill-architect` 71 006 символов

Зафиксирован 2026-08-07 **до** написания сжатой версии. Механический скан по
маркерам (`не`, `нельзя`, `кроме`, `только`, `иначе`, `обязан`, `not`, `never`,
`only`, `unless`, `without`, `must`, `rather than`, `instead of`, `avoid`) дал
**283 строки**; после сведения дублей — **108 нормативных единиц**.

Сверка после разреза — поимённо по этому списку, а не чтением.

Источники: **S** = `SKILL.md`, **G** = `GLOSSARY.md`,
**AP** = `references/anti-patterns.md`, **DA** = `references/deep-audit.md`,
**LC** = `references/local-skill-contract.md`,
**PA** = `references/platform-skill-authoring.md`.

Колонка «Ловит» — номер ситуации из `A-battery-skill-architect.md`; `—` означает
«не покрыта».

## 1. Вход и диагноз

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N01 | «Не начинай с названия, структуры папки или списка возможностей.» | S «Начинай с провала» (дубль LC: «do not start from a skill name or desired folder») | A01 |
| N02 | «Если провал нельзя показать даже сценой, skill пока строится из вкуса автора. Не лечи гипотетическую слабость prompt-бюджетом.» | S «Начинай с провала» | A03 |
| N03 | «Default: что модель делает естественно, а не карикатурно плохо.» | S «Как проектировать когнитивный механизм» (дубли: G Natural Default; AP «Straw-agent diagnosis») | — |
| N04 | «Метафора „вставить орган“ полезна для автора, но не заменяет tell, causal chain и transfer evidence»; «Не доказывай буквальную „неспособность“ модели» | S «Начинай с провала», «Cognitive shaper» (дубли: PA «a "missing organ" metaphor is not evidence»; LC «Do not use model-anatomy metaphors as proof»; AP «Anatomy as proof») | — |
| N05 | «не выбирай любимый термин по гладкости. Сохрани обе competing hypotheses и назови probe, результат которого различит их» | S «Начинай с провала» | — |
| N06 | «Не можешь назвать — остановись на ней.» (Proof Gate) | S «Начинай с провала»; G Proof Gate | A04 |
| N07 | «Сложный механизм должен победить не только no-skill baseline, но и меньшую форму того же вмешательства.» | S «Начинай с провала» (дубль AP «Oversized first intervention») | A04 |
| N08 | «Сам факт вызова или красивый `SKILL.md` не доказывает ни того, ни другого.» | S «Зачем этот скилл существует» | — |
| N09 | «задача автора — не максимизировать число правил, а изменить локальную экономику решения» | S «Зачем этот скилл существует» | — |

## 2. Класс пакета и слой enforcement

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N10 | «отправь enforcement в hook, permission, validator или другой детерминированный слой, а не надейся на prose skill» | S «Operational package» (дубли: AP «Prompt-only guardrail for hard risk»; LC Surface gate; PA «use deterministic enforcement rather than prose») | A06 |
| N11 | «Для invariant или safety surface доказательство необходимости обязано назвать защищаемый риск и последствие нарушения.» | S «Operational package» | A06 |
| N12 | «Жёсткий workflow оправдан только там, где порядок сам является частью корректности» | S «Operational package» (дубли: LC «Preserve strict order only when order itself is part of correctness»; PA «Ordered steps appear only when violating order reproduces a correctness, safety, or tool failure») | A05 |
| N13 | «Не заставляй operational package изображать глубокую когнитивную теорию. И не сжимай cognitive shaper до runbook» | S «Operational package» (дубли: PA «Do not force both through one template»; LC «Do not invent cognitive ceremony around a deterministic operation») | A05 |
| N14 | «Гибрид разделяет causal/judgment core и детерминированный tool layer явно.» | S «Operational package» | — |
| N15 | «Его продукт — не только ответ, а переиспользуемый controller» | S «Cognitive shaper» (дубли: AP «Mechanism without controller», «Controller as decoration»; G Reusable Controller) | — |

## 3. Доказательство необходимости

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N16 | «Пиши это как объяснение причин, а не рекламу: „важно“, „профессионально“, „надёжнее“ и пересказ цели пользователя ничего не доказывают.» | S «Доказательство необходимости» (дубли: AP «Explanation bloat»; G Necessity Proof) | — |
| N17 | «Если агент может без труда вывести весь механизм из текущего запроса и ближайшего owner-а, отдельный skill не нужен.» | S «Доказательство необходимости» (дубли: LC Necessity proof; G Reuse-first Gate; AP «Cargo-cult creation») | A04 |
| N18 | «подпись владельца не превращает ошибочную causal story в факт: claim остаётся проверяемым» | S «Доказательство необходимости» | — |

## 4. Когнитивный механизм

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N19 | «опиши не желаемый характер агента, а переход между двумя состояниями мышления» | S «Как проектировать когнитивный механизм» | — |
| N20 | «Следующие элементы — диагностический язык, а не обязательный шаблон output» | S там же | — |
| N21 | «Proxy: какая проверка над текстом, контекстом или артефактом заменяет ненадёжное „осознай“, „заметь“ или „не забудь“» | S там же (дубли: AP «Introspection imperative»; G Proxy Translation) | — |
| N22 | «Operators: одна-три операции, которые действительно вызывают переход.» | S там же | — |
| N23 | «не перекладывай на владельца работу модели»; «Не проси владельца сочинять то, что ему проще распознать в твоём варианте.» | S там же, «Labor inversion» | — |
| N24 | «Самолов для proxy и экономики делается во время письма, не после benchmark-а» | S там же | — |
| N25 | «мысленно удали operator: если не меняются следующий выбор, probe или evidence, это post-hoc label, а не рычаг» | S там же | — |
| N26 | «сделай его конкретным в точке действия — рядом с командой, шаблоном или phase boundary, — а не только в раннем rationale» | S «Позиция тоже часть operator-а» (дубли: AP «Distant critical rule»; LC Point of action) | A08 |
| N27 | «Owner смысла остаётся один: используй точный pointer или generated reminder, а не независимый пересказ правила.» | S там же (дубль AP «One rule in many owners») | A08 |
| N28 | «Не вставляй все пять по привычке. Выбирай только те, без которых повторяется конкретный causal failure» | S «Пять рычагов управления» (дубли: PA «Add a local objective … only when the demonstrated failure depends on that lever»; LC Cognitive core) | — |
| N29 | «Anchor обязан иметь источник/вето и reopen signal, иначе ранняя ошибка лишь цементируется.» | S «Пять рычагов» (дубли: G Commitment Anchor; AP «Anchor lock-in») | — |
| N30 | «Это control boundary, не универсальная пошаговая форма.» (phase separation) | S «Пять рычагов» (дубли: G Phase Separation; AP «Phase leak») | — |
| N31 | «Не требуй от модели раскрывать приватную chain-of-thought.» | S «Пять рычагов», финал | — |
| N32 | «Objective rebasing: вместо абстрактного „сделай хороший ответ“ skill задаёт меру, которая продолжает разрешать новые случаи» | S «Пять рычагов» (дубли: G Local Objective; AP «Unchanged economics») | — |

## 5. Примеры и causal cell

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N33 | «Operator без причины становится optional ceremony. Причина без operator-а — объяснительный шум. Карикатурный anti-example не вырезает реальную границу.» | S «Примеры должны учить мышлению» (дубли: G Causal Cell; AP «False contrast») | A09 |
| N34 | «Для центрального механизма дай несколько коротких контрастивных примеров прямо в `SKILL.md`; длинные варианты и доменные серии можно вынести в `references/`.» | S там же | — |
| N35 | «Число не является механизмом; различающий probe является.» | S там же (антипример к «Всегда перечисляй три гипотезы») | — |
| N36 | «Примеры иллюстрируют операции, не поставляют факты реального проекта.» | S там же (дубль G Thought Demonstration `_Avoid_`) | — |
| N37 | «Его claim — перенос decision structure, не автоматический рост точности задачи.» | S там же (дубль AP «Demonstration overclaim») | — |
| N38 | «Не подсовывай ответ evaluation-кейса и не делай один доменный пример единственным способом узнать правило.» | S там же (дубль AP «Leaked demonstration») | — |
| N39 | «Пример финального output часто учит стилю и заполнению полей.» | S там же (дубли: G Output-example Trap; AP «Output-example trap»; LC «A final-output example alone is insufficient») | — |

## 6. Form congruence

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N40 | «Его форма должна исполнять собственный метод» | S «Form congruence» | A10 |
| N41 | «Это не требование копировать стиль или секции — совпадать должна decision structure.» | S там же (дубль G Form Congruence `_Avoid_`) | A10 |
| N42 | «Раннее соблюдение не доказывает устойчивость»; «Это long-horizon risk, а не редакционная аккуратность» | S там же (дубль AP «Form mismatch») | A10 |

## 7. Поверхность, граница, stop

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N43 | «Одна поверхность владеет одним положительным моментом и одним связным изменением. Не превращай body в каталог соседних routes.» | S «Выбери правильную поверхность после диагноза» | A07 |
| N44 | «не выбирай surface раньше диагноза: иначе формат начинает диктовать объяснение проблемы» | S там же (дубли: G Surface-first Design; AP «Surface-first»/Ordering) | A07 |
| N45 | «**no new surface** — ближайший owner уже способен вернуть механизм в нужный момент.» | S там же | A07 |
| N46 | «Не добавляй меню соседей, handoff catalog или объяснение действий для случаев, где его положительный trigger не совпал» | S там же (дубль PA «Keep near-miss cases in evaluation, not as neighbor pointers in runtime text») | A11 |
| N47 | «Отрицательную boundary добавляй только когда она предотвращает реальный authority overclaim.» | S там же | — |
| N48 | «Внешнюю skill/tool dependency объявляй лишь когда без неё невозможно выполнить положительный момент: назови точный handle, её information job и поведение при недоступности.» | S там же (дубль LC Boundary) | — |
| N49 | «Он не scaffold-ит package, не выполняет tool workflow, не распространяет projection и не выдаёт собственный design за измеренный behavioral proof.» | S «Граница и stop» | A02 |
| N50 | «Если necessity или transfer нельзя сформулировать, вердикт — не добавлять правила, а вернуться к failure trace либо отказаться от нового surface.» | S там же | A03 |
| N51 | «Не компенсируй это расширением description: вернись к сцене, owner или границе.» | S там же (дубль LC Portable Done) | — |

## 8. Discovery contract

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N52 | «Capability list и безрисковое „helps with...“ не дают модели причины потратить контекст.» | S «Discovery contract» (дубли: G Capability List, Central Model Violation; AP «Capabilities over triggers») | — |
| N53 | «`description` — не summary, а убедительный указатель: **condition × stake**.» | S там же (дубли: G Condition x Stake, Shallow Abstraction; PA Discovery Contract) | — |
| N54 | «общий trigger phrase — сигнал ownership/collision, а не повод для буквального dedupe» | S там же (дубли: PA «A shared trigger phrase is a collision/ownership question, not literal deduplication»; G Canvas Audit, Collision) | A11 |
| N55 | «Проверь его против полного live candidate canvas и реальных near-misses» | S там же (дубли: G Candidate Canvas, Description-in-Vacuum; AP «Description-in-vacuum») | A11 |
| N56 | «Cut test: if removing a phrase does not change which skill should activate against live neighbors, it is a no-op or body material.» | PA «Discovery Contract» | A11 |
| N57 | «Prefer path/file/action over abstract categories that require self-classification»; Hot Zone: «Put the main moment and trigger words here» | G Observable Anchor, Hot Zone (дубль AP «Abstract category trigger») | — |
| N58 | «_Avoid_: 1024 as target, premature shortening» (Description Budget) | G Description Budget | — |
| N59 | «`disable-model-invocation: true` suits a deliberate/manual skill that should not compete in model discovery.» | PA «Candidate Canvas and Invocation» | — |

## 9. Skill Frame и замыкание контура

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N60 | «Это coverage map, не анкета: покажи только load-bearing ответы, способные изменить дизайн или его проверку.» | S «Результат: Skill Frame» | A12 |
| N61 | «Не создавай отдельный файл ради формы, если локальный проект не назначил ему owner.» | S там же | A12 |
| N62 | «Если claim зависит от поведения модели, зафиксируй resolved model, дату наблюдения и смену target model set как reopen signal.» | S там же (дубли: G Undated Model Deficit; AP «Undated model deficit»; LC Portable Done) | — |
| N63 | «Stop/sunset: когда дизайн достаточен и какой сигнал потребует пересмотра.» | S там же (дубль AP «No sunset signal») | — |
| N64 | «Явная подпись владельца нужна, когда дизайн интерпретирует его намерение, меняет authority, риск или material scope. В остальных случаях … не создавай церемонию ради каждого локального решения.» | S «Замкни контур до implementation» | — |
| N65 | «перечитай его точный релевантный block в активный контекст; существование файла и память о summary якорь не применяют» | S там же (дубль G Commitment Anchor) | A13 |
| N66 | «Если block устарел, сначала revise/reopen его, а не проявляй верность ошибочному прошлому решению.» | S там же | A13 |
| N67 | «Новый core assumption, несработавший прогноз или форма без изменившегося решения reopen-ят Frame; не цементируй дрейф локальной правкой текста.» | S там же | A13 |
| N68 | «Прогноз не является доказательством переноса, но ловит красивый механизм без causal grip» | S там же | — |
| N69 | «Модель сама формулирует полный черновик … человек или semantic owner делает дешёвое узнавание, коррекцию либо veto.» | S там же (дубль G Two Users, S «Labor inversion») | — |

## 10. Evidence

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N70 | «Структурная validation доказывает только читаемость package. Prompt visibility доказывает только selection. Заполненный шаблон доказывает только compliance.» | S «Evidence: докажи изменение, а не послушание» (дубли: AP «Matcher-only proof», «Compliance-only proof»; PA «Prompt visibility proves only that selection is possible»; G Checklist Theatre) | A14 |
| N71 | «Не требуй тяжёлого benchmark для маленькой правки, но не называй semantic перенос доказанным по lint и самоотчёту модели.» | S там же (дубли: G Thought Theatre; AP «Thought theatre») | A14 |
| N72 | «используй matched resampling: одна непоказанная ситуация, тот же resolved model и settings … Считай частоту нужного первого акта на развилке и записывай число прогонов.» | S там же (дубли: G Claim-bound Evidence; LC Validation) | A14 |
| N73 | «Один удачный run доказывает возможность, но не сдвиг вероятности.» | S там же | A14 |
| N74 | «Для routing нужны use/skip/near-miss cases против живых соседей.» | S там же (дубли: PA Evidence by Claim; AP «No near-miss negatives»; LC Portable Done) | — |
| N75 | «Не прогоняй фиксированный ритуал всех проверок; выбирай evidence, которое различает именно заявленные риски.» | S там же (дубль PA «This does not become a fixed number of prompts, a mandatory benchmark, or a universal verification ritual») | — |
| N76 | «Сила evidence растёт вместе с широтой, частотой, риском, credential/network effects, trigger collision и историей regressions.» | S там же (дубли: PA Evidence by Claim; LC Validation) | — |
| N77 | «Перед добавлением нового правила проведи delete-first pass: убери obsolete scaffolding, повторы, generic brevity и строки без action-changing Delta.» | S там же (дубли: LC Minimality; AP «Add-only output»; DA шаг 7) | A15 |
| N78 | «Не удаляй causal explanation или thought demonstration, если без них controller снова превращается в произвольную команду.» | S там же (дубли: LC Minimality; G Micro-router) | A15 |
| N79 | «Elastic defense: a failed run is rescued by a post-hoc explanation when no bypass prediction and revision criterion were recorded before it.»; «register the bypass prediction first» | AP Evaluation Failures; LC Validation; G Elastic Defense; S «Типовые провалы» | — |
| N80 | «No mechanism ablation: a central explanation or example is assumed to cause the effect without testing whether behavior survives its removal» | AP Evaluation Failures (дубль S «Сильнейшее evidence — with/without, previous-version или ablation») | — |
| N81 | «Structural, routing, cognitive-transfer, operational, and distribution claims are reported as separate evidence layers; uncovered layers stay explicit.» | LC Portable Done (дубль PA Evidence by Claim) | — |

## 11. Объём, routes, progressive disclosure

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N82 | «Точные значения выделенных архитектурных терминов бери из `GLOSSARY.md`, только когда термин двусмыслен или меняется сам словарь.» | S «Зачем этот скилл существует» (дубль G intro: «Read it only when a term is ambiguous») | — |
| N83 | «`references/deep-audit.md` — только для полного аудита landscape/control system, не для одной правки.» | S «Условные routes» (дубль DA intro) | — |
| N84 | «Open this only when the output includes "make a local skill", "rewrite this skill", or "port this skill into another supported runtime".» | LC intro | — |
| N85 | «Do not instruct the agent to read every reference. Give each bundled file an action-changing route from `SKILL.md`.» | PA Core Contract (дубль PA Claude-Specific Done) | — |
| N86 | «Keep reference files one level deep … A body under 500 lines is a ceiling, not a target.» | PA Core Contract (дубль LC Portable Done) | — |
| N87 | «Do not move the causal core out merely to make `SKILL.md` short.» | LC Progressive disclosure (дубль G Micro-router) | — |
| N88 | «`SKILL.md` is the smallest causally complete contract, not a textbook»; «Include only **Delta** in a skill» | PA Core Contract (дубли: G Delta; AP «Encyclopedic body») | — |
| N89 | «Scripts are justified by deterministic behavior, external tooling, or a recurring fragile operation; examples do not compensate for a weak interface.» | PA Core Contract | — |
| N90 | «Name authority, required output, and side-effect boundaries only when they change the permitted action.» | PA Core Contract | — |

## 12. Платформа, источники, projection

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N91 | «Verify the live Claude skill root and resolved model rather than inferring them from an alias, old path, or another platform.» | PA Candidate Canvas / Claude-Specific Done (дубли: LC Portable Done; AP «Runtime by analogy») | — |
| N92 | «Model, effort, thinking, long-run, and fallback rules belong to the current model owner/runtime. Do not copy them into the skill.» | PA Model Baseline | — |
| N93 | «Generic self-review, an automatic verifier, and fan-out are not part of the portable baseline.» | PA Model Baseline | — |
| N94 | «Older Claude 4.x skills and prompts are historical migration evidence, not an active baseline or fallback.» | PA Model Baseline | — |
| N95 | «An Anthropic-endorsed claim requires a current official source»; «Label local engineering as local engineering, not an Anthropic recommendation»; «Do not invent metrics, limits, or runtime availability.» | PA Source Discipline | — |
| N96 | «No `agents/openai.yaml`, Codex-only tool names, or Codex validation commands remain in the Claude projection»; «Portable files contain no platform-only paths, metadata, commands, model routing, or validation claims» | PA Claude-Specific Done; LC Portable Done | — |
| N97 | «It does not merely make Opus 5 or Fable 5 perform an authoring checklist»; «Its step list is the mechanics of a specific tool, not the mandatory shape of a skill body … Do not reproduce the matcher/eval pipeline» | PA Desired Result, Authoring Mechanics | — |
| N98 | «`SKILL.md` frontmatter has `name` and `description`; optional `disable-model-invocation` and `allowed-tools` match real runtime intent.» | PA Claude-Specific Done (дубль LC Portable Done) | — |

## 13. Порядок и правила deep-audit

| # | Норма (цитата) | Источник | Ловит |
| --- | --- | --- | --- |
| N99 | «Keep the order. Current-state map and forces come before failure scan.» | DA Eight Steps (дубль AP «Failure scan before capability inventory») | — |
| N100 | «If the upstream layer is missing or stale, report that instead of compensating with general architecture.» | DA шаг 1 (дубль AP «Cold upstream») | — |
| N101 | «Use exact handles, not classes. "Hook exists" is too vague; name event, matcher, and action.» | DA шаг 2 | — |
| N102 | «Generic future change without a signal is out of scope.» | DA шаг 3 (дубль AP «Forces as epilogue») | — |
| N103 | «Done when failures are classes, not a flat patch list»; «One failure -> one prescription: patching symptoms instead of finding a single intervention that removes the class» | DA шаг 4; AP Ordering Failures | — |
| N104 | «Do not recommend a new surface until reuse-first has failed.» | DA шаг 5 (дубли: G Reuse-first Gate; AP «Cargo-cult creation») | — |
| N105 | «Prompt-level fixes are acceptable only when runtime/skill/agent alternatives are unnecessary or too costly for the risk.» | DA шаг 6 | — |
| N106 | «Do not publish prescriptions without reuse-first gate, owner, observable signal, and validation.» | DA Rules | — |
| N107 | «Include minimize pass even when nothing was removed»; «Chesterton's fence check: what breaks if this old piece is removed?»; «Use folder audit only when folders are actually in scope»; «Apply lenses during the steps, not as a ritual» | DA шаг 7, Lenses, Rules | — |
| N108 | «For load-bearing routing or enforcement changes, use an empirical probe when reasonable. For small text-only edits, structural validation plus manual criteria check is enough.» | DA шаг 8 | — |

## 14. Отдельно: словарь запретов GLOSSARY

`GLOSSARY.md` снабжает **каждый** из ~40 терминов строкой `_Avoid_:` — списком
соседних слов, которыми термин подменяют («_Avoid_: topic, usefulness, about-X,
capabilities» у Moment-fit и т. д.). Это нормативная конструкция словаря целиком;
сведена в единицу **N-GLOS**, отдельным номером в счёт не берётся, но при сверке
проверяется как один блок: сохранился ли механизм «термин + чем его подменяют».

**Ловит:** — (не покрыта).

## Сверка покрытия

Единиц в инвентаре: **108**.

Покрыты батареей (35): N01→A01, N02→A03, N06→A04, N07→A04, N10→A06, N11→A06,
N12→A05, N13→A05, N17→A04, N26→A08, N27→A08, N33→A09, N40→A10, N41→A10,
N42→A10, N43→A07, N44→A07, N45→A07, N46→A11, N49→A02, N50→A03, N54→A11,
N55→A11, N56→A11, N60→A12, N61→A12, N65→A13, N66→A13, N67→A13, N70→A14,
N71→A14, N72→A14, N73→A14, N77→A15, N78→A15.

Не покрыты (73): N03, N04, N05, N08, N09, N14, N15, N16, N18, N19, N20, N21,
N22, N23, N24, N25, N28, N29, N30, N31, N32, N34, N35, N36, N37, N38, N39, N47,
N48, N51, N52, N53, N57, N58, N59, N62, N63, N64, N68, N69, N74, N75, N76, N79,
N80, N81, N82, N83, N84, N85, N86, N87, N88, N89, N90, N91, N92, N93, N94, N95,
N96, N97, N98, N99, N100, N101, N102, N103, N104, N105, N106, N107, N108
(+ блок N-GLOS сверх счёта).

**Не покрыта: 73 из 108.**

Это ожидаемо и не является дефектом батареи: протокол ограничивает её 10–15
ситуациями ради того, чтобы она запускалась на каждой партии разрезов. Матрица
покрытия здесь — фильтр перед прогоном, а не сертификат. Непокрытые единицы
проверяются поимённо глазами по этому списку после каждой партии; выпадение любой
из них — событие, требующее решения владельца, а не молчаливого списания.

Плотнее всего непокрытая масса лежит в четырёх местах, и именно там сверка глазами
обязательна: механизм (N19–N32), примеры (N34–N39), платформенные и source-нормы
(N91–N98), порядок deep-audit (N99–N108).
