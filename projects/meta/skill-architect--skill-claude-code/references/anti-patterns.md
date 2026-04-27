# Anti-patterns — Чему Я Не Верю

Не абстрактные запреты. Позиции, заработанные на повторении одних и тех же сбоев.

## Порядок Мышления

- **Failure scan до capability inventory.** Сканить сбои, не зная, что уже установлено, = изобретать то, что есть, или строить защиту рядом с работающей. Capability inventory (Шаг 2) обязателен до failure classes (Шаг 4).
- **Forces в эпилоге.** Если силы прописаны в конце как украшение, design под них не адаптирован. Forces — constraint на вход (Шаг 3), не output.
- **Add-only output без Minimize pass.** Архитектор, который только добавляет, делает систему тяжелее каждой сессией. Шаг 7 обязателен, молчание = сбой Gate.
- **«1 failure → 1 prescription» без Leverage analysis.** Инженерная гигиена, не архитектура. Сначала ищи systemic fix, закрывающий класс; только потом 1:1 patch.

## Upstream Truth Layer

- **Читать `_ops/` как snapshot, не как hot state.** Триада (PLAN + INTERVIEW + learnings) должна обновляться **при каждом значимом сигнале**, не раз в месяц. Архитектор, читающий stale триаду, работает по устаревшей карте.
- **Prescription без механизма обновления триады.** Если в output нет ни одного hook / skill / checkpoint, который триггерит запись в `_ops/` при preference revealed / plan delta / expected-vs-actual дельте — архитектор оставил upstream без защиты. Это failure, не feature.
- **Делегировать freshness дисциплине пользователя или модели.** Обе дисциплины проигрывают усталости, token economy и забыванию. Freshness — **структурная задача**, не «попросим запомнить».
- **Ожидать, что `project-roadmap` сам вызовется при каждом сигнале.** `project-roadmap` — процедура, а не fairy. Её вызов должен быть триггернут механизмом (UserPromptSubmit hook на preference keywords, Stop hook на Stage completion), а не надеждой.

## Проектирование

- **Красивым схемам ролей до проверки plan-specific failure modes.** Порядок «схема → сбои» подгоняет реальность под схему. Правильный порядок — «telos → as-is → forces → failures → leverage → prescriptions».
- **Generic failure mode** (*«модель может ошибиться»*) вместо plan-specific. Это лозунг, не рабочая диагностика. Failure обязан ссылаться на конкретный Stage или дельту в learnings.
- **Созданию нового skill'а без доказанной необходимости.** Каждый новый skill — cost (context, maintenance, trigger pollution). `local-skill-contract.md` proof gate обязателен **и** reuse-first gate.
- **Prescription без reuse-first gate.** «Добавить hook X» без строки *«существующее покрытие <handle> недостаточно, потому что Y»* = изобретение вслепую.

## Защитные слои

- **Prompt-only защитам.** Декомпозируются с каждым token budget shift. Если сбой важный — перенеси в runtime или skill, даже если дороже.
- **Одному правилу в трёх местах без owner'а.** `_ops/` + `AGENTS.md` + skill + hook на одну проблему — drift-источник. Один owner или compose layer.
- **Prescription без sunset signal.** Правило, которое нельзя похоронить — archaeology by construction.
- **Sunset signal, не связанный ни с одной Force.** Если ни одна из названных сил не делает эту prescription уязвимой, либо сила косметическая, либо prescription слепая. Проверяй в Шаге 8.

## Capabilities

- **Предположению о capability по текстовому упоминанию.** Проверяй реальную установку (`settings.json`, `installed_plugins.json`), не «в README написано — значит есть». Subagent probe или прямая проверка.
- **Внешнему поиску до локального capability audit.** Обычно решение уже лежит в репо — не увидел, потому что не посмотрел.
- **Построению нового skill'а, когда marketplace уже содержит подходящий.** Reuse-first gate блокирует это.

## Folder discipline

- **Удалению папки без Chesterton's fence probe.** Если не знаешь, зачем она была — не трогай. Archaeology иногда держит load-bearing state.
- **Folder audit без привязки каждой папки к Stage или preference-секции.** Нет якоря — либо папка устарела, либо план не полон.

## Язык и precedence

- **Английскому голосу в русскоязычном truth layer.** Смешение ломает precedence и создаёт fuzzy mental model.

## Вопросы

- **`AskUserQuestion` в формате «согласен с моим анализом?»** — leading-prompt, сикофантия в маскировке.
- **Вопросам без EVPI-проверки.** Вопрос, ответ на который не меняет prescription — делегирование мышления пользователю.

## Внутренние инструменты

- **Видимым секциям «Inversion» / «Premortem» / «Pressure-test» в файлах.** Это внутренние инструменты мышления, не артефакты. В файл попадает либо prescription, либо запись в learnings.

## Future-proofing

- **Закладке абстракций «на всякий случай».** `PROJECT-ROADMAP.md` покрывает всю траекторию — используй это, чтобы **удалять** сложность, а не готовиться к воображаемому будущему. Default — YAGNI; знание плана даёт право на упрощение, а не мандат на future-proof.
- **Fix под сегодняшнюю модель/тулзу без sunset signal.** Hook matcher, зашитый под текущее имя модели, сломается при смене. Если сила «смена модели» в Шаге 3 — sunset должен сработать по её early signal.

## Two Users

- **Оптимизации только под AI-сессию.** Если структура понятна ИИ, но живой человек не находит нужное за минуту — проиграна половина задачи.
- **Оптимизации только под пользователя.** Красивая folder-иерархия, которую ИИ игнорирует, — не архитектура, а косметика.
