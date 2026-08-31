# 1codex-bg-threads — clean-room semantic draft

> Исторический loss oracle. Owner correction от `2026-08-30T19:23:46+05:00`
> сняла typed receiver envelopes и заменила их простой Markdown-инструкцией.
> Этот файл не входит в exact runtime candidate.

Статус: смысловой черновик до authoring modes. Это zero-based reimplementation,
а не реконструкция прежней структуры пакета. В этом файле нет `SKILL.md`,
runtime reference или предположений о старых именах команд и схемах.

## Базовая функция

Переносить делимое мышление и исполнение в видимые фоновые Codex threads под
управлением root, который действует как технический директор: сохраняет
бизнес-направление, связность решений, интеграцию и приёмку, а не забирает
делимую работу обратно себе.

Полезный результат функции — больше проверяемой самостоятельной работы за тот
же бюджет без потери качества решений. `1orchestration` отвечает за смысловую
нарезку outcomes; этот skill отвечает за то, чтобы такая нарезка стала
управляемым жизненным циклом видимых Codex threads.

## Admission, trigger, skip и near-miss

### Admission / trigger

Скилл допускается, когда владелец просит offload, create, continue, fork или
retain видимых фоновых Codex threads, либо уже вызванный оркестратор обнаружил
делимые outcomes, которые по замыслу должны выполняться в таких threads.

При admission должны быть различимы три вещи: самостоятельный outcome каждого
потока, ответственность root за сквозное решение и способ предъявить итоговое
состояние потока. Если хотя бы одна из них пока не различима, это gap для
уточнения или остановки, а не разрешение выдумать схему.

### Skip

Пропустить этот скилл следует, если просьба не касается видимых фоновых Codex
threads и не требует их для заявленного результата. Также skip допустим для
неделимого решения, которое по своей природе принадлежит root, если владелец
не просил вынести его в отдельный видимый thread.

Не следует присваивать этому скиллу общее управление любыми агентами,
Claude-сессиями, внешними провайдерами или обычными задачами, созданными для
непосредственного взаимодействия владельца. Это не отрицательный workflow, а
граница authority: без видимого Codex background-thread результата здесь нет
собственного предмета.

### Near-miss

Близкими, но отдельными случаями являются:

- просьба только распараллелить рассуждение без видимого Codex thread;
- просьба открыть, переименовать, закрепить, архивировать или показать задачу
  без offload и без передачи ей bounded outcome;
- просьба выполнить обычную локальную работу root, когда делимый outcome не
  выделен;
- просьба использовать другой runtime или модель без Codex background-thread
  lifecycle.

В этих случаях нельзя автоматически расширять scope этого скилла каталогом
соседних операций.

## Предлагаемое commander's intent

### Уникальный контекст

Модель пользователя — не единственный исполнитель, а root-оркестратор. Дешёвые
Luna Max дают масштаб, но mutable результат фонового исполнителя нельзя считать
истиной без независимой проверки. Retained thread полезен накопленным контекстом,
но его память не является текущим источником правды; доступные lifecycle,
модели и команды определяет живой Codex runtime.

### Цели пользователя

1. Вся посильная самостоятельная работа и делимое мышление уходят в правильно
   ограниченные видимые threads; root сохраняет бизнес-приоритеты, topology,
   сквозные решения, integration и acceptance, поэтому прямое исполнение root
   само по себе не считается успехом.
2. Каждый thread получает один ограниченный outcome и достаточный актуальный
   контекст; Luna Max является default, а Sol medium или Sol xhigh выбирается
   только при доказанной сложности задачи.
3. Mutable результаты и terminal lifecycle подтверждаются внешним evidence;
   retained context переиспользуется только после обновления источников, Local
   остаётся default, а Worktree применяется лишь при доказанном и
   неустранимом пересечении записи.

## Decision / outcome contract

Состояние считается успешным, если для каждого принятого делимого outcome
существует видимый Codex thread с ограниченной ответственностью, достаточным
актуальным контекстом и обоснованными model/isolation choices; root разрешил
конфликты и принял интегрированный результат по предъявленному evidence; native
lifecycle завершён наблюдаемым terminal state.

Основные решения должны отвечать следующим вопросам.

1. **Делимость.** Можно ли отделить outcome так, чтобы его границы и критерий
   готовности были понятны без передачи thread всего проекта? Если да, outcome
   уходит worker-у; если нет, его владеет root или он останавливается.
2. **Когнитивная нагрузка.** Разделение делается по самостоятельным outcomes и
   тому, что каждый thread должен удерживать, а не по произвольному числу
   агентов или фиксированным волнам.
