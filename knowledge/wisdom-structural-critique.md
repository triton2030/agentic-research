# Wisdom — Structural Critique

Снимок на 25 апреля 2026.

Единый источник для оптики структурной критики, распределённой по 9 скилам (`1skill-architect`, `instruction-layer`, `repo-shape`, `project-roadmap`, `task-contract`, `plan-drift-watch`, `strategy-trace`, `1work-review`, `pulse-check`). Скилы несут адаптацию под свою trigger surface; этот файл держит **полный словарь и discipline**, чтобы избежать drift между скилами.

Дополнительно — поверхность для двух subagent'ов (`brooks`, `smith`) как conditional fallback, когда нужен независимый, контекст-свободный взгляд.

## Откуда Оптика

Три книги, прочитанные и прожитые:

- **John Ousterhout, «A Philosophy of Software Design»** — deep modules vs shallow, complexity как главный враг, минимизация cognitive load, interface ≪ implementation.
- **Frederick Brooks, «The Mythical Man-Month»** — accidental vs essential complexity, conceptual integrity как то, что теряется первым при росте, the tar pit.
- **Michael Feathers, «Working Effectively with Legacy Code»** — швы (seams) в коде, характеризационные тесты, работа с тем, что нельзя переписать с нуля.

Это сформированная оптика, не чек-лист. Не вспоминать определения по таблице — видеть shallow-обёртку через две секунды чтения и знать, что в ней не так.

## Discipline Rules (универсально для всех 9 скилов)

1. **Назвать проблему, не чинить.** Output — диагноз. Brooks даёт structural
   recommendation к finding; Smith даёт scoped recommendation к trajectory
   finding. Исполнение и переписывание остаются у отдельного owner.
2. **Молчание при сомнении лучше слабого замечания.** Если не уверен — не пиши.
3. **Пустой review — валидный результат.** Не выдавливать findings ради presence.
4. **Не комментировать стиль/именование/длину функций**, пока не решены вопросы структуры. Структура первой.
5. **Ясность через 6 месяцев > одобрение сейчас.** Спрашивай, как это будет выглядеть через два года и через пять редакторов.
6. **Спор двигает findings, не оптику.** Когда автор защищается — спрашивай, какое допущение читаешь неправильно, проверяй, возвращайся к диагнозу либо снимай его.

## Stop-Rule (универсально)

> Если не можешь сформулировать центральную модель / trigger surface / план-цель того, что смотришь — это **первая и главная находка**. Сообщи об этом и остановись. Не сглаживай.

Этот rule одинаков во всех 9 скилах. Дублирование намеренное (фрешность discipline через каждое срабатывание).

## Brooks-Vocabulary (структура артефакта)

Применяется к **код**, **скилам**, **агентам**, **инструкциям**, **папкам/конфигам** — везде, где есть структура, имеющая центральную модель.
Brooks не останавливается на диагнозе: каждая находка должна назвать
архитектурную рекомендацию, то есть какой shape системы лучше сохранит
central model, deep modules и conceptual integrity.

### Три категории

1. **Central model violation.** Артефакт нарушает свой организующий принцип. Признак: отдельные правки кажутся локально разумными, но в сумме разъедают модель.
2. **Shallow abstraction** (Ousterhout). Стоимость интерфейса ≈ или > скрываемой функциональности. Признак: чтение интерфейса не экономит чтение реализации.
3. **Red flags** (см. ниже).

### Red Flags Brooks-словаря

- **Pass-through method** — функция, которая просто пробрасывает аргументы дальше без преобразования.
- **Interface = implementation** — public API повторяет внутреннюю структуру 1:1; нет инкапсуляции.
- **Configuration explosion** — N настроек, чтобы покрыть M частных случаев, без объединяющего абстрактного.
- **Temporal decomposition** — модули разбиты по времени выполнения («сначала X, потом Y»), а не по ответственности. Меняешь шаг — трогаешь несколько модулей.
- **Information leakage** — деталь реализации модуля A знает модуль B; изменение A ломает B без причины.
- **Shallow utility class** — класс «UtilHelpers» без когезии; все его методы ничего не знают друг о друге.
- **Broken window** — один шаткий артефакт → норма для остальных; качество просаживается ниже линии.
- **Cargo cult** — паттерн скопирован «по аналогии» без понимания, что он решал.
- **Dependency surprise** — артефакт молча зависит от другого; вызывающий не знает.
- **New-in-legacy blindness** (Feathers) — новое добавляется без понимания existing seams; растут наслоения вместо интеграции.
- **Hallucinated API** (LLM-патология) — вызов функции/метода/параметра, которого не существует или существует с другой сигнатурой.
- **Plausibly incorrect** — код, который читается как правильный, но семантически делает не то; самый коварный класс LLM-ошибок.

### Адаптация под domain (для скилов-носителей)

Каждый принимающий скил адаптирует 2-3 категории под свой trigger surface.

**`1skill-architect`:**
- Central model = trigger surface (что скил ловит как пользовательский момент)
- Shallow = description, который перечисляет capabilities вместо моментов; SKILL.md тело, дублирующее description
- Red flags: skill configuration explosion (N пересекающихся скилов), interface=implementation (description ≈ body paraphrase), dependency surprise (скил тихо требует другой), broken-window, cargo-cult creation (по упоминанию в памяти без verify)

**`instruction-layer`:**
- Central model = climate of root layer (eternal rules) vs operational (decay-prone)
- Shallow = инструкция, которая повторяет другую без добавления specificity
- Red flags: configuration explosion правил, dependency surprise (правило молча требует другое), broken window (один weak rule → норма), new-in-legacy blindness (новое правило без проверки existing layers)

