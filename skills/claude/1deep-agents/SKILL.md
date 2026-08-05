---
name: 1deep-agents
description: >
  Явный запрос `$1deep-agents`, «глубоких агентов» или трёх
  framework-разборов — вызови skill: иначе один контекст смешает методы и
  подделает trace. Запусти минимум трёх history-isolated,
  prompt-constrained advisory субагентов, дай каждому ровно один релевантный
  cognitive framework, потребуй наблюдаемую трассу каждого шага без private
  chain-of-thought и синтезируй все streams без голосования. Не для реализации,
  обычного review или question-only экспертов.
---

# Глубокие Агенты

## Product Job

В момент, когда одна важная задача заслуживает нескольких настоящих способов
мышления, получить минимум три изолированных framework-trace и один
decision-ready synthesis. Каждый субагент остаётся когнитивным advisor-ом:
применяет одну методологию к одному task packet, делает публичное применение
каждого её шага аудируемым и не выполняет саму задачу.

Продукт — не три мнения и не длинный ответ. Продукт — наблюдаемое различие
между тремя cognitive operations: что каждая заметила, как преобразовала
представление задачи, где изменила вывод и какой gap оставила владельцу решения.

## Authority И Non-Composition

Этот skill владеет только framework-trace product.

- Запрос на named native critic, auditor или scout принадлежит `1fresh-eyes`:
  его native output не втискивается в trace schema. Если нужны оба продукта,
  запускай их отдельными фазами.
- User-owned background tasks принадлежат отдельной runtime surface; same-thread
  framework-субагенты не подменяют их lifecycle. Точный seam указан в runtime
  adapter.
- При смешанном буквальном запросе раздели фазы либо вынеси один действительно
  material product choice. Не заменяй одну orchestration surface другой молча.

## Почему Команды «Подумай Тремя Frameworks» Недостаточно

Естественный shortcut одного контекста — сначала сформировать привычный ответ,
затем подобрать к его абзацам названия методологий. Frameworks смешиваются,
один и тот же вывод повторяется разными словами, а гладкое объяснение ошибочно
принимается за доказательство приватной последовательности мышления. Поздний
synthesis уже не может восстановить независимость или пропущенную публичную
мыслительную операцию.

Минимальный comparator — один prompt: «примени три релевантных framework и
покажи их шаги». Он не закрывает три load-bearing случая:

- общий conversation prior уже выровнял исходные frames;
- один агент может незаметно переносить выводы между методологиями;
- перечисленные шаги не доказывают наблюдаемого преобразования на каждом шаге.

Механизм skill разрывает эту цепочку так:

```text
один raw task packet
→ три разные cognitive jobs
→ три clean streams, один framework на stream
→ framework declaration + observable step trace
→ acceptance каждого trace
→ публикация раздельных native outputs
→ synthesis расхождений без vote
```

## Контроллер Root-Агента

Root владеет task packet, выбором frameworks, ожиданием всех обязательных
streams, проверкой traces, публикацией и synthesis. Субагенты владеют только
применением назначенной методологии. Они не выбирают другую методологию, не
видят outputs друг друга и не получают право редактировать, планировать
исполнение или делегировать.

Перед spawn удерживай компактный controller:

```text
decision: какой вопрос должен разрешить owner/root
packet: raw request + факты + constraints + известные gaps
cognitive_work: какая domain-independent мыслительная работа реально нужна
lenses: минимум три разные cognitive jobs
frameworks: один named method на lens + operational step spine + topology
barrier: какие traces обязаны вернуться до synthesis
```

History isolation означает только свежую non-fork invocation, определённую
runtime adapter-ом; она не изолирует active instructions, tools или общий
filesystem. No-tools/no-write — prompt constraint, а не sandbox guarantee. Если
integrity materially важна, root фиксирует pre-state receipt и сравнивает
post-state; необъяснённый delta отклоняет run.

Если вопроса решения нет, а нужен lookup, обычная реализация, question-only
эксперты или проверка готового acceptance, не присваивай этой surface чужую
работу.

## 1. Собери Один Task Packet

Передай всем streams один и тот же self-contained packet:

- точные слова задачи или максимально raw excerpt;
- решение, stakes, scope и запреты;
- только факты/evidence, уже доступные root-у;
- названные неизвестности, которые нельзя превращать в факты;
- ожидаемый продукт: cognitive trace, не implementation artifact.

