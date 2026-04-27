# Skill Architecture Thinking

Снимок на 25 апреля 2026. Статус: full Claude Code rollout выполнен для marketplace `my-skills`; native Codex parity также установлен через 14 split skills.

Это не tested wisdom — это **рабочая позиция** про то, как должна быть устроена skill-поверхность как control surface для работы с ИИ. Когда устаканится на нескольких сессиях — поднимется в `wisdom-skills-plugins.md` или в `guides/perfect-skills.md`. Пока — здесь.

## Откуда Появилось

Стартовая точка: audit восьми установленных скилов в `my-skills` плагине. Половина undertriggers («не запускается даже когда полезен»), половина overcrowded (один большой скил пытается покрыть 5 разных триггерных поверхностей). Оба сбоя — следствие одной ошибки: скилы спроектированы как «профессии» (большие компетенции), а не как **точечные инструкции в момент действия**.

Anthropic в собственном `skill-creator` пишет дословно: *«Currently Claude has a tendency to undertrigger skills — to not use them when they'd be useful. To combat this, please make the skill descriptions a little bit pushy.»* Описание должно быть напористее, чем интуитивно кажется правильным. Одна часть фикса — переписать description-ы. Другая, более глубокая — пересмотреть **что вообще такое скил**.

## Три Слоя Контроля Поведения ИИ-Агента

ИИ-агент, работающий в течение длинной сессии, контролируется в трёх слоях с разной природой:

**1. Корневые инструкции (root layer).** `AGENTS.md`, `CLAUDE.md`, project-level CLAUDE.md, MEMORY.md. Загружаются один раз в начале сессии. Дают **базовый климат**: какой здесь стек, какие правила вечны, какие anti-patterns. Сильны на старте, **декаются** по ходу — модель забывает, разбавляет, расставляет приоритеты заново. К десятому сообщению root становится фоном.

**2. Скилы (skill layer).** Динамически вызываемые специализированные блоки. Сильны тем, что **доставляются в момент необходимости** через description-matching. Слабее хуков — не гарантированы, могут пропуститься. Сильнее корневых — потому что не декаются (грузятся заново при каждом срабатывании).

**3. Хуки (hook layer).** Pre/post tool-use инжекции, валидаторы, blocking gates. **Гарантированы** — выполняются вне воли модели. Самый сильный слой контроля. Но негибкие — каждый хук стоит конфигурации, нагружает все вызовы инструмента, и плохо масштабируется до 50 правил.

Skill — золотая середина: **сильнее корневых, гибче хуков**.

## Главный Тезис

Скил надо проектировать **не как компетенцию, а как момент**. Описание скила должно отвечать на вопрос **«какую фразу/действие пользователя/состояние я ловлю»**, а не **«что я умею».**

Из этого следует: малых скилов с узкими триггерами — много; больших скилов с широкими триггерами — мало. Дублирование инструкций между скилами — **фича**, а не bug: каждый раз, когда скил срабатывает, он **фрешит** правило в контекст модели. Это и есть его смысл — побороть decay корневых инструкций.

## Два Класса Скилов

### Moment-skills (контекстные инжекторы)

Триггерятся на **тип действия или фразу пользователя в конкретный момент**. Описание = «прямо сейчас ты делаешь X — вот что вспомнить». Должны быть лёгкими: 3-5 строк receipt, никаких файлов на запись, никакого interview, никакого пересмотра стратегии.

Примеры:
- `before-work` — перед нетривиальной правкой: освежи рамку, прочитай контракт.
- `work-review` — после правки, перед закрытием хода: проверь evidence, отметь Подшаг.
- `preference-sync` — на «хочу/предпочитаю»: молча захвати в INTERVIEW.md.
- `contradiction-hold` — на запрос, противоречащий stored предпочтению: блок диалогом.
- `plan-drift-watch` — git/chat показывают, что фаза фактически закрыта: синкни стратегию.

