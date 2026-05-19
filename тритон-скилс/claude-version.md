# Claude-версия

Этот файл показывает, как Claude-сторона агентной системы отвечает на твои шесть исходных запросов. Под каждой цитатой — текущие решения: какие скилы держат какие поверхности правды, какие хуки усиливают дисциплину на уровне runtime и где живёт что.

Общая логика системы: главный контракт проекта живёт в `_ops/GOAL.md` (shape owner — `1strategy-docs`, thinking owner до commit — `1strategy`); короткий человеческий контекст и on-ramp — в `README.md` (owner — `1strategy-docs`); shape `_ops/PROJECT-ROADMAP.md` (формат, что туда идёт) держит `1strategy-docs`, а content updates (current path сдвинулся, Stage closed) — `1planning`; устойчивые правила и предпочтения — в `_ops/criteria/*.md` (owner — `1user-truth`); central index папочного графа (`depends-on` / `related-when` / `veto-class`) — в `_ops/project-graph.md` (owner — `1instruction-layer`). Корневые `AGENTS.md` / `CLAUDE.md` цитируют 3–5 строк эссенции из `_ops/GOAL.md#Что делаем` — fresh agent видит контракт проекта до любых routing-правил.

Moment-уровень работает через runtime и инструкционный слой, не через отдельные moment-скилы: **PreToolUse hook `criteria-gate.py`** перед каждой substantive правкой (`Edit` / `Write` / `MultiEdit` / mutating `Bash`) блокирует write без prior Read из applicable `_ops/criteria/*.md`; **UserPromptSubmit hook `prompt-submit-reminder.py`** — threshold-based intent-grounding только на первом ходу сессии (через `session-state.turn_id`); task-level anchor перед нетривиальной работой — durable правило в root инструкциях («прочитай `_ops/GOAL.md` + `_ops/PROJECT-ROADMAP.md` + применимые criteria до содержательного ответа»); closeout перед claim «готово» — `1work-review` сравнивает diff с Definition of done из GOAL, criteria и evidence; **Stop hook** упрощён до структурного маркера `1work-review: да` (verbatim citation теперь живёт в Output template самого `1work-review`, не дублируется хуком).

## 1

> Мне надо чтобы ИИ давал мне картинку как мы дойдём от 0 до готово, но ввиде очень краткого и понятного файла, чтобы я видел текущий подход к работе и понимал на сколько мы далеко или близко к цели. Но в тоже время чтобы этот файл был динамичный ведь цели меняются

### Текущие решения

`1strategy-docs` пишет `_ops/GOAL.md` — главный контракт проекта: что делаем, что не делаем, definition of done и stop rules. До commit идёт обсуждение в `1strategy` (mental tools, варианты approach, ground-check); файлы пишет `1strategy-docs`. Если меняется outcome, scope или stop rules, маршрут — `1strategy` → `1strategy-docs`, а не roadmap-правка.

`1strategy-docs` также держит `README.md`, но только как короткий контекст: vision, approach, motivation, on-ramp. README больше не является главным strategy-документом.

Shape `_ops/PROJECT-ROADMAP.md` (формат, что туда идёт) — у `1strategy-docs`; content updates (current path сдвинулся, Stage closed, position update) — у `1planning`. Карта динамична: фронт сдвигается при смене целей. В polygon-режиме roadmap описывает «как сейчас работать», а не обязательную цепочку стадий и не scope-контракт.

`1work-review` сравнивает diff/artifact с целью, criteria и evidence — что уже закрыто, что не доказано, где нужно продолжать.

## 2

> Мне надо чтобы всё что я сказал во время любого обсуждения или решения, ИИ записывал информацию обо мне в нужный файл критериев, если такого нет то создал бы. Я не хочу одно и то же писать много раз с каждой новой сессии или при смене ИИ агента. Это одновременно и память обо мне и моих предпочтениях и одновременно критерии принятия.

### Текущие решения

`1user-truth` переводит твои устойчивые сигналы (preference, red line, success picture, motivation, факт о пользователе) в `_ops/criteria/*.md`. Если подходящего criteria-файла нет, скил его создаёт. Two modes: passive writer при прямом durable-сигнале; active probe (через `AskUserQuestion` для 1–3 коротких вопросов или handoff в `1interview-tool` для ≥4 связанных) если правило собирается без verbatim user source. **Tier-1 эмбеддинг-защита от дублей:** перед каждой записью criterion'а скил обязан запустить `md_navigator.py search _ops/criteria/ "<суть кандидата>" --limit 3` — если top-1 уже описывает похожее правило (Dense ≤ ~0.6 с RRF gap к #2), кандидат relabel'ится как **Confirmation**, write отменяется или превращается в merge в существующую строку. Это решение прямой проблемы «одно и то же много раз с каждой новой сессии».