3. **Контекст.** Переданный контекст должен быть достаточным для outcome и
   актуальным относительно источников. Retained memory ускоряет работу, но не
   заменяет обновление источников.
4. **Модель.** Default — Luna Max. Sol medium или Sol xhigh — исключение,
   которое допускается только с наблюдаемым основанием сложности; точный
   runtime alias и capability check относятся к живому runtime reference.
5. **Запись и изоляция.** Local — default. Worktree нужен только когда
   доказано, что одновременные записи пересекаются и пересечение нельзя снять
   разрезом ownership или иным безопасным разделением.
6. **Проверка mutable output.** Если thread фактически изменил файлы или другое
   mutable состояние, его результат нельзя принять по self-report worker-а.
   Нужен независимый внешний check, который читает сам результат и показывает
   pass, failure или gap. Для read-only анализа такой обязательный writer-check
   не требуется, но его полезность и границы всё равно остаются за root.
7. **Lifecycle.** Создание, продолжение, fork, reuse и terminal completion
   должны быть видимы через native Codex state. Вызов команды, ответ worker-а
   или retained memory сами по себе не доказывают terminal outcome.
8. **Root ownership.** Root синтезирует результаты, разрешает расхождения,
   удерживает бизнес-приоритет и topology, выполняет integration и final
   acceptance. Worker не может принять сквозное решение вместо root.

Минимальный return contract worker-а: bounded outcome, краткий результат,
адресуемое evidence, gaps или blockers и наблюдаемый lifecycle status. Root
возвращает наружу не список запущенных потоков, а решение о том, что принято,
что отклонено или заблокировано, почему, и чем это подтверждается.

## Невыводимые инварианты

Следующие вещи нельзя безопасно получить из commander's intent и нельзя
зашивать в semantic draft как будто они уже решены.

- Точные имена native Codex commands, допустимые enum, поля API и набор
  terminal states.
- Точный runtime alias для «Luna Max», «Sol medium» и «Sol xhigh», их текущие
  capability limits и способ доказать complexity.
- Определение mutable state для конкретного Codex runtime и минимальная форма
  независимого verifier-а.
- Кто именно является независимым проверяющим, какой у него доступ и как
  предъявляется его verdict.
- Как runtime обозначает retained thread, как выбирать его по теме и какие
  обновления источников обязательны перед reuse.
- Точный критерий file-overlap, правила writer ownership и механика выбора
  Local/Worktree.
- Максимальный fan-out, число waves, параллельность, timeout, retry, pin,
  archive, navigation и другие UI/lifecycle actions.
- Нужно ли получать отдельное подтверждение владельца непосредственно перед
  каждой внешней мутацией; этот вопрос должен решаться живыми permission и
  runtime правилами, а не догадкой из semantic intent.
- Точная структура worker card, thread metadata, handoff или completion
  record.

Эти gaps не отменяют семантику root-orchestrator и не оправдывают возврат
делимой работы root-у; они запрещают притворяться, что неизвестные runtime
детали уже определены.

## Режимы, которым действительно понадобятся references

В будущем authoring pass может выделить references только для режимов, где
runtime-specific knowledge меняет действие. Core semantic contract выше не
нуждается в reference-файле для повторения очевидной цели.

1. **Native lifecycle mode.** Нужна актуальная официальная Codex reference для
   create/continue/fork/retain, видимости задач, terminal states и способов
   получить внешний status evidence.
2. **Model-routing mode.** Нужна актуальная runtime/model reference для
   валидных alias, effort/capability и наблюдаемых признаков «доказанной
   сложности»; она не должна превращать Sol в новый default.
3. **Mutable-verification mode.** Нужна reference, только если bundled
   runtime задаёт особый verifier protocol, write evidence или независимый
   reader contract, которые нельзя выразить общим outcome contract.
4. **Reuse-and-refresh mode.** Нужна reference, если retained thread имеет
   специальный re-entry API или обязательный refresh sequence источников.
5. **Isolation mode.** Нужна reference, если Local/Worktree и file-overlap
   зависят от конкретного Codex workspace/runtime механизма.

`1orchestration` остаётся companion authority для cognitive decomposition. Не
нужно копировать его body сюда; reference появляется только если этот skill
добавляет Codex-specific seam, которого нельзя вывести из outcome contract.

## Stop и evidence

Остановиться с явным gap или blocker нужно, когда отсутствует bounded outcome,
недостаточен актуальный контекст, не доказана сложность для Sol, неясен writer
ownership, невозможно независимо проверить mutable output, не наблюдается
native lifecycle state, либо integration конфликтует с бизнес-приоритетом и
его нельзя разрешить без root/владельца.

