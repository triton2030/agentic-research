# Codex-версия

Снимок обновлён 28 июня 2026 по живой Codex-поверхности. Это карта системы, а
не источник рабочего поведения.

Если этот файл расходится с живой системой, выигрывают:

- `/Users/triton/.codex/AGENTS.md` - верхняя рамка Codex;
- `/Users/triton/.codex/skills/*/SKILL.md` - живые контракты локальных скилов;
- `/Users/triton/.codex/agents/*.toml` - нативные read-only агенты Codex;
- `/Users/triton/.codex/config.toml` - модель, features, plugins и hooks;
- plugin/system skill bodies - встроенные и плагинные навыки Codex;
- `README.md`, `_ops/GOAL.md`,
  `_ops/project-graph.md` и `_ops/rules/*.md` - текущая правда этого
  репозитория.

Главная модель сейчас: один активный owner на момент работы. Стартовый маршрут
держат root-инструкции, локальные owner-файлы и live skill contracts; соседние
скилы остаются handoff-поверхностями, а не параллельными алгоритмами.

## Актуальный Контур

В глобальном конфиге Codex указан `gpt-5.5`; включены `multi_agent`,
`memories`, `hooks` и `goals`. Из плагинов включены GitHub, Vercel, Build Web
Apps, Browser и Chrome. Плагинные скилы не принадлежат этой папке: их надо
читать по live plugin contracts, когда они реально триггерятся.

Активные hooks из `/Users/triton/.codex/config.toml`:

- `PreToolUse` -> `md_graph_pre_edit_reminder.py`: reminder перед Markdown-
  правками через `apply_patch` / write tools;
- `PostToolUse` -> `post_tool_md_graph_collect.py`: собирает Markdown-правки;
- `Stop` -> `stop_md_graph_rollup.py`: делает graph rollup после Markdown-
  правок.

Hooks усиливают скилы, но не заменяют их. Старые pre-write идеи не считать
живым runtime, если их нет в текущем `config.toml`.

Локальные installed `1*`-скилы:

- `1goal` - форма и правки `README.md`, `_ops/GOAL.md`: context и scope
  contract без дублирования;
- `1planning` - task-планирование: task contracts, subtasks,
  archive/reconcile;
- `1break-down` - in-session разбивка тяжёлой или многошаговой задачи до
  правильной формы и ближайшего проверяемого фронтира без записи task-файла;
- `1interview-tool` - временные intake-формы в `_ops/interviews/**`, когда
  после context triage осталось 4+ user-only неизвестных;
- `1assumption-audit` - ручной `ground-check` уже выбранного подхода: какие
  предпосылки должны быть true, что доказано, где blocker/assumption/revision;
- Финальная сверка - прямой evidence-closeout текущего owner-а: просьба,
  качество, evidence, applied criteria/instructions/radius; видимый отчёт
  короткий, если риск маленький;
- `1findings` - горячие "что-то не так" находки и актуальные проблемы до
  стратегии, задачи, критерия или решения;
- `1fresh-eyes` - независимая проверка и нативные Codex subagents только по
  прямому запросу или подтверждённому brief;
- `1step-back` - разговорный reframe, когда сама рамка цели, метода или
  допущения может быть неверной;
- `1instruction-layer` - language-quality и placement текста инструкций:
  AGENTS, папочные инструкции, wording, criteria links, links-over-inline,
  lost-in-middle, literal scope;
- `1folder-contract` - системный контракт инструкций: Owner Decision Map,
  `_ops/project-graph.md`, folder graph, criteria delivery chain, hooks,
  validators, permissions, MCP/apps, runtime guardrails, Goal-quote sync;
- `1skill-architect` - устройство скилов: `SKILL.md`, `description`,
  references, scripts, `agents/openai.yaml`, validation, GPT-5.5 migration;
- `1ia-audit` - IA Markdown/docs/knowledge: owner truth, container fit,
  naming, retrieval path, section/file/folder shape;
- `1md-navigator` - semantic-first чтение Markdown-корпуса: `map`,
  `headings`, `search`, `overlaps`, `cluster`, `read`, `read-related`;