**PreToolUse hook `criteria-gate.py`** (`~/.claude/skills/1start-here/scripts/`) — реальный write-gate: блокирует `Edit` / `Write` / `MultiEdit` / mutating `Bash` без prior Read из applicable `_ops/criteria/*.md`. Fail-open на ambiguous mapping, чтобы не блокировать legitimate работу. Если ни один criterion не покрывает зону работы, агент останавливается и идёт в `1user-truth` для авторинга нового, без правки под near-miss anchor.

**UserPromptSubmit hook `prompt-submit-reminder.py`** — threshold-based intent-grounding, активен только при `turn_id == 1` через `session-state.py` shared memory. Один раз за сессию напоминает назвать что услышано до substantive ответа; после первого хода — молчит, чтобы не превратиться в декорацию.

**Stop hook `stop-work-review.py`** упрощён: если в сессии были file-changes, финальный ответ требует маркер `1work-review: да`; если редактировался `_ops/criteria/*.md` — дополнительный маркер `1user-truth: да`. Verbatim-цитата anchor-доков теперь живёт в Output template самого `1work-review` skill body, не дублируется хуком (детект-vs-decide разделение: hook ловит структурный факт, skill body владеет cognitive work).

`_ops/interviews/**` — временный интерактивный слой intake для случаев, когда нужно ≥4 связанных вопросов с предсказуемыми вариантами или batch-параметры по N items. Owner intake-формы — `1interview-tool` (горизонтальный, прямой пятый ОБЯЗАН триггер): caller (`1user-truth` / `1strategy` / `1planning` / `1instruction-layer`) даёт intent, tool строит Meta Bind форму в `_ops/interviews/YYYY-MM-DD-topic.md` (`INPUT[textArea/inlineSelect/inlineList/toggle]:answer_*` поля, callouts, `<details>` для agent-only промптов). После команды пользователя «проверь / разбери / перевари» или `status: ready` control возвращается caller'у для processing: durable answers → `_ops/criteria/*.md` через `1user-truth`, остальное в owners (`1planning`, `1strategy`, `knowledge/`, `_ops/findings/`). Файл уходит в `_ops/interviews/_archive/` только когда весь смысл перенесён. Правила слоя — `_ops/criteria/interview-intake-workflow.md`.

## 3

> Мне надо чтобы предже чем выбрать подход к работе ИИ предлагал разные варианты подхода к задачам, включая работу на главной дорожной картой, так и разными подходами внутри задач, чтобы мы шли к главной цели максимально эффективным и продуманым путём так чтобы мы ничего не сломали

### Текущие решения

`1strategy` раскрывает 1–2 локальные развилки или 2–4 широких выбора до фиксации плана; сравнивает варианты по скорости, сложности, риску и будущим ограничениям. Он обязательно включается при правке `_ops/GOAL.md` или попытке агента изменить scope проекта.

`1step-back` помогает выйти из кривой рамки, когда подход уже выбран, но сама постановка цели может быть неверной.

`1assumption-audit` после выбора подхода проверяет почву под планом: для каждого критерия приёмки выписывает предпосылки и помечает их как блокер, допущение или сигнал на пересмотр подхода. Так «продуманно и ничего не сломали» — не вера, а явный список проверенных условий.

`_ops/findings/**` — временная полка только для реальных актуальных проблем, которые ещё не стали задачами, критериями или решениями. Owner — `1findings`: quick-note path (3 строки и обратно к задаче) или полный фильтр (Evidence + Current tension + Owner gap). Из находки маршрутизация: approach → `1strategy`, roadmap/task → `1planning`, AGENTS/CLAUDE/criteria/canon → `1instruction-layer`, durable preference → `1user-truth`. Когда проблема решена или перенесена в правильный owner-файл, файл уходит в `_ops/findings/_archive/`; archive значит «файл не активен», не обязательно «решено». Правила слоя — `_ops/criteria/ops-findings-layer.md`.

## 4

> Мне надо чтобы после того как мы обсудили подходы к работе, обсудили цель и коротко как мы до неё дойдём, мы писали связанные файлы, где дорожная карта это первый уровень планирования, имя стадий это название папок а сами файлы уже второй уровень планирования внутри стадий а подзадачи написанные внутри уже третий

### Текущие решения