**`repo-shape`:**
- Central model = layered ownership репо (что где живёт, кому принадлежит)
- Shallow = папка, которая просто группирует без contract'а
- Red flags: configuration explosion в `settings.json`, hook pass-through (вызывает один tool без преобразования), folder без owner, new-in-legacy

**`strategy-trace`** (Brooks side, артефакт-структура):
- Central model = служит ли артефакт Goal/активному Stage
- Red flags: vague boundary (артефакт «как бы» служит), phantom prerequisite (опирается на удалённый Stage)

**`1work-review`** (light) и **`pulse-check`** (light):
- Только universal stop-rule — «не могу назвать что не так = это и есть находка».

## Smith-Vocabulary (траектория выполнения)

Применяется к **трём слоям плана**: L1 project roadmap / strategy,
L2 task-файлы и phase tasks, L3 Подшаги / done evidence / verification.
Smith также держит бывшую Bob-оптику: метод не должен подменять цель, а
локально удобная задача не должна ломать будущую траекторию проекта. Как и
Brooks, Smith может давать рекомендации, но по trajectory scope: как лучше
сформулировать задачу, разбить её, проверить done state или выбрать способ
выполнения.

### Категории

1. **Strategy mismatch** — L2/L3 работа не служит L1 trajectory.
2. **Method as goal** — способ, артефакт или процесс подменил исходный эффект.
3. **One-way door** — локальный способ создаёт будущую дорогую связку.
4. **Cheaper probe missing** — перед дорогим ходом не сделан маленький reversible check.
5. **Best-practice mismatch** — формулировка, разбиение или исполнение задачи
   нарушает релевантную доменную практику: programming, frontend, business,
   prompts, skills, instructions, research или другую выбранную линзу.
6. **Missing intermediate** — между шагом A и шагом C нет необходимого B.
7. **Phantom prerequisite** — шаг ссылается на «уже сделано», чего на самом деле нет / удалили / не доделали.
8. **Vague boundary** — конец шага не определён testable-критерием; «closeout» субъективен.
9. **Hidden coupling** — два «независимых» шага на самом деле зависят; правка одного ломает другой без видимой причины.
10. **Done not evidenced** — задача объявлена закрытой без evidence, совпадающего со scope.
11. **Future trajectory risk** — локально выполненная задача ухудшает следующий Stage.

### Адаптация под domain

**`project-roadmap`:**
- Missing intermediate Stage между «обозначенный» и «заявленный»
- Phantom prerequisite (Stage требует исчезнувшее)
- Vague boundary (Stage без testable «done when»)

**`task-contract`:**
- Hidden coupling между Must items
- Vague boundary Подшага (нет testable end)
- Phantom prerequisite (ссылка на удалённое Anchored-in)

**`plan-drift-watch`:**
- Phantom prerequisite (referenced Stage gone after pересборки плана)
- Hidden coupling (drift в одном Step тихо ломает другой)

**`strategy-trace`** (Smith side, артефакт-в-плане):
- Vague boundary (артефакт служит Goal частично)
- Phantom prerequisite (опирается на удалённое)

## Subagent Fallback — Когда Поднимать

Конкретные пороги, чтобы fallback не превратился в дефолт:

| Когда | Поднять | Причина |
|---|---|---|
| Сложный артефакт + чувство «что-то не так но не могу назвать» | `brooks` | independent perspective, контекст-свободный |
| Три слоя плана расходятся: roadmap -> task -> subtasks/evidence | `smith` | нужен внешний trajectory/execution critic |
| План/последовательность с 5+ Подшагами с handoffs между ними | `smith` | швы тяжело видеть из главного потока |
| Нужно проверить несколько независимых task/subtask surfaces | parallel `smith` instances | каждый Smith получает disjoint scope, synthesis остаётся в main context |
| Cross-cutting concern, нужно проверить consistency между N артефактами | `brooks` или `smith` по доминанте | роевая безопасность, можно звать параллельно |
| Перед критическим commit (instruction layer, hook-script) | `brooks` | last-line-of-defense на структурную ошибку |

**Никогда:**
- На тривиальной правке (typo, переименование) — пустые findings, шум.
- В качестве required gate в скиле — оба агента **conditional**, не блокирующие.
- Без чёткого вопроса агенту — Brooks/Smith работают по специфическому промпту, не «посмотри так».

## Связь Со Скилами

| Скил | Vocab | Subagent fallback |
|---|---|---|
| `1skill-architect` | Brooks (full-domain adapted) | `brooks` (primary) |
| `instruction-layer` | Brooks-light | `brooks` (available) |
| `repo-shape` | Brooks-light | `brooks` (available) |
| `project-roadmap` | Smith (full-domain adapted) | `smith` (primary) |
| `task-contract` | Smith-light | `smith` (available) |
| `plan-drift-watch` | Smith-light | `smith` (available) |
| `strategy-trace` | Brooks+Smith-light | оба available |
| `1work-review` | stop-rule only | оба manually invokable |
| `pulse-check` | stop-rule only | — |

## Условия Promotion в Tested Wisdom

Поднимать в `wisdom-skills-plugins.md` или собственный `wisdom-*` после:

1. ≥3 скила реально использовали свои Brooks/Smith категории на реальных задачах за месяц.
2. Subagent fallback вызывался не чаще, чем 1 раз в 5-10 дней (если чаще — паттерн расходится; если никогда — fallback не нужен, удалить).
3. Не было случая, когда дубликация vocab между скилами вызвала путаницу/конфликт (а не резерв надёжности).

До этого — позиция, не wisdom.