- `1md-graph` - graph/frontmatter/blast-radius: `description`,
  `read-before-edit`, `edit-after-edit`, wikilinks, preflight/changed/impact;
- `1obsidian` - Obsidian-facing Markdown UX: Bases, callouts, links, Meta Bind,
  kanban, без второй правды;
- `1smart-simple` - сокращение и усиление уже существующего текста без потери
  load-bearing смысла;
- `1cli-tools` - быстрые CLI evidence: `rg`/`fd`, links, cleanup, deps,
  security, JSON, token budget, repo pack.

Durable user truth сейчас не держит отдельный installed skill. Устойчивые
правила идут в owner-документы проекта или Codex Memories только по явной
просьбе пользователя; рабочие self-learning/finding факты идут через
`1findings`.

Специализированные локальные маршруты:

- `claude-mcp` - controlled Claude Bridge: независимый reviewer/advisor,
  run/peek/wait/kill, logs, relay и evidence;
- `gemini-mcp` - controlled Gemini peer: second opinion, web/file research,
  model comparison, managed runs и process-tail checks;
- `claude-skill` - только прямой запрос запускать Claude Code CLI или `claude`;
- `impeccable` - frontend design/polish с обязательными product/design/shape
  gates перед UI-правками;
- `screenshot-design` - standalone визуальная критика UI-скриншота;
- `design-subagents` - параллельная эстетическая критика конкретных UI-crops
  только по явному запросу;
- `pitch-coherence-audit` - аудит coherence и investor appeal после правок
  существующих pitch materials;
- `playwright` - browser automation через CLI-wrapper и свежие snapshots;
- `pdf` - чтение/создание/review PDF с render-first проверкой;
- `vercel-composition-patterns` - React composition: API shape, boolean props,
  shared state, context boundaries;
- `vercel-react-view-transitions` - React/Next.js View Transition API только
  для transitions, где есть понятная пространственная связь.

Нативные read-only агенты Codex:

- `auditor` - acceptance/evidence audit большой сдачи по критериям;
- `brooks` - структурный критик LLM-shaped artifacts и conceptual integrity;
- `smith` - критик trajectory/execution: task contract, execution и evidence.

## 1

> Мне надо чтобы ИИ давал мне картинку как мы дойдём от 0 до готово, но ввиде
> очень краткого и понятного файла, чтобы я видел текущий подход к работе и
> понимал на сколько мы далеко или близко к цели. Но в тоже время чтобы этот
> файл был динамичный ведь цели меняются

### Текущие решения для динамичной карты

Approach-choice больше не живёт в отдельном skill-owner-е. Текущий
owner/context pass отделяет желание от метода, показывает реальные развилки,
цену решений, слабые предпосылки и вариант "сделать меньше / отложить / не
делать", если это защищает цель.

`1goal` держит стратегические поверхности чистыми: `README.md` - короткий
on-ramp, `_ops/GOAL.md` - главный scope-контракт. Если
меняется outcome, scope, NOT in scope, definition of done или stop rules, это
не обычная planning-правка.

`1planning` держит динамичную рабочую карту после выбранной стратегии:
task-файлы в `_ops/plans/**` и подзадачи внутри task-файла. Верхняя рамка
берётся из `README.md` + `_ops/GOAL.md`, без отдельного верхнеуровневого
planning-файла.

Прямой evidence-closeout, `smith` и `auditor` проверяют не "красиво ли звучит",
а приблизила ли работа к цели, доказана ли готовность и не поехала ли
траектория.

## 2

> Мне надо чтобы всё что я сказал во время любого обсуждения или решения, ИИ
> записывал информацию обо мне в нужный файл критериев, если такого нет то
> создал бы. Я не хочу одно и то же писать много раз с каждой новой сессии или
> при смене ИИ агента. Это одновременно и память обо мне и моих предпочтениях и
> одновременно критерии принятия.

### Текущие решения для критериев

Отдельного live `1user-truth` и обязательного `_ops/criteria` слоя сейчас нет.
Устойчивую пользовательскую правду нельзя додумывать: нужен прямой user signal
и правильный owner. В зависимости от природы сигнала это project owner-док,
Codex Memories по явной просьбе пользователя или временная находка через
`1findings`.