Bootstrap-скрипт `init-three-level.sh` (`~/.claude/skills/1start-here/scripts/`) на старте проекта создаёт shape одним проходом: skeleton'ы `README.md`, `AGENTS.md`, `CLAUDE.md` (auto-loaded инструкции), `_ops/GOAL.md` (outcome-first контракт TBD), минимальный `_ops/PROJECT-ROADMAP.md` (current path TBD, без Goal-блока — контракт живёт в `_ops/GOAL.md`), пустой `_ops/project-graph.md` skeleton (central index папочного графа), пустые `_ops/criteria/`, `_ops/plans/`, `_ops/interviews/{,_archive}/`, `_ops/findings/{,_archive}/` с `.gitkeep`. Скрипт fill-missing и idempotent — безопасно перезапускать на старых проектах. Владельцы наполняют содержимым через свои скилы.

`1strategy` обсуждает strategy в чате (mental tools, варианты approach, ground-check, raw desire), файлов не пишет. `1strategy-docs` пишет `_ops/GOAL.md` — главный strategy-контракт проекта (outcome, in scope, NOT in scope, definition of done, stop rules). `README.md` он же держит отдельно как короткий context/on-ramp, не как scope-контракт и не как текущий статус.

Recursive planning держит `1planning`, единый owner трёх уровней:

- **Level 1** — `_ops/PROJECT-ROADMAP.md` (текущий путь, режим или стадии когда проект реально работает по стадиям). В polygon-режиме это «как сейчас в этом проекте работать», не обязательная цепочка и не дубликат `_ops/GOAL.md`.
- **Level 2** — task-файлы `_ops/plans/**/task-*.md`. Когда проект работает по стадиям, имена папок совпадают с именами стадий (`phase-NN-<slug>/`).
- **Level 3** — подшаги внутри task-файла.

`1planning` сужает фокус постепенно и материализует только активный фронт неопределённости — всё дерево заранее не разворачивается. Task-файл обязан ссылаться на применимые `_ops/criteria/*.md` и агентные инструкции через раздел `Применимые критерии и инструкции`. `_ops/plans/**` используется только по явному запросу для активной сложной работы; в polygon-режиме это не backlog. При изменении верхнего уровня нижние task-файлы reconciled/archived через `1planning`; каждая папка внутри `_ops/plans/**` имеет свой `_archive/`.

## 5

> Мне надо чтобы ИИ активно читал планы, дорожну карту, выполнял задачи следуя критериям принятия, чтобы он точно понимал в любой момент что мы делаем, на какой мы стадии и зачем и каким образом что то делать. Чтобы он мог почти автономно делать большие цепи задач и при этом был бы максимально ментально синхронизирован со мной.

### Текущие решения

`1start-here` даёт карту скиллов, стартовый маршрут и обязательные case-based триггеры: instruction-layer audit при подозрении на рассинхрон, `1strategy` при raw desire / hidden branch / scope-changing ходе, `1planning` при task scope/prerequisites, `1user-truth` при durable signal, `1interview-tool` при ≥4 связанных вопросах / batch-параметрах.

Отдельный pre-work skill ретайрнут. Его бывшие функции распределены по слоям:

- **Owner/criteria check** перед substantive `Edit` / `Write` / `MultiEdit` / mutating `Bash` → PreToolUse hook `criteria-gate.py` (структурное принуждение: блокирует write без prior Read из applicable `_ops/criteria/*.md`, fail-open на ambiguous mapping) плюс ответственность owner-скилла прочитать applicable файл.
- **Task-level anchor** перед нетривиальной работой → durable правило в root `AGENTS.md` / `CLAUDE.md`: прочитать `_ops/GOAL.md`, `_ops/PROJECT-ROADMAP.md`, применимые `_ops/criteria/*.md` и agent instructions до содержательного ответа.
- **Ground-check предпосылок** → `1strategy` Phase 1 (perimeter + key preconditions внутри strategy discussion) и `1assumption-audit` (manually-invoked более глубокая инвентаризация).
- **Paraphrase guard** → reference-файл `1strategy/references/anti-paraphrase.md` плюс anti-pattern `Paraphrase stop` в `1start-here/SKILL.md`.
- **Owner-routing «сигнал → owner skill»** → reference-файл `1work-review/references/routing-matrix.md` (canonical destination map).
- **Closeout-проверка фактического применения owner/criteria** → `1work-review`.

`1cli-tools` даёт быстрые факты через CLI (rg, knip, lychee, ast-grep, gitleaks): файлы, ссылки, dead code, broken docs, package shape, security.