Evidence должно покрывать ровно заявленные свойства:

- **Admission:** исходная просьба владельца и карта делимых outcomes.
- **Routing:** для каждого thread видны outcome, актуальный контекст,
  model/isolation choice и retained/reuse decision.
- **Behavior:** worker return с адресами evidence, gaps/blockers и status.
- **Mutable result:** независимый check фактически изменённого результата,
  а не только сообщение worker-а.
- **Lifecycle:** внешний native status, включая terminal state, а не только
  факт вызова команды.
- **Integration:** решение root о конфликтах, принятии или остановке и его
  связь с business priority/topology.

Чтение инструкции, наличие вызова skill, self-report агента и retained memory
не являются доказательством соблюдения. Если требуемого evidence нет, outcome
не объявляется принятым.

## Оценка active set

Оценка для core body: 14 самостоятельных инструкций/ограничений — admission,
граница scope, делимость, когнитивное разбиение, контекст, model default,
complexity exception, retained freshness, isolation, mutable verification,
lifecycle evidence, root ownership, worker return и stop/evidence gate.

Каждый условно загруженный runtime reference добавляет примерно 3–5
самостоятельных единиц только в своём режиме. При одном активном режиме общий
набор остаётся ориентировочно в пределах 17–19; все перечисленные references
не должны загружаться одновременно. Точный count потребует authoring draft и
runtime schema, которых этот clean-room этап намеренно не создаёт.

## Сознательно не добавлено

- фиксированное число workers, waves, fan-out или параллельных turn-ов;
- каталог всех Codex lifecycle/UI операций;
- конкретные команды, API payloads, aliases, status enums и thread schemas;
- обязательная пошаговая процедура для каждой задачи;
- generic self-review, checklist или ritual, не привязанный к evidence;
- автоматический retry, timeout, polling, archive, pin или cleanup policy;
- модельная матрица за пределами Luna Max default и Sol medium/xhigh exception;
- перенос authority `1orchestration` или дублирование его cognitive-decomposition
  правил;
- Claude, внешние провайдеры и не-Codex background runtimes;
- отдельный protocol для read-only threads, если его необходимость не появится
  в наблюдаемом failure mode;
- воспроизведение старой структуры, имён файлов, historical cards,
  `THREAD_CARD`/`THREAD_DONE` и любых других неданных здесь форматов;
- installation, projection, compatibility и parity procedures;
- интернет-поиск и runtime documentation в semantic draft: они относятся к
  будущему reference-authoring, а не к clean-room смыслу.

## Gaps для следующей стадии

Semantic intent не выбирает точные Codex commands, runtime schema, verifier
identity, complexity signal, retained refresh sequence или Local/Worktree
mechanics. Эти gaps требуют официального живого Codex runtime evidence при
authoring modes; они не являются разрешением восстанавливать старый пакет по
памяти.

## Точно прочитанные пути и граница clean room

Прочитаны полностью:

- `/Users/triton/Documents/GitHub/agentic-research/skills/1codex-bg-threads/intent-2026-08-30.md`
- `/Users/triton/.codex/skills/1skill-creation/SKILL.md`
- `/Users/triton/.codex/skills/1skill-creation/references/goal-context.md`
- `/Users/triton/.codex/skills/1skill-creation/references/refactor.md`
- `/Users/triton/Documents/GitHub/agentic-research/knowledge/practical-guides/how-to-write-skills/authoring-canon.md`
- `/Users/triton/.codex/skills/.system/skill-creator/SKILL.md`
- `/Users/triton/.codex/skills/1chat-recall/SKILL.md`
- `/Users/triton/.codex/skills/1chat-recall/references/retrieval.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/product-frames/agentic-research.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/product-frames/agentic-research.principles.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/AGENTS.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/GOAL.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/AGENTS.md`
- `/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-skills-plugins.md`
- `/Users/triton/Documents/GitHub/agentic-research/knowledge/wisdom-llm.md`
- `/Users/triton/Documents/GitHub/agentic-research/_ops/chat-recall/2026-08-29-203235-codex-01a04e23.md`

Честное подтверждение: я не читал `/Users/triton/.codex/skills/1codex-bg-threads/**`,
старые `draft-*` и любые другие history/evidence/reviews файлы в
`/Users/triton/Documents/GitHub/agentic-research/skills/1codex-bg-threads/**`.
Единственное прочитанное исключение внутри этой папки —
`intent-2026-08-30.md`; новый файл здесь создан с нуля.
