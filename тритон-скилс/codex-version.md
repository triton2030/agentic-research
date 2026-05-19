# Codex-версия

Снимок на 18 мая 2026. Это карта текущей Codex-системы, а не источник
рабочего поведения.

Если этот файл расходится с живой системой, выигрывают:

- `/Users/triton/.codex/AGENTS.md` - верхняя рамка Codex;
- `/Users/triton/.codex/skills/*/SKILL.md` - живые контракты локальных скилов;
- `/Users/triton/.codex/agents/*.toml` - нативные read-only агенты Codex;
- `/Users/triton/.codex/config.toml` - модель, features, plugins и hooks;
- plugin/system skill bodies - встроенные и плагинные навыки Codex;
- `README.md`, `_ops/GOAL.md`, `_ops/PROJECT-ROADMAP.md`,
  `_ops/criteria/*.md` - текущая правда этого репозитория.

Главная модель сейчас: один активный owner на момент работы. `1start-here`
восстанавливает намерение, локальную почву и выбирает маршрут; соседние скилы
остаются handoff-поверхностями, а не параллельными алгоритмами.

## Актуальный Контур

В глобальном конфиге Codex указан `gpt-5.5`; включены `multi_agent`,
`memories`, `hooks` и `goals`. Из плагинов включены GitHub, Vercel, Build Web
Apps, Browser и Chrome. Плагинные скилы не принадлежат этой папке: их надо
читать по live plugin contracts, когда они реально триггерятся.

Активные hooks:

- `SessionStart` - на `startup`, `resume`, `clear` загружает полный
  `/Users/triton/.codex/skills/1start-here/SKILL.md` как дополнительный
  контекст;
- `UserPromptSubmit` - даёт короткий якорь: не работать в вакууме, читать
  локальные инструкции и применимые `_ops/criteria/*.md`, если они могут
  изменить ответ;
- `Stop` - после чувствительных правок или 3+ изменённых файлов требует
  компактный `1work-review`; обычные маленькие правки не превращает в
  церемонию.

Hooks усиливают скилы, но не заменяют их. Старые pre-write идеи не считать
живым runtime, если их нет в текущем `config.toml`.

Локальные `1*`-скилы:

- `1start-here` - стартовый system-steward router: intent, SoT/owner/criteria,
  radius и один следующий owner;
- `1strategy` - выбор подхода до планирования: цель против метода, развилки,
  цена решений, ground check и handoff;
- `1strategy-docs` - форма и правки `README.md`, `_ops/GOAL.md`,
  `_ops/PROJECT-ROADMAP.md`: context, contract, current path без дублирования;
- `1planning` - рекурсивное планирование: L1 roadmap/current path, L2 task,
  L3 subtasks, archive/reconcile;
- `1user-truth` - durable user truth и `_ops/criteria/*.md`; пишет только из
  прямого пользовательского сигнала или утверждённой проектной правды;
- `1interview-tool` - временные intake-формы в `_ops/interviews/**`, когда
  после context triage осталось 4+ user-only неизвестных;
- `1assumption-audit` - ручной `ground-check` уже выбранного подхода: какие
  предпосылки должны быть true, что доказано, где blocker/assumption/revision;
- `1work-review` - пропорциональная финальная сверка: просьба, качество,
  evidence, applied criteria/instructions/radius; видимый отчёт короткий, если
  риск маленький;
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
- `smith` - критик trajectory/execution: L1 roadmap, L2 task, L3 evidence.

## 1

> Мне надо чтобы ИИ давал мне картинку как мы дойдём от 0 до готово, но ввиде
> очень краткого и понятного файла, чтобы я видел текущий подход к работе и
> понимал на сколько мы далеко или близко к цели. Но в тоже время чтобы этот
> файл был динамичный ведь цели меняются

### Текущие решения для динамичной карты

`1strategy` больше не пишет roadmap сам. Он выбирает подход: отделяет желание
от метода, показывает реальные развилки, цену решений, слабые предпосылки и
вариант "сделать меньше / отложить / не делать", если это защищает цель.