`1work-review` закрывает работу только после сверки diff/artifact с целью, criteria и evidence; разделяет режим repair-until-pass (когда явно просили закрыть задачу) и read-only audit. **Tier-1 эмбеддинг-пробуска для нового файла:** если сессия создала новый `.md` в корпусе с warm `1md-navigator` index — `md_navigator.py read-related <new-file> --semantic-radius 5` показывает, нет ли уже файлов той же темы; топические соседи без backlink — finding «дубликат вместо update», route по природе (`1user-truth` / `1instruction-layer` / `1ia-audit`).

`1fresh-eyes` спавнит независимые субагенты со свежим контекстом, когда оркестратор сам не может надёжно проверить работу из своего окна. Два режима: parallel breadth (3–5 воркеров на независимые слайсы одной формы) или single deep-read одного артефакта, где self-review унесёт inherited bias. Промт каждому субагенту собирается так, чтобы компенсировать failure modes одновременно writer-LLM (sycophancy, paraphrase, auto-close) и orchestrator-LLM (frame inheritance, premature convergence). Это та ментальная свежесть, которую длинная цепь задач теряет автоматически — её нельзя вернуть в текущем окне, только привести из чистого.

Хуки на уровне runtime (`~/.claude/settings.json`, скрипты в `~/.claude/skills/1start-here/scripts/`) держат цепочку, разделяя структурный детект (hooks) и cognitive work (skill bodies):
- **SessionStart** (`session-start.sh`) запускает стартовый маршрут и печатает orientation slice `1start-here/SKILL.md`: orient-before-act, mandatory routing, local failure detectors, first-response contract.
- **UserPromptSubmit** (`prompt-submit-reminder.py`) — threshold-based intent-grounding только при `turn_id == 1` через `session-state.py` shared memory: напоминает одной фразой назвать что услышано и читать applicable criterion перед substantive правкой. После первого хода молчит.
- **PreToolUse** (`criteria-gate.py`, matcher `Edit|Write|MultiEdit|NotebookEdit|Bash`) — реальный write-gate: блокирует substantive write без prior Read из applicable `_ops/criteria/*.md`. Fail-open на ambiguous mapping.
- **Stop** (`stop-work-review.py`) после файловых правок требует маркер `1work-review: да`; если редактировался `_ops/criteria/*.md` — дополнительный маркер `1user-truth: да`. Verbatim-цитата anchor-доков теперь живёт в Output template `1work-review` skill body, не дублируется хуком (hook ловит факт, skill решает что писать).

## 6

> Мне надо чтобы ИИ понимал сам себя свои проблемы и всю систему и поэтому мог написать инструкции сам себе в проекте, чтобы улучшить использование скилов, понимал когда и в какой момент использовать скилы и как усилить их использование за счёт инструкций которые сам себе напишет и эти инструкции также должны сочетаться, со всей остальной системой узнавания меня, моих задачах, моей дорожной карты которую сам ИИ и пишет

### Текущие решения

`1instruction-layer` — единый entry-point для «куда живёт правило / механизм / матчер»: `CLAUDE.md`, папочные инструкции, criteria-ссылки или skill contract. Сам пишет prose-инструкции и держит central index папочного графа в `_ops/project-graph.md` (`depends-on` / `related-when` / `veto-class`); criteria-запись делегирует в `1user-truth`, GOAL/README/ROADMAP shape — в `1strategy-docs`, runtime — в `1start-here`, skill matcher — в `1skill-architect`. Owner Decision Map: `_ops/GOAL.md` (shape) → `1strategy-docs`, `README.md` → `1strategy-docs`, `_ops/PROJECT-ROADMAP.md` shape → `1strategy-docs` / content updates → `1planning`, `_ops/plans/**/task-*.md` + подшаги → `1planning`, `_ops/criteria/*.md` → `1user-truth`, `_ops/project-graph.md` + AGENTS.md / CLAUDE.md prose → `1instruction-layer`, hooks / permissions / MCP / settings.json → `1start-here`, SKILL.md / agent persona → `1skill-architect`, file-vs-folder shape / split / merge → `1ia-audit`. **Tier-1 эмбеддинг-защита от дублей правил:** перед finalizing owner — `md_navigator.py search _ops "<суть правила>" --limit 5` показывает, не лежит ли это правило уже где-то в criteria / AGENTS.md / GOAL.md; literal duplicate → не размещать, finding для merge. Для audit — `md_navigator.py overlaps _ops --threshold 0.75 --top 20` как automated cross-file duplication detector. `AGENTS.md` и корневой `CLAUDE.md` в самом начале содержат Goal-блок (3–5 строк цитата эссенции из `_ops/GOAL.md#Что делаем`) — fresh agent видит контракт проекта до любых routing-правил; цитата синхронизируется при правке `_ops/GOAL.md` в том же ходу через handoff из `1strategy-docs` сюда.