Не передавай собственный preferred answer, подозреваемую проблему, очередность
исследования или вывод другого агента. Clean означает новую non-fork invocation
без parent conversation и готового solution frame, а не отсутствие системных и
project instructions: называй эту границу честно.

## 2. Извлеки Cognitive Work И Выбери Минимум Три Frameworks

Не маршрутизируй по поверхностной теме задачи. Область говорит, **о чём**
задача, но не говорит, какая мыслительная работа должна произойти, чтобы её
разрешить. Сначала построй mechanism-level модель:

```text
raw task
→ actors, objects и требуемое изменение состояния
→ search, abstraction, representation, inference, simulation, choice,
  verification, uncertainty и feedback
→ место возможного cognitive failure
→ нужные преобразования или decision tests
→ distinct cognitive jobs
→ framework signatures
```

Модель достаточна, когда root может назвать для каждого будущего stream:

- какое представление, belief, causal model, option space или decision rule
  должно появиться либо измениться;
- какая операция вызывает этот переход и какой shortcut она предотвращает;
- какой публичный artifact покажет, что операция действительно произошла.

Ищи framework по структуре этой работы, а не по словарю или исходной профессии
метода. Cross-domain transfer нормален, если роли, отношения и все канонические
шаги framework-а содержательно отображаются на текущую задачу. До выбора
проверь mapping
`framework entity/operation → task entity/operation`. Если перенос требует
пропустить, переставить, объединить или изобрести шаг, это structural no-fit.
Креативность принадлежит диагнозу cognitive work и обнаружению неожиданного
structural fit; сама выбранная методология не адаптируется.

Только после этого используй
[`references/frameworks.md`](references/frameworks.md) как компактный recall и
contrast seed. Registry не задаёт множество разрешённых candidates, не даёт
приоритета перечисленным names и никогда не работает как whitelist.

Выбирай сначала cognitive work, затем job, затем framework. Примеры jobs ниже —
не ontology и не меню:

- reframe или decomposition;
- evidence, causality или belief challenge;
- systems, architecture или domain boundaries;
- options, decision или uncertainty;
- risk, failure или resilience;
- information organization или findability.

Жёсткие правила выбора:

1. Запусти минимум три framework-а; default — ровно три.
2. Главный критерий качества — situational fit и ожидаемая cognitive delta:
   framework должен заметно улучшать представление задачи, различающий probe
   или проверку решения. Каждый framework меняет отдельную operation; три
   near-duplicate метода не создают три lenses.
3. Для software, system, database, data или information-architecture задачи
   хотя бы один framework обязан быть domain-native. Общие mental models его не
   заменяют.
4. Если пользователь назвал framework, сохрани его. Недостающие до трёх lenses
   подбери по distinct job; явный structural no-fit покажи до запуска.
5. Framework вне registry — обычный best-fit выбор, а не исключение. Root обязан
   выбрать его, если он релевантнее перечисленных, даёт distinct move и имеет
   defensible best-practice lineage. Root восстанавливает полный established
   operational step spine и topology: `linear` или `iterative`; он не сочиняет
   task-specific variant. Branch alternatives могут быть публичным artifact
   внутри исходного шага, но не отдельной execution topology. Если lineage,
   порядок или обязательность шага неясны, либо пользователь просит exact
   branded/canonical procedure, сначала проверь первичный или официальный
   источник, назови version и не импровизируй методологию из красивого названия.
6. После выбора не сокращай, не переставляй, не гибридизируй и не «улучшай»
   framework. Под задачу отображаются только его сущности и входные данные;
   механизм, полный step spine, topology и completion condition сохраняются.
7. Добавь четвёртый или пятый stream только под отдельную consequential
   uncertainty, которую первые три jobs принципиально не видят. Больше агентов
   не является evidence само по себе.

До spawn покажи пользователю короткую selection table: `cognitive work →
framework → structural fit → почему он способен изменить решение`. Не публикуй
внутренний ranking dump.
Назначь шагам стабильные IDs `S1…Sn`; для iterative методов заранее обозначь
допустимые возвраты.

## 3. Запусти Clean Framework-Агентов