Перед закреплением durable truth агент проверяет, не живёт ли смысл уже в
`AGENTS.md`, `_ops/GOAL.md`, `_ops/project-graph.md`, `_ops/rules/**`, skill
contract или памяти. Если правило похоже на wording/placement инструкции,
route в `1instruction-layer`; если на routing, hook, permission, system
contract или глобальный default — в `1folder-contract`.

`1interview-tool` включается только когда после чтения локального контекста
остаётся 4+ user-only неизвестных, batch decisions или per-item ответы. Он
строит временную форму в `_ops/interviews/**`; смысл потом возвращается
caller-скилу: durable truth в правильный owner, task scope в `1planning`,
wording правил в `1instruction-layer`, системный маршрут в `1folder-contract`.

Root-инструкции и локальный owner pass дают context reminder в момент работы, но
не пишут правила за пользователя. Если подходящего owner-а нет, правильный ход -
остановиться и получить user-backed truth, а не импровизировать criteria.

## 3

> Мне надо чтобы предже чем выбрать подход к работе ИИ предлагал разные
> варианты подхода к задачам, включая работу на главном плане, так и
> разными подходами внутри задач, чтобы мы шли к главной цели максимально
> эффективным и продуманым путём так чтобы мы ничего не сломали

### Текущие решения для выбора подхода

Развилки держит текущий owner/context pass. Он показывает только те варианты,
которые реально меняют cost, risk, scope, future constraint, reversibility или
owner route. Декоративные варианты не нужны; один сильный путь лучше трёх
псевдоальтернатив.

Проверка почвы теперь распределена:

- текущий owner/context pass проверяет ключевые предпосылки до заморозки
  подхода;
- `1assumption-audit` делает ручной глубокий `ground-check` выбранного подхода;
- `1planning` сохраняет blocker/assumption/order там, где это нужно для
  исполнения;
- текущий execution owner проверяет, применялись ли эти criteria и assumptions
  в работе.

`1step-back` нужен, когда может быть неверна сама рамка мышления. `1fresh-eyes`
нужен, когда риск в inherited context: поддакивание, frame lock,
auto-close, пропущенная связь. `1findings` удерживает подтверждённые актуальные
проблемы в `_ops/findings/**`, пока стратегия не решит, что с ними делать.

## 4

> Мне надо чтобы после того как мы обсудили подходы к работе, обсудили цель и
> коротко как мы до неё дойдём, мы писали связанные файлы, где верхняя рамка
> задаёт направление, имена рабочих направлений могут становиться папками, а сами файлы
> уже второй уровень планирования внутри стадий а подзадачи написанные внутри
> уже третий

### Текущие решения для уровней планирования

Живой owner один: `1planning`. Старые отдельные planning/task handles больше не нужны.

`1goal` держит границу между стратегическими документами: `GOAL` не становится
task tracker, `README` не дублирует scope-контракт.

`1planning` держит:

- task-файл в `_ops/plans/**/task-*.md`: только активная сложная работа по явному
  запросу или когда без task-файла scope станет мутным;
- подзадачи внутри task-файла.

`_ops/plans/` и каждая вложенная planning-папка имеют `_archive/`. Если task
меняется, вложенные подзадачи сначала reconcile/archive, а не продолжают управлять работой по
инерции. Если меняется форма задач, папок, owner truth или retrieval path,
`1planning` передаёт IA-вопрос в `1ia-audit`.

## 5

> Мне надо чтобы ИИ активно читал планы и task-файлы, выполнял задачи следуя
> критериям принятия, чтобы он точно понимал в любой момент что мы делаем, на
> какой мы стадии и зачем и каким образом что то делать. Чтобы он мог почти
> автономно делать большие цепи задач и при этом был бы максимально ментально
> синхронизирован со мной.

### Текущие решения для исполнения

Проектную работу запускает локальный context/owner pass: восстановить intent,
SoT/owner, применимые инструкции, dependency radius и один активный owner. Это
не отдельный installed skill и не ритуал для простого ответа, но защита от
ответа из вакуума, когда локальная система может изменить решение.