`1skill-architect` проектирует и чинит сами скилы — `SKILL.md`, agent persona, hook-script структуру — по trigger surface, не по списку capability. Скил с правильной capability, но кривой trigger surface, проваливается молча: модель его не находит. **Tier-1 эмпирический matcher test перед commit:** `md_navigator.py search ~/.claude/skills "<should-trigger phrase>" --scope descriptions --limit 5` — top-1 должен быть кандидат-скил; collision в top-3 = overtrigger/undertrigger risk. Плюс `md_navigator.py overlaps ~/.claude/skills --threshold 0.7` показывает существующие descriptions, делящие trigger surface с кандидатом. Это превращает дизайн trigger surface из догадки в измерение — синтетический eval (3 should-trigger + 3 should-not-trigger примера) дополняется эмпирическим против живого skills root.

`1md-navigator` — semantic-first reader для любого Markdown-корпуса: per-corpus persistent index (BM25F + dense embeddings через OpenRouter / `text-embedding-3-small`) питает `search` (natural-language section retrieval), `search --scope descriptions` (file-level orientation), `overlaps` (cosine pairs для smell detection), `cluster` (K-means топик-карта; `common_parent` mismatch с `centroid_path` — strong IA signal), `read-related --semantic-radius K` (dense neighbours за пределами explicit link set), `read-related --check-links` (links semantically far от anchor). Shape questions (`map`, `headings`, `read`) обслуживает тот же CLI. Это default entry-point для любого «meaning question» о Markdown; `rg` остаётся только для exact strings / regex / non-Markdown evidence. Tier-1 интеграция в `1user-truth`, `1skill-architect`, `1instruction-layer`, `1work-review`, `1ia-audit` — все они зовут navigator под капотом для anti-drift retrieval.

`1ia-audit` владеет container shape: file-vs-folder, split / merge / rename / move, owner truth размазан, view-vs-truth, retrieval path слаб, drift cost. Smell checklist (Container fit, Function split, Owner truth, Retrieval path, Distribution balance, Naming scent, View vs truth, Drift cost) применяется только к surface, который явно назван — не silent ко всему репо. **Глубоко Tier-1 интегрирован:** 6 embedding-aware probes (owner detection, smeared-without-cross-ref, off-topic link, folder cohesion, cluster-vs-folder, drift status) превращают IA verdicts из subjective taste в evidence-based.

`1start-here` в Claude также отвечает за runtime-часть: hooks, permissions, MCP, validators, `settings.json` и папочные правила (folder ownership). Bootstrap нового проекта (`init-three-level.sh`) тоже здесь.

`1step-back` подключается, когда сама рамка работы может быть кривой — anchoring, frame lock, sycophancy, goal misgeneralization. Файлов не пишет, только перенастраивает оптику.

`1strategy` поддерживает self-awareness через mental tools и ground-check, когда агент пишет инструкции себе — чтобы новые правила были согласованы с `_ops/GOAL.md`, criteria, roadmap и README. Thinking-only — файлы через `1strategy-docs`.

`1md-graph` держит portable Markdown graph hygiene: frontmatter-схема (`description` / `read-before-edit` / `edit-after-edit`), wikilinks, reverse-scan «кто сломается, если я правлю этот файл». Перед правкой важного `.md` показывает, откуда файл получает смысл, и что станет ложным после; после правки валидирует граф. Не владеет смыслом task, roadmap, criteria или knowledge файла — это остаётся у их owner-скилов; broad CLI-доказательства (rg/fd/lychee, stale references, mass cleanup) делегируются в `1cli-tools`, broad folder navigation, hybrid section search и semantic-overlap detection — в `1md-navigator`. Bundled CLI: `~/.claude/skills/1md-graph/scripts/md_graph.py` с командами `scan / deps / map / check / related / doctor`.

`1obsidian` делает Markdown удобным рабочим окном в Obsidian: callouts, сворачиваемые секции, wikilinks, properties, Bases и `.base` views, `obsidian-bases-kanban`. Не создаёт вторую правду рядом с `_ops/GOAL.md`, README, roadmap, criteria или task files — оформляет и показывает уже выбранную правду; graph-связи передаёт в `1md-graph`, project-truth changes — в `1planning` (roadmap content / task) / `1strategy-docs` (GOAL/README/ROADMAP shape) / `1user-truth` (criteria) / `1instruction-layer` (CLAUDE.md/AGENTS.md/project-graph), structured intake формы — в `1interview-tool`. References грузятся только когда меняют решение по структуре, интерактиву, ссылкам или view: `obsidian-primitives`, `visual-markdown`, `links-and-graph`, `bases-kanban`.