Перед launch прочитай matching subsection в
[`references/runtime-orchestration.md`](references/runtime-orchestration.md) и
используй native fresh-subagent primitive текущего runtime. Передай каждому
self-contained brief ниже, подставив один framework и только его step spine.
Запускай независимые streams параллельно, когда доступны slots; иначе
последовательно. Не используй named critic roles: их встроенный метод
конкурирует с назначенным framework.

Точная точка действия:

```text
Ты — history-isolated cognitive-method advisor. Ты не worker и не автор
implementation. Не вызывай tools, не читай и не редактируй файлы, не выполняй
решение, не строй delivery plan, не вызывай других агентов и не подменяй
назначенный framework соседним. Это behavioral constraint, не sandbox.
Работай только с TASK PACKET; отсутствующее evidence оставляй gap.

TASK PACKET
<одинаковый raw packet для всех streams>

ASSIGNED FRAMEWORK
Name: <один framework>
Diagnosed cognitive work: <одна distinct cognitive job>
Structural fit: <framework entities/relations → task entities/relations>
Topology: <linear | iterative>
Operational step spine:
S1. <step>
S2. <step>
...

REQUIRED OUTPUT
1. Назови framework, его цель, topology и повтори полный operational step spine
   до анализа. Затем покажи cross-domain mapping, не меняя методологию. Если
   mapping не позволяет содержательно пройти каждый исходный шаг, верни
   structural no-fit и остановись: не создавай task-specific variant. Не
   называй step spine canonical без source-grounding.
2. Адресуй каждый declared step согласно topology. Для loop покажи повторный
   step ID и observable delta между проходами. Для каждого покажи:
   - Task-local input: факты, наблюдения или предыдущий результат шага;
   - Cognitive operation shown: наблюдаемое преобразование, различение, карта,
     альтернатива, причинная связь или probe — не скрытый внутренний монолог;
   - Step result: что стало известно или изменилось;
   - Evidence/gap: на что опирается результат и что остаётся неизвестным;
   - Handoff: что именно переходит в следующий шаг.
3. Дай Framework-native conclusion: только decision-relevant выводы этого
   lens, без реализации задачи и без смешивания других methodologies.
4. Заверши Trace coverage index: step ID → exact heading/address → public
   artifact type → grounding `fact|inference|gap`. Это адреса для root
   validation, а не твой self-grade `pass|fail`.
5. Не раскрывай private chain-of-thought или token-level monologue. Покажи
   проверяемые intermediate representations и decision-relevant reasoning
   artifacts, достаточные для аудита применения метода.
```

Нельзя ослаблять этот brief до «think step by step». Название framework,
operational spine, topology и trace fields находятся рядом со spawn именно
потому, что поздний checklist не исправляет уже смешанный stream.

Accepted trace доказывает только coverage и связность публичного method
artifact: в ответе видны task-specific операции и переходы. Он не доказывает
фактическую private chain-of-thought, истинность выводов или причинную роль
каждого скрытого inference; skill таких claims не делает.

## 4. Проверь Каждый Trace До Synthesis

Trace принимается, только если одновременно верно:

- объявлены один framework, topology и весь operational step spine со
  стабильными IDs;
- cognitive work и structural mapping видимы, а все исходные шаги применимы
  без изменения методологии;
- каждый declared step адресован согласно topology; повторные проходы
  показывают IDs и task-specific deltas;
- у каждого шага есть task-specific observable transformation, а не generic
  пересказ учебника или self-report;
- следующий шаг использует видимый результат предыдущего;
- факты, inference и gaps различимы;
- нет второго framework, implementation work, файловых правок или nested
  delegation;
- conclusion следует из trace и остаётся внутри lens authority;
- Trace coverage index адресует реальный текст ответа; root проверил coverage,
  dependency между шагами и grounding, а не принял self-attestation.

Если stream нарушил контракт, сначала классифицируй owner дефекта. Спроси:
может ли исходный packet и spine пройти acceptance, честно оставляя недоступное
evidence как gap?

- Advisor-compliance defect → запусти один новый history-isolated replacement
  с тем же packet, framework и полным brief плюс нейтрально названный defect.
- Packet, spine или controller defect → исправь owner input и заново запусти
  все затронутые streams; если изменился общий packet, сбрось comparability и
  перезапусти все обязательные streams.

