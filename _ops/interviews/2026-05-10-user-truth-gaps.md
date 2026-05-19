---
type: interview
status: draft
answer_role_other: ИИ иследователь
context_personal: true
---

# Про тебя и полигон

Первое интервью в этом проекте. Цель — закрыть пробелы в `_ops/criteria/`,
которых сейчас нет: текущие 15 файлов описывают слои, процессы и routing, но
почти ничего не говорят про тебя как исследователя.

Жми на чекбоксы и выбирай из списков. Свободные поля — только когда
своё. Когда будешь готов, напиши «проверь» — разнесу ответы по владельцам.

> [!note] Контекст
> Канон проекта: `GPT-5.5` и `Claude Opus 4.7`. Полигон — не backlog задач,
> а живая память для будущей сессии: knowledge, criteria, временные интервью,
> проблемы.

---

## 1. Кто ты сейчас в полигоне

> [!question] Роль (выбери одну главную)
> `INPUT[inlineSelect(option(curator, 'Куратор — выбираю и отвергаю предложения агентов'), option(knowledge, 'Инженер знаний — вытаскиваю durable правду в criteria'), option(researcher, 'Исследователь паттернов — тестирую как ведёт модель'), option(architect, 'Архитектор системы — проектирую слои и routing'), option(publisher, 'Издатель — готовлю выводы для других')):answer_role]`
>
> Своё: `INPUT[textArea(placeholder('Если ни одна роль не подходит')):answer_role_other]`

> [!question] Что параллельно отнимает внимание
> - `INPUT[toggle:context_commercial]` Параллельные коммерческие проекты
> - `INPUT[toggle:context_other_llm]` Другие LLM-эксперименты
> - `INPUT[toggle:context_learning]` Обучение, чтение источников
> - `INPUT[toggle:context_teaching]` Преподавание, делёжка опытом
> - `INPUT[toggle:context_personal]` Личная жизнь, не-проектное
>
> Своё: `INPUT[textArea(placeholder('Что ещё')):answer_context_other]`

---

## 2. Зачем

> [!question] Что ты хочешь получить от полигона
> - `INPUT[toggle:goal_templates]` Накопить рабочие шаблоны под GPT-5.5 / Opus 4.7
> - `INPUT[toggle:goal_coherence]` Понять, как удерживать coherence в длинных сессиях
> - `INPUT[toggle:goal_minimal]` Найти minimal stack правил, который работает
> - `INPUT[toggle:goal_portable]` Подготовить переносимые скилы для других проектов
> - `INPUT[toggle:goal_understanding]` Глубже понять, как ведут себя модели
> - `INPUT[toggle:goal_publish]` Вынести выводы наружу — в статьи, разговоры, гайды
>
> Глубже одной фразой: `INPUT[textArea(placeholder('Главное, ради чего ты это делаешь')):answer_motivation]`

> [!question] Что планируешь использовать в реальных проектах
> - `INPUT[toggle:export_full]` Скил-систему как есть
> - `INPUT[toggle:export_criteria]` Только криитерия-протокол
> - `INPUT[toggle:export_wisdom]` Конкретные wisdom-файлы
> - `INPUT[toggle:export_instruction]` Подход к instruction-layer
> - `INPUT[toggle:export_routing]` Принцип routing через owner-skills
> - `INPUT[toggle:export_none]` Пока непонятно

---

## 3. Картина успеха

> [!tip] Хорошая сессия — что в ней есть
> - `INPUT[toggle:good_variants]` Начинается с короткого выбора вариантов
> - `INPUT[toggle:good_short_text]` Я почти не пишу длинных текстов
> - `INPUT[toggle:good_criteria_write]` Заканчивается записью в criteria
> - `INPUT[toggle:good_artifact]` Заканчивается готовым артефактом
> - `INPUT[toggle:good_proactive]` Агент сам предлагает следующий ход
> - `INPUT[toggle:good_disagree]` Агент со мной спорит, когда видит ошибку

> [!warning] Плохая сессия — что в ней есть
> - `INPUT[toggle:bad_ritual]` Длинные ритуалы без ценности
> - `INPUT[toggle:bad_lazy_q]` Агент задаёт вопросы, ответ на которые есть в файлах
> - `INPUT[toggle:bad_paraphrase]` Paraphrase вместо проверки
> - `INPUT[toggle:bad_silent_exec]` Агент молча выполняет, не показав варианты
> - `INPUT[toggle:bad_sycophancy]` Sycophancy: соглашается со всем подряд
> - `INPUT[toggle:bad_drift]` К концу сессии агент уехал от изначальной цели

---

## 4. Что радует и что бесит

