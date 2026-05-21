# Self-Learning Log

Свалка наблюдений **только про AI поведение и работу с инструментами** — как модель использует tools / skills / инструкции и где можно сделать комфортнее и быстрее. Owner — `1self-learning` (срабатывает anywhere в сессии при noticing + natural moment после closeout, когда `1work-review` зовёт).

Цель: **«как AI быть полезнее и быстрее конкретно для меня»**. Это comfort & efficiency setup для модели, не tracker проектных задач.

## ЖЁСТКАЯ граница

**Это про AI, не про проект.**

✅ **Пиши когда:**

- **Модель не уловила intent** — user задал → модель пошла не туда → user поправил. Почему не поняла сразу, как сделать прозрачнее.
- **Нужные скилы не сработали** — matcher miss / undertrigger: trigger ожидался, skill не включился (или включился не тот).
- **Инструкция прочитана, но не помогла** — `CLAUDE.md` / `AGENTS.md` / `SKILL.md` открыт, direction не появилось, или два правила конфликтуют.
- **Skill больше мешал чем помогал** — over-triggering, ritual overhead, форма не подходит моменту, заставлял делать лишнее.
- **Felt friction** — субъективно «что-то мешает решить»: непрозрачная boundary, missing tool, конфликт скилов, attention overload.
- **Self-deviation despite clear setup** — несмотря на чёткие инструкции и working скилы модель вдруг повела себя не качественно или в другую сторону. Premature jumping, sycophancy, missed context, literal-vs-intent, over-cautious.
- **Tool overhead высокий** — модель долго искала правильный путь использования tool'а.
- **User поправил посередине работы** — почему signal не уловлен в начале.

❌ **НЕ записывать сюда:**

- Bug в проекте, который надо фиксить → `1findings` / `_ops/findings/`.
- Идея фичи, архитектурный недостаток проекта → `1findings` / `1strategy`.
- Гэп в knowledge/ или missing criterion → `1user-truth` / criteria.
- Что-то про сам repo, код, контент проекта → owner-скил соответствующего слоя.

**Простой тест:** запись помогает **AI работать лучше** или помогает **проекту работать лучше**? Первое — сюда. Второе — `1findings`.

## Mentality

- Свалка. Папка **не загружается** в сессию, **не влияет** на код, **не влияет** на инструкции.
- Пиши смело — лучше слишком много, чем ничего.
- Пользователь сам периодически читает и **вручную чистит**.
- **Scope:** project-local. Cross-project preferences — через `/remember` и `1user-truth`, не здесь.

## Workflow записи

После closeout:

1. **Meta-анализ всего хода:** где модель не поняла сразу? Где user поправлял? Где tool/skill подвели? Где инструкция запутала? Где сама модель отклонилась?
2. **Урок:** как разговор мог быть лучше? Что в инструкции / skill / process помогло бы next time?
3. **Записать** если есть наблюдение. Сомневаешься — **пиши**.

**Идеальный пример сценария:**

> User задал вопрос → модель начала работать → user поправил «не то, я имел в виду X» → это сигнал, что модель не уловила intent с первого раза.

Записать: почему не уловила, что в инструкции / skill / tool наборе помогло бы next раз сразу поймать тот же intent.

## Convention

**Один файл = одна тема** с relevant именем (`literal-vs-intent.md`, `mid-work-correction.md`, `skill-trigger-miss.md`, `instruction-read-no-direction.md`, `tool-choice-overhead.md`). Имя отражает AI pattern, не сессию.

При новом observation:

1. `ls _ops/self-learning/` — есть файл по теме?
2. Есть → дописать в Counter `- YYYY-MM-DD [runtime]: <краткий контекст>`. Не плодить дубль.
3. Нет → создать новый с relevant именем.
4. Уже описано точно то же самое → дописать только counter с runtime.

## Format файла

```md
# <AI Pattern>

## Observation
<1-3 строки: что было в поведении модели, что мешало>

## Counter
- 2026-05-19 [Claude Opus 4.7]: <session/контекст: что именно произошло>
- 2026-05-19 [GPT-5.5]: <контекст>

## Possible upgrade (опц.)
<куда могло бы пойти улучшение для AI setup —
имя скила, инструкции, hook'a; не делать сейчас>
```

**Runtime field обязателен.** GPT-5.5 и Claude Opus 4.7 — разные thinking patterns; разделение помогает видеть, у кого какие шероховатости.

**Handoff identity в чат.** При сообщении о записи модель явно указывает свой runtime: `1self-learning [Claude Opus 4.7]: записал в <file>` или `1self-learning [GPT-5.5]: записал в <file>`. Файлы shared (один файл = одна тема, mixed runtime entries — норма), но **acting runtime** должен self-identify в handoff, чтобы пользователь видел кто именно только что записал без открытия файла. Обе SKILL.md (Claude + Codex) дублируют этот формат — это часть convention, не платформенная деталь.

**Length cap:** файл ≤ 50 строк.

## Cleanup

Пользователь вручную:

- Удаляет файлы, применённые в реальной инструкции / скиле / hook'е.
- Удаляет устаревшие observations.
- Промоутит pattern через `/remember`, `1user-truth`, `1instruction-layer`, или `1folder-contract`.

Агент **не** промоутит и **не** чистит. Только пишет.

## Boundary против соседей

| Слой | Owns | Скил |
|---|---|---|
| **Self-learning** (эта папка) | AI behavior meta-patterns: «модель спотыкается на X», «инструкция Y запутала», «skill Z не discoverable» | `1self-learning` пишет |
| `_ops/findings/**` | Проектные problems: «в коде / архитектуре / контенте есть вопрос с decision-trigger» | `1findings` |
| `_ops/criteria/*.md` | Durable user-backed правила | `1user-truth` |
| Memory `/remember` | Cross-project user preferences (durable taste, red lines) | manual |