### Topic-skills (узкие owner-skills по контракту)

Триггерятся на **тематический запрос и владеют контрактом файла или артефакта**. Большие, тяжёлые, могут вести многостраничные references. Запускаются реже, чем moment-skills.

Примеры:
- `task-contract` — owner task-файла: Цель / Подшаги / Критерии приёмки.
- `project-roadmap` — owner PROJECT-ROADMAP: direction, Goal, roadmap.
- `ops-sync` — механический sync `_ops/`: phase folders, sync-ops.sh.
- `skill-architect` — design новых скилов/агентов.
- `instruction-layer` — где живёт правило: AGENTS/CLAUDE, routing, ownership.
- `repo-shape` — папки, файлы, hooks, permissions, settings.json.

## Принцип Резки

Делить скилы надо **по триггерной поверхности**, не по капабилити.

- Две функции, срабатывающие на одни и те же фразы пользователя → один скил, даже если внутри делают разное.
- Две функции на разных триггерах → разные скилы, даже если делят 80% кода/референсов.

Иначе: у одного скила description пытается перечислить все триггеры, размывается, и Claude не знает, на что именно реагировать. Это была болезнь retired монолитов.

## Дублирование — Фича

`before-work` пересказывает кусок инструкции `task-contract` («открой task-файл, прочитай Цель/Must-not»). `preference-sync` пересказывает кусок `project-roadmap` («молча в INTERVIEW.md»). `contradiction-hold` пересказывает Hard Block оттуда же.

Это **не bloat** — это **resilience**:

- Если root-инструкции не удержали preference signal — есть свежая инжекция через `preference-sync`.
- Если task context не всплыл на быстрой правке — есть свежая инжекция через `before-work`.
- Если противоречие возникло в момент быстрой задачи — `contradiction-hold` ловит семантический сигнал до молчаливого override.

Дубль — это резерв надёжности. У одного скила вероятность срабатывания P. У двух independent скилов на тот же сигнал — 1-(1-P)². При P=0.7 один даёт 70%, два дают 91%, три — 97%.

Это рассуждение работает **только при разной триггерной поверхности**: если оба скила триггерятся на одну и ту же фразу — это не дубль-резерв, а дубль-конфликт.

## Cargo-Cult Guard — Не Строй По Памяти

Когда строится новый скил/агент/файл/модуль, особенно по упоминанию в `MEMORY.md`/`AGENTS.md`/CLAUDE.md/старой стратегии — **сначала verify against reality**:

1. Существует ли уже? Grep / find / ls по имени и алиасам.
2. Якоря, на которые ссылается описание — существуют? («Solomon — часть critic-family с Brooks и Smith» → Brooks и Smith реально есть как агенты?)
3. Какой layer? (Если паттерн живёт как агенты в `~/.claude/agents/`, новый член семьи — тоже агент, не скил. Не смешивать слои на основе «по мотивам».)
4. Зачем именно сейчас? Что новый артефакт ловит, чего существующие не ловят? Если ответ «потому что упомянут в памяти» — это не scope, это inertia.

Память и инструкционный слой содержат **аспирации, упоминания будущих сущностей, устаревшие ссылки**. Строить по упоминанию без проверки = cargo cult. Особенно опасно для skill / agent / hook слоёв — там разная runtime-механика, аналогия по описанию даёт неправильную форму.

Это правило вшито в `before-work` SKILL.md как явный gate перед созданием артефактов.

## Anthropic-Style Description — Десять Признаков

На корпусе из 18 официальных Anthropic скилов:

