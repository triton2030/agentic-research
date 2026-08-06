# Маршрутная таблица — `SA-cand-2`

Пересборка пакета `1skill-architect` (71 006 символов, ядро 25 374) в форму
«ядро ≤2000 + references по ≤2000». Ядро — 1904 символа (13.3× к исходному
ядру), 41 reference-файл, все ≤2000.

**Сверка механическая, не чтением.** Каждая из 108 единиц инвентаря
`A-negations-skill-architect.md` проверена скриптом: цитата нормализуется
(пробелы, `*`, `` ` ``, кавычки) и ищется дословно в текстах пакета.
Результат прогона: **106 из 108 найдены дословно**; N82 и N83 — это сами
route-нормы, их условие перенесено в строку ядра дословно, а адрес переписан
на новые имена файлов (старых `GLOSSARY.md` и `references/deep-audit.md`
больше не существует).

Отдельно проверено, что **все** строки `GLOSSARY.md`, `anti-patterns.md`,
`deep-audit.md` присутствуют в пакете дословно (0 непокрытых строк);
у `SKILL.md` непокрыты только перенесённые в ядро route-блоки, у
`platform-skill-authoring.md` и `local-skill-contract.md` — только удалённые
дубли, перечисленные ниже поимённо.

## Таблица единиц

| # | Норма (начало цитаты) | Файл назначения | Строка ядра-маршрут | показ |
| --- | --- | --- | --- | --- |
| N01 | «Не начинай с названия, структуры папки или списка возможностей.» | **ядро** (дословно) + `trace.md` | —  (норма стоит в ядре первой строкой) |  |
| N02 | «Если провал нельзя показать даже сценой, skill пока строится из вкуса автора. Не лечи гипот… | `trace.md` | «берёшь trace, называешь deficit → `trace.md`» |  |
| N03 | «Default: что модель делает естественно, а не карикатурно плохо.» | `mechanism.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N04 | «Метафора „вставить орган“ полезна для автора, но не заменяет tell, causal chain и transfer … | `class.md`, `trace.md` | «класс пакета и слой enforcement → `class.md`» |  |
| N05 | «не выбирай любимый термин по гладкости. Сохрани обе competing hypotheses и назови probe, ре… | `trace.md` | «берёшь trace, называешь deficit → `trace.md`» |  |
| N06 | «Не можешь назвать — остановись на ней.» (Proof Gate) | `necessity.md` | «Proof Gate и причинная цепочка → `necessity.md`» |  |
| N07 | «Сложный механизм должен победить не только no-skill baseline, но и меньшую форму того же вм… | `necessity.md` | «Proof Gate и причинная цепочка → `necessity.md`» |  |
| N08 | «Сам факт вызова или красивый `SKILL.md` не доказывает ни того, ни другого.» | `why.md` | «вмешательство должно доказать себе необходимость → `why.md`» |  |
| N09 | «задача автора — не максимизировать число правил, а изменить локальную экономику решения» | `why.md` | «вмешательство должно доказать себе необходимость → `why.md`» |  |
| N10 | «отправь enforcement в hook, permission, validator или другой детерминированный слой, а не н… | `class.md` | «класс пакета и слой enforcement → `class.md`» |  |
| N11 | «Для invariant или safety surface доказательство необходимости обязано назвать защищаемый ри… | `class.md` | «класс пакета и слой enforcement → `class.md`» |  |
| N12 | «Жёсткий workflow оправдан только там, где порядок сам является частью корректности» | `class.md` | «класс пакета и слой enforcement → `class.md`» |  |
| N13 | «Не заставляй operational package изображать глубокую когнитивную теорию. И не сжимай cognit… | `class.md` | «класс пакета и слой enforcement → `class.md`» |  |
| N14 | «Гибрид разделяет causal/judgment core и детерминированный tool layer явно.» | `class.md` | «класс пакета и слой enforcement → `class.md`» |  |
| N15 | «Его продукт — не только ответ, а переиспользуемый controller» | `class.md` | «класс пакета и слой enforcement → `class.md`» |  |
| N16 | «Пиши это как объяснение причин, а не рекламу: „важно“, „профессионально“, „надёжнее“ и пере… | `necessity.md` | «Proof Gate и причинная цепочка → `necessity.md`» |  |
| N17 | «Если агент может без труда вывести весь механизм из текущего запроса и ближайшего owner-а, … | `necessity.md` | «Proof Gate и причинная цепочка → `necessity.md`» |  |
| N18 | «подпись владельца не превращает ошибочную causal story в факт: claim остаётся проверяемым» | `necessity.md` | «Proof Gate и причинная цепочка → `necessity.md`» |  |
| N19 | «опиши не желаемый характер агента, а переход между двумя состояниями мышления» | `mechanism.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N20 | «Следующие элементы — диагностический язык, а не обязательный шаблон output» | `mechanism.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N21 | «Proxy: какая проверка над текстом, контекстом или артефактом заменяет ненадёжное „осознай“,… | `mechanism.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N22 | «Operators: одна-три операции, которые действительно вызывают переход.» | `mechanism.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N23 | «не перекладывай на владельца работу модели»; «Не проси владельца сочинять то, что ему проще… | `levers.md`, `mechanism.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N24 | «Самолов для proxy и экономики делается во время письма, не после benchmark-а» | `position.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N25 | «мысленно удали operator: если не меняются следующий выбор, probe или evidence, это post-hoc… | `position.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N26 | «сделай его конкретным в точке действия — рядом с командой, шаблоном или phase boundary, — а… | `position.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N27 | «Owner смысла остаётся один: используй точный pointer или generated reminder, а не независим… | `position.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N28 | «Не вставляй все пять по привычке. Выбирай только те, без которых повторяется конкретный cau… | `levers.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N29 | «Anchor обязан иметь источник/вето и reopen signal, иначе ранняя ошибка лишь цементируется.» | `levers.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N30 | «Это control boundary, не универсальная пошаговая форма.» (phase separation) | `levers.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N31 | «Не требуй от модели раскрывать приватную chain-of-thought.» | `levers.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N32 | «Objective rebasing: вместо абстрактного „сделай хороший ответ“ skill задаёт меру, которая п… | `levers.md` | «проектируешь механизм → `mechanism.md`, `position.md`, `levers.md`» |  |
| N33 | «Operator без причины становится optional ceremony. Причина без operator-а — объяснительный … | `demos.md` | «примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`» |  |
| N34 | «Для центрального механизма дай несколько коротких контрастивных примеров прямо в `SKILL.md`… | `demos.md` | «примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`» |  |
| N35 | «Число не является механизмом; различающий probe является.» | `demos-examples.md` | «примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`» |  |
| N36 | «Примеры иллюстрируют операции, не поставляют факты реального проекта.» | `demos-examples.md` | «примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`» |  |
| N37 | «Его claim — перенос decision structure, не автоматический рост точности задачи.» | `demos-examples.md` | «примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`» |  |
| N38 | «Не подсовывай ответ evaluation-кейса и не делай один доменный пример единственным способом … | `demos-examples.md` | «примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`» |  |
| N39 | «Пример финального output часто учит стилю и заполнению полей.» | `demos.md` | «примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`» |  |
| N40 | «Его форма должна исполнять собственный метод» | `demos.md` | «примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`» |  |
| N41 | «Это не требование копировать стиль или секции — совпадать должна decision structure.» | `demos.md` | «примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`» |  |
| N42 | «Раннее соблюдение не доказывает устойчивость»; «Это long-horizon risk, а не редакционная ак… | `demos.md` | «примеры и конгруэнтность формы → `demos.md`, `demos-examples.md`» |  |
| N43 | «Одна поверхность владеет одним положительным моментом и одним связным изменением. Не превра… | `surface.md` | «поверхность, граница, stop → `surface.md`, `stop.md`» |  |
| N44 | «не выбирай surface раньше диагноза: иначе формат начинает диктовать объяснение проблемы» | `surface.md` | «поверхность, граница, stop → `surface.md`, `stop.md`» |  |
| N45 | «**no new surface** — ближайший owner уже способен вернуть механизм в нужный момент.» | `surface.md` | «поверхность, граница, stop → `surface.md`, `stop.md`» |  |
| N46 | «Не добавляй меню соседей, handoff catalog или объяснение действий для случаев, где его поло… | `surface.md` | «поверхность, граница, stop → `surface.md`, `stop.md`» |  |
| N47 | «Отрицательную boundary добавляй только когда она предотвращает реальный authority overclaim.» | `surface.md` | «поверхность, граница, stop → `surface.md`, `stop.md`» |  |
| N48 | «Внешнюю skill/tool dependency объявляй лишь когда без неё невозможно выполнить положительны… | `surface.md` | «поверхность, граница, stop → `surface.md`, `stop.md`» |  |
| N49 | «Он не scaffold-ит package, не выполняет tool workflow, не распространяет projection и не вы… | `stop.md` | «поверхность, граница, stop → `surface.md`, `stop.md`» |  |
| N50 | «Если necessity или transfer нельзя сформулировать, вердикт — не добавлять правила, а вернут… | `stop.md` | «поверхность, граница, stop → `surface.md`, `stop.md`» |  |
| N51 | «Не компенсируй это расширением description: вернись к сцене, owner или границе.» | `stop.md` | «поверхность, граница, stop → `surface.md`, `stop.md`» |  |
| N52 | «Capability list и безрисковое „helps with...“ не дают модели причины потратить контекст.» | `discovery.md` | «пишешь `description` → `discovery.md`, `canvas.md`» |  |
| N53 | «`description` — не summary, а убедительный указатель: **condition × stake**.» | `discovery.md` | «пишешь `description` → `discovery.md`, `canvas.md`» |  |
| N54 | «общий trigger phrase — сигнал ownership/collision, а не повод для буквального dedupe» | `discovery.md` | «пишешь `description` → `discovery.md`, `canvas.md`» |  |
| N55 | «Проверь его против полного live candidate canvas и реальных near-misses» | `discovery.md` | «пишешь `description` → `discovery.md`, `canvas.md`» |  |
| N56 | «Cut test: if removing a phrase does not change which skill should activate against live nei… | `discovery.md` | «пишешь `description` → `discovery.md`, `canvas.md`» |  |
| N57 | «Prefer path/file/action over abstract categories that require self-classification»; Hot Zon… | `discovery.md`, `glossary-6.md` | «пишешь `description` → `discovery.md`, `canvas.md`» | показ |
| N58 | «_Avoid_: 1024 as target, premature shortening» (Description Budget) | `discovery.md`, `glossary-6.md` | «пишешь `description` → `discovery.md`, `canvas.md`» | показ |
| N59 | «`disable-model-invocation: true` suits a deliberate/manual skill that should not compete in… | `canvas.md` | «пишешь `description` → `discovery.md`, `canvas.md`» |  |
| N60 | «Это coverage map, не анкета: покажи только load-bearing ответы, способные изменить дизайн и… | `frame.md` | «отдаёшь результат владельцу → `frame.md`, `loop.md`» | показ |
| N61 | «Не создавай отдельный файл ради формы, если локальный проект не назначил ему owner.» | `frame.md` | «отдаёшь результат владельцу → `frame.md`, `loop.md`» | показ |
| N62 | «Если claim зависит от поведения модели, зафиксируй resolved model, дату наблюдения и смену … | `frame.md` | «отдаёшь результат владельцу → `frame.md`, `loop.md`» | показ |
| N63 | «Stop/sunset: когда дизайн достаточен и какой сигнал потребует пересмотра.» | `frame.md` | «отдаёшь результат владельцу → `frame.md`, `loop.md`» | показ |
| N64 | «Явная подпись владельца нужна, когда дизайн интерпретирует его намерение, меняет authority,… | `loop.md` | «отдаёшь результат владельцу → `frame.md`, `loop.md`» |  |
| N65 | «перечитай его точный релевантный block в активный контекст; существование файла и память о … | `loop.md` | «отдаёшь результат владельцу → `frame.md`, `loop.md`» |  |
| N66 | «Если block устарел, сначала revise/reopen его, а не проявляй верность ошибочному прошлому р… | `loop.md` | «отдаёшь результат владельцу → `frame.md`, `loop.md`» |  |
| N67 | «Новый core assumption, несработавший прогноз или форма без изменившегося решения reopen-ят … | `loop.md` | «отдаёшь результат владельцу → `frame.md`, `loop.md`» |  |
| N68 | «Прогноз не является доказательством переноса, но ловит красивый механизм без causal grip» | `loop.md` | «отдаёшь результат владельцу → `frame.md`, `loop.md`» |  |
| N69 | «Модель сама формулирует полный черновик … человек или semantic owner делает дешёвое узнаван… | `loop.md` | «отдаёшь результат владельцу → `frame.md`, `loop.md`» |  |
| N70 | «Структурная validation доказывает только читаемость package. Prompt visibility доказывает т… | `evidence-1.md` | «доказываешь изменение, режешь старое → `evidence-1.md`, `evidence-2.md`, `evidence-by-claim.md`» |  |
| N71 | «Не требуй тяжёлого benchmark для маленькой правки, но не называй semantic перенос доказанны… | `evidence-1.md` | «доказываешь изменение, режешь старое → `evidence-1.md`, `evidence-2.md`, `evidence-by-claim.md`» |  |
| N72 | «используй matched resampling: одна непоказанная ситуация, тот же resolved model и settings … | `evidence-1.md` | «доказываешь изменение, режешь старое → `evidence-1.md`, `evidence-2.md`, `evidence-by-claim.md`» |  |
| N73 | «Один удачный run доказывает возможность, но не сдвиг вероятности.» | `evidence-1.md` | «доказываешь изменение, режешь старое → `evidence-1.md`, `evidence-2.md`, `evidence-by-claim.md`» |  |
| N74 | «Для routing нужны use/skip/near-miss cases против живых соседей.» | `evidence-2.md` | «доказываешь изменение, режешь старое → `evidence-1.md`, `evidence-2.md`, `evidence-by-claim.md`» |  |
| N75 | «Не прогоняй фиксированный ритуал всех проверок; выбирай evidence, которое различает именно … | `evidence-2.md` | «доказываешь изменение, режешь старое → `evidence-1.md`, `evidence-2.md`, `evidence-by-claim.md`» |  |
| N76 | «Сила evidence растёт вместе с широтой, частотой, риском, credential/network effects, trigge… | `evidence-2.md` | «доказываешь изменение, режешь старое → `evidence-1.md`, `evidence-2.md`, `evidence-by-claim.md`» |  |
| N77 | «Перед добавлением нового правила проведи delete-first pass: убери obsolete scaffolding, пов… | `evidence-2.md` | «доказываешь изменение, режешь старое → `evidence-1.md`, `evidence-2.md`, `evidence-by-claim.md`» |  |
| N78 | «Не удаляй causal explanation или thought demonstration, если без них controller снова превр… | `evidence-2.md` | «доказываешь изменение, режешь старое → `evidence-1.md`, `evidence-2.md`, `evidence-by-claim.md`» |  |
| N79 | «Elastic defense: a failed run is rescued by a post-hoc explanation when no bypass predictio… | `anti-patterns-4.md`, `evidence-2.md` | «узнать провал по имени → `failures.md`; broad audit → `anti-patterns-1…4.md`» |  |
| N80 | «No mechanism ablation: a central explanation or example is assumed to cause the effect with… | `anti-patterns-4.md`, `evidence-2.md` | «узнать провал по имени → `failures.md`; broad audit → `anti-patterns-1…4.md`» |  |
| N81 | «Structural, routing, cognitive-transfer, operational, and distribution claims are reported … | `portable-done.md` | «собираешь пакет, решаешь что вынести → `core-contract.md`, `portable-done.md`» |  |
| N82 | «Точные значения выделенных архитектурных терминов бери из `GLOSSARY.md`, только когда терми… | **ядро** (строка-маршрут) | «термин двусмыслен или меняется сам словарь → `glossary-1…10.md`» — условие перенесено дословно, адрес переписан на новые файлы |  |
| N83 | «`references/deep-audit.md` — только для полного аудита landscape/control system, не для одн… | **ядро** (строка-маршрут) | «полный аудит landscape, не для одной правки → `deep-audit-1…3.md`…» — условие перенесено дословно, адрес переписан |  |
| N84 | «Open this only when the output includes "make a local skill", "rewrite this skill", or "por… | `portable-done.md` | «собираешь пакет, решаешь что вынести → `core-contract.md`, `portable-done.md`» |  |
| N85 | «Do not instruct the agent to read every reference. Give each bundled file an action-changin… | `core-contract.md` | «собираешь пакет, решаешь что вынести → `core-contract.md`, `portable-done.md`» |  |
| N86 | «Keep reference files one level deep … A body under 500 lines is a ceiling, not a target.» | `core-contract.md` | «собираешь пакет, решаешь что вынести → `core-contract.md`, `portable-done.md`» |  |
| N87 | «Do not move the causal core out merely to make `SKILL.md` short.» | `portable-done.md` | «собираешь пакет, решаешь что вынести → `core-contract.md`, `portable-done.md`» |  |
| N88 | «`SKILL.md` is the smallest causally complete contract, not a textbook»; «Include only **Del… | `core-contract.md` | «собираешь пакет, решаешь что вынести → `core-contract.md`, `portable-done.md`» |  |
| N89 | «Scripts are justified by deterministic behavior, external tooling, or a recurring fragile o… | `core-contract.md` | «собираешь пакет, решаешь что вынести → `core-contract.md`, `portable-done.md`» |  |
| N90 | «Name authority, required output, and side-effect boundaries only when they change the permi… | `core-contract.md` | «собираешь пакет, решаешь что вынести → `core-contract.md`, `portable-done.md`» |  |
| N91 | «Verify the live Claude skill root and resolved model rather than inferring them from an ali… | `canvas.md` | «пишешь `description` → `discovery.md`, `canvas.md`» |  |
| N92 | «Model, effort, thinking, long-run, and fallback rules belong to the current model owner/run… | `platform-1.md` | «Claude runtime, метаданные, источники → `platform-1.md`, `platform-2.md`» |  |
| N93 | «Generic self-review, an automatic verifier, and fan-out are not part of the portable baseli… | `platform-1.md` | «Claude runtime, метаданные, источники → `platform-1.md`, `platform-2.md`» |  |
| N94 | «Older Claude 4.x skills and prompts are historical migration evidence, not an active baseli… | `platform-1.md` | «Claude runtime, метаданные, источники → `platform-1.md`, `platform-2.md`» |  |
| N95 | «An Anthropic-endorsed claim requires a current official source»; «Label local engineering a… | `platform-1.md` | «Claude runtime, метаданные, источники → `platform-1.md`, `platform-2.md`» |  |
| N96 | «No `agents/openai.yaml`, Codex-only tool names, or Codex validation commands remain in the … | `platform-2.md`, `portable-done.md` | «Claude runtime, метаданные, источники → `platform-1.md`, `platform-2.md`» |  |
| N97 | «It does not merely make Opus 5 or Fable 5 perform an authoring checklist»; «Its step list i… | `platform-2.md` | «Claude runtime, метаданные, источники → `platform-1.md`, `platform-2.md`» |  |
| N98 | «`SKILL.md` frontmatter has `name` and `description`; optional `disable-model-invocation` an… | `platform-2.md` | «Claude runtime, метаданные, источники → `platform-1.md`, `platform-2.md`» |  |
| N99 | «Keep the order. Current-state map and forces come before failure scan.» | `deep-audit-1.md` | «полный аудит landscape, не для одной правки → `deep-audit-1…3.md`, шаблон отчёта `deep-audit-report.md`» |  |
| N100 | «If the upstream layer is missing or stale, report that instead of compensating with general… | `deep-audit-1.md` | «полный аудит landscape, не для одной правки → `deep-audit-1…3.md`, шаблон отчёта `deep-audit-report.md`» |  |
| N101 | «Use exact handles, not classes. "Hook exists" is too vague; name event, matcher, and action.» | `deep-audit-1.md` | «полный аудит landscape, не для одной правки → `deep-audit-1…3.md`, шаблон отчёта `deep-audit-report.md`» |  |
| N102 | «Generic future change without a signal is out of scope.» | `deep-audit-1.md` | «полный аудит landscape, не для одной правки → `deep-audit-1…3.md`, шаблон отчёта `deep-audit-report.md`» |  |
| N103 | «Done when failures are classes, not a flat patch list»; «One failure -> one prescription: p… | `anti-patterns-1.md`, `deep-audit-1.md` | «узнать провал по имени → `failures.md`; broad audit → `anti-patterns-1…4.md`» |  |
| N104 | «Do not recommend a new surface until reuse-first has failed.» | `deep-audit-1.md` | «полный аудит landscape, не для одной правки → `deep-audit-1…3.md`, шаблон отчёта `deep-audit-report.md`» |  |
| N105 | «Prompt-level fixes are acceptable only when runtime/skill/agent alternatives are unnecessar… | `deep-audit-2.md` | «полный аудит landscape, не для одной правки → `deep-audit-1…3.md`, шаблон отчёта `deep-audit-report.md`» |  |
| N106 | «Do not publish prescriptions without reuse-first gate, owner, observable signal, and valida… | `deep-audit-report.md` | «полный аудит landscape, не для одной правки → `deep-audit-1…3.md`, шаблон отчёта `deep-audit-report.md`» | показ |
| N107 | «Include minimize pass even when nothing was removed»; «Chesterton's fence check: what break… | `deep-audit-2.md`, `deep-audit-report.md` | «полный аудит landscape, не для одной правки → `deep-audit-1…3.md`, шаблон отчёта `deep-audit-report.md`» | показ |
| N108 | «For load-bearing routing or enforcement changes, use an empirical probe when reasonable. Fo… | `deep-audit-2.md` | «полный аудит landscape, не для одной правки → `deep-audit-1…3.md`, шаблон отчёта `deep-audit-report.md`» |  |

| N-GLOS | конструкция словаря «термин + `_Avoid_`: чем его подменяют» (~40 терминов) | `glossary-1.md`…`glossary-10.md` | «термин двусмыслен или меняется сам словарь → `glossary-1…10.md`» | показ |

## Партитура показа (дословно, сжатию не подлежит)

| Блок | Файл | Почему показ |
| --- | --- | --- |
| Выдача `Skill Frame` — то, что владелец получает и по чему принимает дизайн | `references/frame.md` | видимый выход адресован владельцу |
| Шаблон итогового отчёта deep-audit (`Output Shape`) | `references/deep-audit-report.md` | шаблон итогового отчёта |
| Обучающий словарь архитектурных терминов вместе со строками `_Avoid_` | `references/glossary-1.md`…`glossary-10.md` | владелец учится словарю по этому тексту |

Все три блока перенесены **дословно**, без правки формулировок; резалась только
разбивка на файлы, и только по границам самостоятельных единиц (термин, пункт
шаблона), чтобы норма не разрывалась между файлами.

## Записи об удалении

Удалялись только дубли; каждая удалённая строка имеет живой канон в пакете.

| Что удалено | Откуда | Причина |
| --- | --- | --- |
| «## Условные routes» целиком (S 467–477) | `SKILL.md` | функция перенесена в блок «Маршруты» ядра; все пять условий сохранены как строки-маршруты, адреса переписаны на новые файлы |
| «Точные значения выделенных архитектурных терминов бери из `GLOSSARY.md`, только когда термин двусмыслен или меняется сам словарь» (S 47–49) | `SKILL.md` | то же: условие «двусмыслен или меняется сам словарь» стоит в строке-маршруте ядра дословно |
| «Расширенный каталог для system-wide audit — `references/anti-patterns.md`» (S 464–465) | `SKILL.md` | маршрут в ядре: «broad audit → `anti-patterns-1…4.md`» |
| Раздел «## Class and Body Shape» (PA 61–77) | `platform-skill-authoring.md` | дубль `class.md` (N10–N15) и `core-contract.md`; канон — `class.md` |
| Оглавления «## Contents» (PA 8–17) | `platform-skill-authoring.md` | оглавление файла, которого больше нет; функцию несёт блок маршрутов ядра |
| Раздел «## Contract», 15 пунктов (LC 8–70), кроме `Progressive disclosure` | `local-skill-contract.md` | дубль разделов `SKILL.md`; см. канон по пунктам ниже |

Канон по пунктам удалённого `LC ## Contract`:

| Пункт LC | Канон в пакете |
| --- | --- |
| Failure trace | `trace.md` (+ N01 дословно в ядре) |
| Necessity proof | `necessity.md` |
| Deficit and proxy | `trace.md`, `mechanism.md` |
| Point of action | `position.md` |
| Surface gate | `class.md`, `surface.md` |
| Type | `class.md` |
| Cognitive core | `mechanism.md`, `levers.md` |
| Operational core | `class.md` |
| Thought demonstrations | `demos.md`, `demos-examples.md` |
| Causal cells and form | `demos.md` |
| Trigger and description | `discovery.md` |
| Progressive disclosure | **не удалён** — перенесён дословно в `portable-done.md` (N87) |
| Boundary | `surface.md` |
| Minimality | `evidence-2.md` (N77, N78) |
| Validation | `evidence-2.md`; уникальная строка «register the bypass prediction first…» перенесена дословно |

## Пакет эскалации владельцу

Метод запрещает решать это самому — три пункта уходят к владельцу.

1. **N87 против нормы ≤2000.** «Do not move the causal core out merely to make
   `SKILL.md` short» — прямой конфликт с нормой формы, которую владелец велел
   внести в ядро дословно. Сейчас causal core (`why.md`, `trace.md`,
   `necessity.md`, `mechanism.md`) вынесен из ядра, и в ядре остались только
   гейт первого хода, норма формы и маршруты. Конфликтную пару молча сжимать
   нельзя — она предъявлена, а не разрешена.
2. **Стеснённое ядро.** В ядре не осталось причинного объяснения, зачем
   вмешательство вообще меняет поведение; оно живёт в `why.md` за маршрутом.
   Если приёмка покажет, что агент выполняет маршруты как churn без диагноза,
   правильный ход — не дописывать ядро, а поднять `why.md` в hot path.
3. **Устаревший путь внутри показа.** В шаблоне отчёта
   (`deep-audit-report.md`, блок `References Applied`) стоит строка
   `- references/deep-audit.md`. Файла с таким именем в пакете нет, но блок —
   партитура показа, и править его без владельца запрещено.

## Что осталось непроверенным

- Батарея на этом кандидате **не прогонялась**: пересборщик её не видит по
  протоколу. Сдаются только символы и поимённая сверка инвентаря; доля
  совпавшего первого хода и поведение на реальной задаче — за приёмкой.
- Заметность (вес нормы после переезда в другой файл) статикой не меряется:
  106 дословных совпадений доказывают целость множества обязательств и молчат
  о том, сработает ли норма под нагрузкой.