`1strategy-docs` держит стратегические поверхности чистыми: `README.md` -
короткий on-ramp, `_ops/GOAL.md` - главный scope-контракт, roadmap - current
path. Если меняется outcome, scope, NOT in scope, definition of done или stop
rules, это не обычная planning-правка.

`1planning` держит динамичную карту после выбранной стратегии:
`_ops/PROJECT-ROADMAP.md` как L1, task-файлы в `_ops/plans/**` как L2 и
подзадачи внутри task-файла как L3. В этом репозитории roadmap не обязан быть
стадийной дорожной картой: он может быть короткой рамкой текущего режима.

`1work-review`, `smith` и `auditor` проверяют не "красиво ли звучит", а
приблизила ли работа к цели, доказана ли готовность и не поехала ли траектория.

## 2

> Мне надо чтобы всё что я сказал во время любого обсуждения или решения, ИИ
> записывал информацию обо мне в нужный файл критериев, если такого нет то
> создал бы. Я не хочу одно и то же писать много раз с каждой новой сессии или
> при смене ИИ агента. Это одновременно и память обо мне и моих предпочтениях и
> одновременно критерии принятия.

### Текущие решения для критериев

`1user-truth` пишет устойчивую пользовательскую правду в `_ops/criteria/*.md`:
предпочтения, красные линии, цели, факты проекта, workflow corrections и
критерии качества. Правило нельзя додумывать: нужен прямой user signal или
явно утверждённая project truth.

Перед записью `1user-truth` делает semantic check по существующим criteria:
если смысл уже есть, это confirmation или merge, а не новый файл и не новая
строка. Если правило похоже на wording/placement инструкции, сначала route в
`1instruction-layer`; если на routing, hook, permission, system contract или
глобальный default — в `1folder-contract`.

`1interview-tool` включается только когда после чтения локального контекста
остаётся 4+ user-only неизвестных, batch decisions или per-item ответы. Он
строит временную форму в `_ops/interviews/**`; смысл потом возвращается
caller-скилу: durable truth в `1user-truth`, task scope в `1planning`, wording
правил в `1instruction-layer`, системный маршрут в `1folder-contract`.

`UserPromptSubmit` и root-инструкции доставляют критерии в момент работы, но не
пишут их за пользователя. Если подходящего критерия нет, правильный ход -
остановиться и получить user-backed truth, а не импровизировать criteria.

## 3

> Мне надо чтобы предже чем выбрать подход к работе ИИ предлагал разные
> варианты подхода к задачам, включая работу на главной дорожной картой, так и
> разными подходами внутри задач, чтобы мы шли к главной цели максимально
> эффективным и продуманым путём так чтобы мы ничего не сломали

### Текущие решения для выбора подхода

`1strategy` - главный владелец развилок. Он показывает только те варианты,
которые реально меняют cost, risk, scope, future constraint, reversibility или
owner route. Декоративные варианты не нужны; один сильный путь лучше трёх
псевдоальтернатив.

Проверка почвы теперь распределена:

- `1strategy` проверяет ключевые предпосылки до заморозки подхода;
- `1assumption-audit` делает ручной глубокий `ground-check` выбранного подхода;
- `1planning` сохраняет blocker/assumption/order там, где это нужно для
  исполнения;
- `1work-review` проверяет, применялись ли эти criteria и assumptions в работе.

`1step-back` нужен, когда может быть неверна сама рамка мышления. `1fresh-eyes`
нужен, когда риск в inherited context: поддакивание, frame lock,
auto-close, пропущенная связь. `1findings` удерживает подтверждённые актуальные
проблемы в `_ops/findings/**`, пока стратегия не решит, что с ними делать.

## 4

> Мне надо чтобы после того как мы обсудили подходы к работе, обсудили цель и
> коротко как мы до неё дойдём, мы писали связанные файлы, где дорожная карта
> это первый уровень планирования, имя стадий это название папок а сами файлы
> уже второй уровень планирования внутри стадий а подзадачи написанные внутри
> уже третий

### Текущие решения для уровней планирования

Живой owner один: `1planning`. `1roadmap` и `1tasks` больше не нужны.

`1strategy-docs` держит границу между стратегическими документами: `GOAL` не
становится roadmap, `README` не становится task tracker, roadmap не дублирует
scope-контракт.