Retained delta-repair не создаёт одного publishable full output. Runtime blocker
допустим только после повторного failure на валидном brief. Не лечи отсутствующий
trace пересказом root-а или склейкой двух ответов.

## 5. Покажи Traces И Только Потом Синтезируй

Все обязательные streams образуют completion barrier. До их возврата и
acceptance нельзя финализировать основное решение, заявлять глубокий анализ или
продолжать implementation, для которого этот анализ был prerequisite.

В user-facing ответе:

1. Покажи selection table.
2. Опубликуй каждый accepted subagent output отдельным подписанным блоком.
   Сохрани framework declaration, все step traces, conclusion и coverage index;
   не заменяй их root-summary. Допустима только механическая очистка повторного
   preamble, не удаляющая evidence шага.
3. После raw traces дай root synthesis:
   - convergence: одинаковый вывод из разных operations;
   - productive conflict: несовместимые premises, границы или criteria;
   - unique contribution: что увидел только один framework;
   - unresolved gap: какое evidence способно изменить решение;
   - integrated implication: следующий owner decision или действие.

Не голосуй и не считай consensus доказательством. Три framework-а могут
наследовать один и тот же ошибочный task packet; конфликт часто полезнее
согласия. Root проверяет load-bearing factual claims до действия.

## Thought Demonstrations

**Default → transition.** Один агент пишет разделы «First Principles»,
«Premortem» и «Systems Thinking», но во всех трёх повторяет исходный вывод.
History-isolated streams получают разные step spines. Первый пересобирает
constraints, второй строит failure causes и signals, третий замыкает feedback
loops. Теперь различие видно в intermediate representations, а не в заголовках.

**Anti-example.** Агент сначала перечислил шесть шагов ATAM, затем дал общий
архитектурный совет и поставил всем шагам `complete`. Step order назван, но
quality-attribute scenarios, sensitivity points и tradeoff evidence в ответе
отсутствуют. Это framework theatre; trace отклоняется.

**Transfer.** Для схемы данных root выбирает Transaction Boundary Analysis,
CAP/PACELC и Information Scent, а не три общих decision matrix. Первый lens
локализует invariants, второй раскрывает distributed tradeoffs, третий
проверяет, сможет ли человек найти и понять данные. Один packet получает три
действительно разные representations.

## Evidence, Feedback И Stop

Структурный validator доказывает только package shape. Один красивый run
доказывает возможность, но не то, что skill стабильно глубже минимального
comparator-а. Behavioral claim проверяй на непоказанной задаче: совпадают ли
framework declaration, полный step trace, distinct representations и
decision-changing synthesis у нескольких matched runs с skill и без него.
Initial non-replayable observations записаны в
[`references/characterization.md`](references/characterization.md). Они не
являются evidence gate; exact matched single-context comparator дал
сопоставимый результат, поэтому skill не приписывает isolation доказанный
cognitive lift. Его продукт — раздельная provenance, auditable method artifacts
и completion barrier.

Failure tells, которые reopen-ят дизайн:

- agents называют разные methods, но возвращают одну representation;
- root выбирает methods по поверхностной теме, не показав cognitive work и
  structural fit;
- cross-domain перенос незаметно меняет, сокращает или смешивает методологию;
- trace fields заполнены, а следующий шаг не использует предыдущий;
- technical tasks снова получают только общие mental models;
- root сжимает native traces до гладкого consensus;
- один-agent comparator стабильно даёт те же операции и решение дешевле.

Skill завершён, когда минимум три history-isolated accepted traces
опубликованы, synthesis сохранил различия и gaps, а следующий owner decision
явен. Если native fresh-subagent primitive или conversation isolation
недоступны, либо после разрешённой замены осталось меньше трёх accepted
streams, честно верни runtime blocker: локальная имитация не считается
выполнением `$1deep-agents`.

Субагенты остаются prompt-constrained no-tools/no-write advisors. После
synthesis root может продолжить отдельно разрешённую implementation-задачу, но
не приписывает её framework agents. Codex characterization рассчитана на
`GPT-5.6`, 2026-08-05. Claude adapter структурно перенесён, но отдельно
поведенчески ещё не охарактеризован; смена target model, subagent schema или
isolation semantics переоткрывает контракт.
