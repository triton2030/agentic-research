# Format Examples

Worked examples of `criteria-generator` output across task types. Use as shape templates, not as content to copy.

## Example 1: Code bugfix

**Input:**
> "Пользователь жалуется, что при экспорте CSV пропадают строки. Почини."

**Output:**

    ## Original task
    Пользователь жалуется, что при экспорте CSV пропадают строки. Почини.

    ## Understood intent
    Найти и устранить причину, по которой часть строк не попадает в экспортированный CSV. "Починено" означает: конкретный баг идентифицирован, исправлен, и существует тест, который падал бы без фикса.

    ## Assumptions (not verified with user)
    - Речь про экспорт в функции `exportToCSV` в `src/exports/csv.ts` (единственный матч по grep).
    - "Пропадают" означает отсутствуют в выводе, а не дублируются.

    ## Acceptance criteria

    ### Must (blocks completion)
    - [ ] Root cause сформулирован одним предложением со ссылкой на строку кода — **Evidence:** строка вида `src/exports/csv.ts:LINE — <причина>`.
    - [ ] Регрессионный тест написан и падает на текущем коде — **Evidence:** вывод `npm test -- csv` до фикса с конкретным `expected N rows, got M`.
    - [ ] Фикс применён — **Evidence:** diff в `src/exports/csv.ts`, не более 20 строк изменений, не затрагивает не связанные функции.
    - [ ] Регрессионный тест проходит после фикса — **Evidence:** вывод `npm test -- csv` с `N passed`.
    - [ ] Полный тестовый набор проходит — **Evidence:** вывод `npm test` с итоговой строкой `All tests passed`.

    ### Must not (anti-patterns)
    - [ ] Не добавлять `if (rows.length === 0) return` или аналогичный silencing — **Why this would be bypassed:** заставит тест "пройти" путём скрытия проблемы.
    - [ ] Не менять форматирование или стилистику файла вне зоны фикса — **Why this would be bypassed:** раздувает diff и маскирует реальное изменение.
    - [ ] Не перезаписывать входной массив перед экспортом — **Why this would be bypassed:** имитирует корректный вывод, но не устраняет причину.

    ### Verification protocol
    1. `git diff --stat src/exports/csv.ts`
       Expected: одно-два изменённых места, <20 строк.
    2. `npm test -- csv 2>&1 | tail -20`
       Expected: регрессионный тест в списке PASSED.
    3. `npm test 2>&1 | tail -5`
       Expected: строка `Tests: X passed`, ноль failed.

## Example 2: Research

**Input:**
> "Разберись, какие новые техники prompt compression появились в 2026 году и что применимо у нас."

**Output:**

    ## Original task
    Разберись, какие новые техники prompt compression появились в 2026 году и что применимо у нас.

    ## Understood intent
    Собрать обзор техник prompt compression 2026 года, отфильтровать по применимости в нашем текущем стеке (Claude Code + Anthropic SDK), и вернуть короткий рабочий список "что внедрять" с обоснованием.

    ## Assumptions (not verified with user)
    - "У нас" = проект `agentic-research` и соседние Claude Code workflows.
    - Применимость оценивается по трём осям: reduction %, complexity cost, зависимость от кастомной инфраструктуры.

    ## Acceptance criteria

    ### Must (blocks completion)
    - [ ] Минимум 5 техник с 2026 года названы, у каждой есть источник — **Evidence:** markdown-список с прямыми ссылками (URL) на статьи или репозитории 2026 года.
    - [ ] Для каждой техники указано одно предложение о механизме — **Evidence:** поле `Mechanism:` под каждой техникой, не копия аннотации, а своя формулировка.
    - [ ] Применимость оценена по трём осям — **Evidence:** таблица `technique | reduction | complexity | infra dep`.
    - [ ] Итоговый короткий список "внедрять / отложить / мимо" — **Evidence:** раздел `Verdict` с 3 сегментами и обоснованием из одной строки на каждую технику.

    ### Must not (anti-patterns)
    - [ ] Не включать техники старше 2026 года — **Why this would be bypassed:** легко набрать объём за счёт классики и прикрыть отсутствие реально нового.
    - [ ] Не ссылаться на блоги без первичного источника (paper / repo) — **Why this would be bypassed:** вторичные пересказы часто искажают механизм.
    - [ ] Не делать вывод "применимо" без конкретного места в нашем стеке — **Evidence:** каждая техника в Verdict ссылается на конкретный скрипт, скилл или workflow.

    ### Verification protocol
    1. Проверить, что все URL-ы в источниках отдают 200 — **Expected:** нет 404.
    2. Прочитать одну статью целиком и сверить с полем `Mechanism` — **Expected:** формулировка точная, не вводит в заблуждение.

## Example 3: Skill or agent creation

**Input:**
> "Сделай мне скилл для ревью пулл-реквестов."

**Output:**

    ## Original task
    Сделай мне скилл для ревью пулл-реквестов.

    ## Understood intent
    Создать Claude Code скилл, который по запросу анализирует PR (diff + описание) и возвращает структурированный ревью: блокирующие замечания, предложения, вопросы, общий вердикт.

    ## Assumptions (not verified with user)
    - Скилл глобальный (`~/.claude/skills/`), не привязан к одному репозиторию.
    - Источник PR — команда `gh pr view` или URL.
    - Формат вывода — markdown в чат.

    ## Acceptance criteria

    ### Must (blocks completion)
    - [ ] Файл `~/.claude/skills/pr-review/SKILL.md` существует — **Evidence:** `ls ~/.claude/skills/pr-review/SKILL.md`.
    - [ ] Frontmatter содержит `name` и `description` с явным "when to use" — **Evidence:** первые 5 строк файла.
    - [ ] Рабочий ход имеет нумерованные шаги с артефактами — **Evidence:** раздел `## Process` с шагами Step 1…N, у каждого `Artifact:` строка.
    - [ ] Раздел Red Flags присутствует с минимум 3 пунктами — **Evidence:** таблица или список под заголовком `## Red flags`.
    - [ ] Smoke test пройден на 1 реальном PR — **Evidence:** вывод скилла на конкретном PR, прикреплённый к диалогу.

    ### Must not (anti-patterns)
    - [ ] Не писать скилл как "общие правила ревью" без рабочего хода — **Why this would be bypassed:** превращается в энциклопедию, не в инструмент.
    - [ ] Не требовать внешних сервисов кроме `gh` — **Why this would be bypassed:** ломает портативность.
    - [ ] Не возвращать размазанный вывод без структуры — **Evidence:** выход должен иметь фиксированные секции Blocking / Suggestions / Questions / Verdict.

    ### Verification protocol
    1. `ls ~/.claude/skills/pr-review/` — **Expected:** `SKILL.md` плюс `references/` при необходимости.
    2. Invoke skill on a sample PR URL — **Expected:** вывод в заданном формате, без отклонений.

## How to pick the right shape

- **Code changes:** всегда Evidence = команда + ожидаемый вывод.
- **Research / writing:** Evidence = ссылки, цитаты, таблицы.
- **Infra / config:** Evidence = вывод `diff`, `kubectl get`, `terraform plan`, etc.
- **Skill / agent authoring:** Evidence = путь к файлу плюс структурная проверка.