`1planning` держит:

- L1 - `_ops/PROJECT-ROADMAP.md`: current path, режим или стадия;
- L2 - `_ops/plans/**/task-*.md`: только активная сложная работа по явному
  запросу или когда без task-файла scope станет мутным;
- L3 - подзадачи внутри task-файла.

`_ops/plans/` и каждая вложенная planning-папка имеют `_archive/`. Если L1
меняется, L2/L3 сначала reconcile/archive, а не продолжают управлять работой по
инерции. Если меняется форма задач, папок, owner truth или retrieval path,
`1planning` передаёт IA-вопрос в `1ia-audit`.

## 5

> Мне надо чтобы ИИ активно читал планы, дорожну карту, выполнял задачи следуя
> критериям принятия, чтобы он точно понимал в любой момент что мы делаем, на
> какой мы стадии и зачем и каким образом что то делать. Чтобы он мог почти
> автономно делать большие цепи задач и при этом был бы максимально ментально
> синхронизирован со мной.

### Текущие решения для исполнения

`1start-here` запускает проектную работу: восстанавливает intent, SoT/owner,
criteria, RAID, dependency radius и выбирает один активный owner. Он не делает
ритуал из простого ответа, но не даёт отвечать из вакуума, когда локальная
система может изменить решение.

Перед исполнением:

- `1strategy` держит approach/scope checkpoint;
- `1planning` держит task prerequisites и active frontier;
- локальные owner/criteria checks перед substantive write проверяют, какой
  файл владеет смыслом и какие criteria должны применяться;
- `1md-navigator` выбирает, что читать в большом Markdown-корпусе;
- `1md-graph` проверяет graph/frontmatter/blast-radius known targets;
- `1cli-tools` даёт bounded CLI evidence: ссылки, stale refs, deps, security,
  cleanup, package/code/docs facts.

`1work-review` закрывает работу через evidence. Он проверяет, выполнена ли
исходная просьба, насколько качественно, какие сомнения остались и были ли
criteria/instructions/radius реально применены во время работы. Маленькие
успешные правки закрываются коротко; большой audit можно отдать `auditor`.

Runtime hooks держат горячие моменты: старт сессии через `1start-here`, новый
prompt через лёгкий criteria/local-instructions anchor, финал после
чувствительных или широких правок через `1work-review`.

## 6

> Мне надо чтобы ИИ понимал сам себя свои проблемы и всю систему и поэтому мог
> написать инструкции сам себе в проекте, чтобы улучшить использование скилов,
> понимал когда и в какой момент использовать скилы и как усилить их
> использование за счёт инструкций которые сам себе напишет и эти инструкции
> также должны сочетаться, со всей остальной системой узнавания меня, моих
> задачах, моей дорожной карты которую сам ИИ и пишет

### Текущие решения для самоулучшения системы

`1instruction-layer` решает формулировку и placement правила: какое поведение
должен увидеть будущий агент, какой language failure закрываем, где живёт
короткая инструкция и чем delivery доказывается. Он не копирует тела скилов в
инструкции и не пишет criteria вместо `1user-truth`.

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

- `1roadmap` и `1tasks` - заменены единым `1planning`.
- `1criteria-council` - удалён; generic fresh-context маршрут теперь
  `1fresh-eyes`, large closeout audit - `auditor`.
- `criteria-generator` - не текущая модель этого репозитория; устойчивые
  критерии живут в `_ops/criteria/*.md` через `1user-truth`.
- `interview через 1obsidian` - устарело; structured intake ведёт
  `1interview-tool`, а `1obsidian` остаётся Obsidian UX-слоем.
- `1repo-shape` как отдельный live owner не используется; structural controls
  принадлежат `1folder-contract`.
- `1before-work` / `1before-write` не являются живыми установленными скилами;
  их прежний смысл распределён между `1start-here`, owner/criteria checks,
  hooks и `1work-review`.
- `1md-graph` больше не владеет reading map: карту, heading index, semantic
  search и related reading держит `1md-navigator`.
- `INTERVIEW.md`, `LEARNINGS.md` и `projects/` - не live owner surfaces этого
  проекта.