Перед исполнением:

- текущий owner/context pass держит approach/scope checkpoint;
- `1planning` держит task prerequisites и active frontier;
- локальные owner/criteria checks перед substantive write проверяют, какой
  файл владеет смыслом и какие criteria должны применяться;
- `1md-navigator` выбирает, что читать в большом Markdown-корпусе;
- `1md-graph` проверяет graph/frontmatter/blast-radius known targets;
- `1cli-tools` даёт bounded CLI evidence: ссылки, stale refs, deps, security,
  cleanup, package/code/docs facts.

Прямой evidence-closeout закрывает работу через evidence. Текущий owner
проверяет, выполнена ли исходная просьба, насколько качественно, какие сомнения
остались и были ли criteria/instructions/radius реально применены во время
работы. Маленькие успешные правки закрываются коротко; большой audit можно
отдать `auditor`.

Runtime hooks держат горячие моменты: Markdown graph reminder перед write, сбор
Markdown-правок после write и graph rollup на Stop.

## 6

> Мне надо чтобы ИИ понимал сам себя свои проблемы и всю систему и поэтому мог
> написать инструкции сам себе в проекте, чтобы улучшить использование скилов,
> понимал когда и в какой момент использовать скилы и как усилить их
> использование за счёт инструкций которые сам себе напишет и эти инструкции
> также должны сочетаться со всей остальной системой узнавания меня, моих задач
> и рабочих планов, которые сам ИИ поддерживает

### Текущие решения для самоулучшения системы

`1instruction-layer` решает формулировку и placement правила: какое поведение
должен увидеть будущий агент, какой language failure закрываем, где живёт
короткая инструкция и чем delivery доказывается. Он не копирует тела скилов в
инструкции и не пишет durable user truth вместо правильного owner-а.

`1folder-contract` держит системный контракт: ведут ли папочный граф, criteria,
hooks, runtime guardrails, review и root shims агента к `_ops/GOAL.md`.

`1skill-architect` чинит сами скилы: trigger surface, `description`,
body, references, scripts, `agents/openai.yaml`, validation и stop condition.
Для GPT-5.5 контракт должен быть outcome-first; старый process-heavy prompt
stack не переносится по инерции.

`1ia-audit` проверяет форму знания: правильный ли container, не размазан ли
owner truth, найдёт ли будущий агент нужный файл, не создаём ли мы новый
drift-point. `1md-navigator` даёт карту/поиск/overlaps, `1md-graph` даёт
обязательства frontmatter и blast-radius. Они не владеют смыслом файла.

`1obsidian` делает чтение и взаимодействие приятнее в Obsidian, но truth остаётся
в owner-файлах. `.base`, Meta Bind, callouts и links не должны становиться
второй правдой.

`brooks`, `smith`, `auditor`, `claude-mcp` и `gemini-mcp` дают внешний или
свежий взгляд, но Codex main context отвечает за синтез, решение и repair.

## Устаревшие Маршруты

- старые отдельные planning/task handles - заменены единым `1planning`.
- `1criteria-council` - удалён; generic fresh-context маршрут теперь
  `1fresh-eyes`, large closeout audit - `auditor`.
- `criteria-generator` и отдельный `1user-truth` - не текущая live-модель этого
  репозитория; устойчивые правила закрепляются только у правильного owner-а.
- `interview через 1obsidian` - устарело; structured intake ведёт
  `1interview-tool`, а `1obsidian` остаётся Obsidian UX-слоем.
- `1repo-shape` как отдельный live owner не используется; structural controls
  принадлежат `1folder-contract`.
- `1before-work` / `1before-write` не являются живыми установленными скилами;
  их прежний смысл распределён между локальным context/owner pass, owner checks,
  hooks и прямым evidence-closeout.
- `1md-graph` больше не владеет reading map: карту, heading index, semantic
  search и related reading держит `1md-navigator`.
- `INTERVIEW.md`, `LEARNINGS.md` и `projects/` - не live owner surfaces этого
  проекта.