1. Императив `Use this skill **whenever**` — сильнее, чем `Use when`.
2. Закавыченные пользовательские фразы (на языке пользователя) — лексические якоря работают надёжнее семантики.
3. Прямые упоминания файловых расширений / контекстов / имён инструментов — те же якоря.
4. Триггеры через симптом, не через жаргон («опять забыла», «как сделать автоматически» — а не «recurring failure mode»).
5. Конкретные `Do NOT use for...` — только для реально смежных скилов, не для очевидно нерелевантного.
6. «Even if» / «regardless of» / «even casually» — закрывают рассуждения модели «возможно, тут не нужен скил, потому что...»
7. Объяснение мотивации внутри description («never copying existing artists' work to avoid copyright violations») — guard rail прямо в трегере.
8. Капс TRIGGER / SKIP блоки для сложной дизамбигуации (`claude-api`).
9. Типичная длина: 200-450 символов; 600+ только если есть реальная конкуренция со смежным скилом.
10. Эмпирическая проверка: 20 запросов × 3 прогона — `should-trigger` должны быть разнообразны по фразировке, `should-not-trigger` — это **near-misses** (наивный keyword match сработал бы, но семантически нужно другое).

## Двухступенчатый Фильтр — Скрытая Механика

Anthropic в `skill-creator`: *«Claude only consults skills for tasks it can't easily handle on its own — simple, one-step queries like "read this PDF" may not trigger a skill even if the description matches perfectly.»*

То есть Claude сначала решает **«нужен ли мне вообще скил»**, потом сопоставляет описания. Это значит, что для простых на вид задач скил пропустится, даже если description идеален. Описание должно сигнализировать **«здесь есть нетривиальная процедура, не пытайся справиться сам»**.

Для moment-skill это значит: явно говорить, что без инжекции модель забудет правило. Например: «Skipping is how the rule decays» / «Default-on for any task-level work, even single-line edits anchored in active task».

## Жизнеспособный Финальный Ландшафт (Snapshot)

Текущая Claude Code цель реализована: live marketplace состоит из 18 skills — 14 landscape skills и 4 unchanged utility/audit skills.

### Moment-skills (6)

| Скил | Триггер | Owner of? |
|---|---|---|
| `before-work` | императивные глаголы старта работы, перед Edit/Write | nothing (read-only) |
| `before-write` | прямо перед Edit/Write на substantive content | nothing |
| `work-review` | после действия, перед закрытием хода: «готово», «проверь», «закрыли» | nothing |
| `preference-sync` | «хочу / предпочитаю / люблю / не хочу» | INTERVIEW.md update only |
| `contradiction-hold` | новый запрос противоречит stored INTERVIEW/PROJECT-ROADMAP | nothing (dialogue mode) |
| `plan-drift-watch` | git/chat/closed task показывают drift | nothing (signal-only) |

### Topic-skills (8)

Из task lifecycle family:
- `task-contract` — owner task-файла (сжатый, без active-context-guard и без двух режимов)
- `strategy-trace` — read-only audit артефакта против Goal/Stage
- `pulse-check` — dialog-time memory probe

Из strategy family:
- `project-roadmap` — direction, Goal, roadmap, planning
- `ops-sync` — механический sync `_ops/`, phase folders, sync-ops.sh

Из system/control-surface family:
- `skill-architect` — design скилов/агентов
- `instruction-layer` — где живёт правило: AGENTS/CLAUDE, routing, ownership
- `repo-shape` — папки, файлы, hooks, permissions, settings.json

### Без изменений (4)

`step-back`, `screenshot-design`, `playwright-skill`, `pitch-coherence-audit`.

### Удалено (1)

`retired LLM wisdom skill` — мёртвый скил, undertriggered настолько, что никогда не срабатывал; контент устарел.

### Retired handles

Три больших монолита и удалённый LLM-oriented skill больше не являются live Claude Code handles. Их поведение разложено по landscape выше.

## Pipeline Выполнения

Фактический rollout выполнен одним проходом по пользовательскому решению full rollout с post-publication validation:

1. Удалить retired LLM-oriented skill — выполнено.
2. Прототип `before-work` — выполнено.
3. Остальные 5 moment-skills — выполнено.
4. Task lifecycle split: `task-contract`, `strategy-trace`, `pulse-check` — выполнено.
5. Strategy split: `project-roadmap`, `preference-sync`, `ops-sync`, `plan-drift-watch`, `contradiction-hold` — выполнено.
6. Control-surface split: `skill-architect`, `instruction-layer`, `repo-shape` — выполнено.
7. Финальный inventory + bump версии + sync `marketplace.json` / `plugin.json` — выполнено.
8. Post-publication validation — следующий operational step.

Ранее планировался prototype checkpoint после `before-work`; пользователь выбрал full rollout сразу, поэтому validation стала post-publication smoke test.

## Что Это Меняет Для Работы С ИИ В Принципе

Это не только про скилы. Это про то, **как вообще собирать control surface** для долгой сессии:

1. **Корневые инструкции — фундамент, не оперативный слой.** В них только то, что должно быть верно весь session. Конкретные правила выполнения уходят в скилы.
2. **Скилы — основной operational layer.** Их должно быть много, узких, моментных. Не «эксперт по X», а «инжекция правила R при сигнале S».
3. **Хуки — для non-negotiable правил.** Если правило в скиле всё равно пропускается, и пропуск стоит дорого — поднимай в хук. Цена: rigidity, конфигурация, шум на не-целевых вызовах.
4. **Память — context, не buildable spec.** В ней живут аспирации и устаревшие ссылки. Перед реализацией по упоминанию — verify.

В этой системе модель проходит длинную сессию, не теряя правил, потому что каждый момент действия имеет **свежую инжекцию** соответствующего правила. Не «model должен помнить» — а «system гарантирует, что модель напомнят прямо перед действием».

## Открытые Вопросы

- **Сколько moment-skills — оптимум?** Стартуем с 6. Может быть, 3 (before-work, work-review, preference-sync) — достаточно. Может, нужно 9 (добавить role-donning-watch, opinionated-mode-watch, refs-applied-check).
- **Длина description.** Текущий `before-work` — ~700 chars (с правкой пользователя). Anthropic-медиана — 324. Для moment-skill с широким захватом большая длина нужна; но грань с overcrowding не определена.
- **Дубли — где предел?** Если три скила пересказывают одно правило, это резерв или путаница? Эмпирика покажет.
- **Источник truth для скилов в `my-skills`.** Сейчас marketplace = source-of-truth, repo `projects/meta/*--skill-claude-code/` = working draft, sync ручной. На 14 скилов это становится тяжёлым. Нужен sync-script или другая схема.
- **Source sync.** Теперь split landscape живёт в двух runtime-формах: Claude Code marketplace и native Codex skills. Нужен sync-script или другой explicit release loop, чтобы 14 пар не расходились.

## Связь С Другими Документами

- `_ops/plans/phase-01-стабилизировать-живую-форму-репы/task-05-skill-landscape-decomposition.md` — executable task-file под эту стратегию.
- `knowledge/wisdom-skills-plugins.md` — общая wisdom про packaging.
- `knowledge/guides/perfect-skills.md` — устойчивые правила написания скилов (требует обновления под moment vs topic split).
- `knowledge/practical-guides/claude-code-skills.md` — practical guide.
- Прототип: `/Users/triton/.claude/marketplaces/my-skills/skills/before-work/SKILL.md`.

## Условия Promotion в Tested Wisdom

Поднимать в `wisdom-skills-plugins.md` (или в собственный `wisdom-skill-architecture.md`) можно когда:

1. ≥3 moment-skills доказали reliable triggering на реальных сессиях (не один прототип).
2. Дубли между скилами проверены: либо реально дают резерв (видно в логах), либо вызывают конфликт (тогда тезис меняется).
3. Pipeline до шага 8 пройден без переписывания принципа резки.
4. Появилась эмпирика: сколько скилов в горячей зоне — оптимум.

До этого — позиция, не wisdom.