> [!question] Радует
> - `INPUT[toggle:love_variants]` Варианты до плана
> - `INPUT[toggle:love_doubt]` Признание неуверенности вслух
> - `INPUT[toggle:love_quotes]` Verbatim-цитаты из anchors вместо пересказа
> - `INPUT[toggle:love_short]` Короткие ответы
> - `INPUT[toggle:love_files_first]` Агент сам читает файлы прежде чем спросить
> - `INPUT[toggle:love_owner_call]` Proactive вызов owner-skills
> - `INPUT[toggle:love_critique]` Критика моей формулировки

> [!warning] Бесит
> - `INPUT[toggle:hate_long_en]` Длинные английские заголовки в русских файлах
> - `INPUT[toggle:hate_dup]` Дублирование правил между файлами
> - `INPUT[toggle:hate_ritual_write]` Ритуальные write без смысла
> - `INPUT[toggle:hate_skip_files]` «Я и так знаю» вместо чтения файлов
> - `INPUT[toggle:hate_ceremony]` Лишняя ceremony на простых задачах
> - `INPUT[toggle:hate_jargon]` Программистский жаргон в обсуждении
> - `INPUT[toggle:hate_summary]` Подведение итогов после tool-call

---

## 5. Красные линии

> [!warning] Никогда
> - `INPUT[toggle:rl_criteria]` Не редактировать `_ops/criteria/*.md` без `1user-truth`
> - `INPUT[toggle:rl_chat_qa]` Не превращать чат в длинное Q&A вместо `_ops/interviews/`
> - `INPUT[toggle:rl_invent]` Не выдумывать criteria за пользователя
> - `INPUT[toggle:rl_skill_md]` Не игнорировать SKILL.md в пользу root-инструкции
> - `INPUT[toggle:rl_neutral]` Не считать model-neutral советы baseline
> - `INPUT[toggle:rl_destroy]` Не делать destructive команды без подтверждения
> - `INPUT[toggle:rl_lang]` Не отвечать по-английски без явной просьбы
>
> Своё: `INPUT[inlineList(placeholder('Добавить красную линию')):answer_red_lines_other]`

---

## 6. Ритм работы

> [!question] Когда работаешь
> `INPUT[inlineSelect(option(daily_short, 'Короткие сессии в течение дня'), option(weekend_long, 'Длинные подходы по выходным'), option(impulse, 'Хаотично, по импульсу'), option(fixed, 'Каждый день в фиксированное время'), option(burst, 'Бурстами по неделям')):answer_rhythm]`

> [!question] Что значит «закончил»
> - `INPUT[toggle:done_task]` Закрытая задача в task-файле
> - `INPUT[toggle:done_criteria]` Новая запись в `_ops/criteria/`
> - `INPUT[toggle:done_skill]` Новый или обновлённый skill
> - `INPUT[toggle:done_clean]` Чувство «теперь чище»
> - `INPUT[toggle:done_archive]` Интервью или проблема ушли в архив
> - `INPUT[toggle:done_commit]` Сделан commit и backup в GitHub

---

## 7. Куда полигон НЕ должен идти

> [!warning] Anti-goals
> - `INPUT[toggle:anti_backlog]` Стать backlog-трекером задач
> - `INPUT[toggle:anti_neutral]` Стать каталогом model-neutral советов
> - `INPUT[toggle:anti_marketplace]` Стать local copy of marketplace skills
> - `INPUT[toggle:anti_complexity]` Расти в сложности слоёв
> - `INPUT[toggle:anti_second_truth]` Создать вторую правду рядом с README/criteria
> - `INPUT[toggle:anti_runtime]` Превратиться в runtime-код агентов
> - `INPUT[toggle:anti_artifact]` Стать каталогом artifacts проектов
>
> Своё: `INPUT[textArea(placeholder('Что ещё неприемлемо')):answer_anti_goals_other]`

---

## 8. Свободное

> [!note] Что я не спросил
> `INPUT[textArea(placeholder('Любая мысль про проект, агентов или процесс — то, что не уложилось в чекбоксы')):answer_freeform]`

---

<details>
<summary>Для агента</summary>

После команды пользователя «проверь»:

- Прочти каждое поле — `toggle` (true/false), `inlineSelect` (значение опции),
  `inlineList` / `textArea` (свободный текст).
- Direct durable user truth → `1user-truth` → `_ops/criteria/*.md`. Файлы
  выбирай по сфере: например, новый `user-rhythm-and-success.md`,
  `agent-tone-and-red-lines.md` или дополни существующие.
- Anti-goals в форме повторяемого правила → `_ops/criteria/*.md`;
  описательные anti-goals → `README.md` через `1strategy`.
- Goal/мотивация уровня проекта → `_ops/PROJECT-ROADMAP.md` через `1planning`.
- Нерешённая проблема, которая всплывёт из ответов → `_ops/findings/**`.
- Полностью разобранное интервью → `_ops/interviews/_archive/`. Если хотя бы
  одно поле осталось без владельца — не архивируй.

Якорный criteria этого файла: `_ops/criteria/interview-intake-workflow.md`.

</details>
