# Сколько инструкций удерживают frontier-модели 2026 года

> **Статус:** датированный evidence snapshot, 1 сентября 2026 года.
> **Окно моделей:** 1 марта — 1 сентября 2026 года.
> **Граница:** этот отчёт владеет сравнением свежих model × benchmark. Инженерные
> правила для `AGENTS.md`, skill и system prompt остаются в
> [`how-to-make-llm-obey.md`](how-to-make-llm-obey.md).

## Короткий ответ

У мощной модели нет одного числа «сколько инструкций она держит».

| Что одновременно требуется | Что показывают свежие измерения | Что считать рабочим ответом |
| --- | --- | --- |
| Разнотипные активные ограничения в одном ответе | В CSE strict all-pass падает ниже 50% при `k=7` у GPT‑5.5, `k=6` у Claude Opus 4.7 и `k=3` у GPT‑5.4 Pro и DeepSeek V4 Pro | **0–5** — рабочая зона для локальной проверки; **6–7** — зона перелома; **8+** нельзя считать надёжной конъюнкцией без декомпозиции или validator |
| Простые однотипные lexical requirements | В IFScale-2026 GPT‑5.5 сохраняет около 99% marginal accuracy до `N=5 000`; Gemini 3.1 Pro также держится до тысяч | Модель может выполнить **тысячи дешёвых однотипных условий**, но это не означает, что каждый ответ прошёл весь набор без единого пропуска |
| Простые verifier-rules со strict all-pass | Sonnet 5 в VeyraBench: 10 правил — 93.8%, 20 — 75.0%, 40 — 23.8%, 80 — 0% | Даже внутри простых правил цена быстро растёт, когда успех требует выполнить **все** |
| Реальная многошаговая работа по policy | В HANDBOOK.md лучший результат — 36.2% strict pass при среднем 12.7 критериев и примерно 30 tool calls | Для длинной агентной траектории безопасный числовой предел **не установлен** |

Итог для проектирования: **пять активных разнотипных обязательств — разумный
warning budget, двадцать — не доказанный надёжный предел**. Справочные факты,
маршруты к файлам и вся история сессии в этот бюджет механически не складываются.

## Почему свежие работы кажутся противоречивыми

Они считают разные единицы и используют разные условия успеха.

| Работа | Единица нагрузки | Метрика | Главная граница |
| --- | --- | --- | --- |
| [CSE](https://arxiv.org/html/2608.12426) | `k=1–12` совместимых constraints из 36 разнотипных классов | `mCSR` по отдельному constraint и `sCSR` — выполнены все | Сильнейшая проверка числа разнотипных active constraints; one-turn synthetic task, не память агента |
| [IFScale-2026](https://arize.com/blog/llm-instruction-following-benchmark-2026/) | `N` обязательных точных слов в одном business report | Доля включённых слов | Чистый тест масштабирования однотипного lexical inclusion; не peer-reviewed и не strict all-pass |
| [VeyraBench](https://arxiv.org/abs/2607.19257) | 10–160 преимущественно include/forbid rules | Perfect-response rate и per-rule adherence | Показывает, насколько atomicity меняет порог |
| [Instruction Stacking Collapse](https://arxiv.org/abs/2608.02639) | 1–20 verifier-checked instructions | Средний follow rate по инструкции | Находит pairwise conflicts; follow rate нельзя читать как вероятность идеального ответа |
| [ComplexConstraints](https://arxiv.org/abs/2606.09118) | 10–40 экспертных rubric criteria в реалистичном prompt | LLM-judged rubric pass | Реалистичнее synthetic rules, но не публикует count → quality curve |
| [HANDBOOK.md](https://arxiv.org/html/2607.25398) | Policy 20–124 страницы и programmatic criteria на длинной траектории | Strict pass: выполнены все действия и запреты | Ближе всего к работе агента в организации, но не изолирует число одновременно активных правил |

`IFScale` и CSE не опровергают друг друга. Требование «включи слово X» можно
закрыть один раз и больше не поддерживать. Точное число слов, совместимый JSON,
структура абзацев и логическая зависимость требуют непрерывного контроля и могут
мешать друг другу. Поэтому 5 000 lexical items и 7 heterogeneous constraints —
два ответа на два разных вопроса.

## Прямо измеренные новые модели

CSE — единственная найденная свежая работа, которая одновременно публикует
сопоставимую model panel, варьирует `k` и определяет half-life как первое `k`,
где strict all-pass падает ниже 50%.

| Модель | Релиз | `sCSR`, среднее по CSE | `mCSR` | Half-life `k*` |
| --- | --- | ---: | ---: | ---: |
| GPT‑5.5 | [23 апреля 2026](https://openai.com/index/introducing-gpt-5-5) | **64.2%** | **79.8%** | **7** |
| Claude Opus 4.7 | [16 апреля 2026](https://www.anthropic.com/research/claude-opus-4-7) | 49.6% | 67.0% | 6 |
| GPT‑5.4 Pro | [5 марта 2026](https://openai.com/index/introducing-gpt-5-4) | 23.2% | 35.6% | 3 |
| DeepSeek V4 Pro | [24 апреля 2026](https://api-docs.deepseek.com/news/news260424) | 22.4% | 22.4% | 3 |

В полной CSE panel также есть Gemini 3.1 Pro (`k*=4`), Gemini 3.1 Flash-Lite
(`k*=3`) и более старые модели. Табличные `sCSR` и `mCSR` выше — агрегаты по
всей CSE выборке, а `k*` — нужная нам точка пересечения 50%; смешивать эти три
столбца в одно «качество модели» нельзя.

### Что говорит кривая CSE

- CSE использует 4 527 probes, 36 constraint types, 15 моделей и 369 753
  deterministic checks.
- При `k=8` средний отдельный constraint выполняется примерно в 41% случаев, но
  все восемь одновременно — только в 5.7% ответов.
- Structural constraints теряют способность примерно вдвое быстрее lexical.
- Отказы в CSE почти независимы; слабое падение надёжности каждого constraint
  перемножается в резкий обвал strict all-pass.

Если вероятности выполнения отдельных правил равны `p_i`, то независимая
иллюстрация выглядит так:

```text
P(all pass) ≈ ∏ p_i
0.99^100 ≈ 36.6%
0.95^20  ≈ 35.8%
```

Это не универсальный закон: CSE находит остаточную связь через общие свойства
выхода, а Instruction Stacking Collapse — значимые попарные конфликты. Формула
нужна только для объяснения, почему высокий per-rule score совместим с низким
all-pass.

## Самый сильный контрпример пределу «20»

Свежие исследования дают для двадцати правил несовместимые на вид числа:

| Постановка | Модель | Результат при 20 |
| --- | --- | ---: |
| VeyraBench, преимущественно простые include/forbid rules, strict perfect response | Sonnet 5 | **75.0%** |
| Instruction Stacking Collapse, 24-типа rule pool, marginal follow rate | Sonnet 4.6 | **60.4%** |
| Та же работа | Gemini 2.5 Flash | 43.3% |
| Та же работа | GPT‑5-mini | 20.1% |

Число двадцать не является ни потолком памяти, ни безопасным production budget.
Оно описывает выбранный проектом уровень риска только после фиксации модели,
типа правил, траектории и strictness метрики.

## Что добавляет ComplexConstraints

[ComplexConstraints](https://surgehq.ai/blog/complexconstraints-a-benchmark-for-entangled-instruction-following)
состоит из 75 профессиональных prompts и 1 559 rubric criteria, обычно 10–40
на prompt. Условия бывают явными, неявными, условными, отрицательными,
планировочными и многошаговыми. Это хороший ответ на вопрос «справляется ли
модель с реальной сетью требований».

Но ComplexConstraints **не отвечает**, сколько инструкций помещается в модели:

- rubric criterion не равен независимой инструкции;
- критерии внутри prompt связаны и отличаются по стоимости;
- оценка сделана LLM judge, а не полностью детерминированными verifiers;
- опубликованной кривой `число критериев → качество` нет;
- leaderboard score ниже 40% у лучших моделей нельзя превратить в capacity
  threshold.

Поэтому исходный разговор о ComplexConstraints привёл к правильному вопросу,
но числовой ответ дают только более узкие CSE, IFScale и VeyraBench.

## Новейшие модели без прямой count-curve

Для текущего поколения проекта прямого matched measurement пока нет.

| Модель | Релиз | Что известно о числе инструкций |
| --- | --- | --- |
| GPT‑5.6 Sol / Terra / Luna | [9 июля 2026](https://openai.com/index/gpt-5-6/) | Публичной CSE/IFScale/Veyra count-curve не найдено |
| Claude Fable 5 / Mythos 5 | [9 июня 2026](https://www.anthropic.com/news/claude-fable-5-mythos-5) | Публичной сопоставимой count-curve не найдено |
| Claude Opus 5 | [24 июля 2026](https://www.anthropic.com/research/claude-opus-5) | Публичной сопоставимой count-curve не найдено |

Context window, coding score, GDPval и vendor-фраза «лучше следует сложным
инструкциям» не заменяют этот пробел. Переносить `k*=7` GPT‑5.5 на GPT‑5.6 или
`k*=6` Opus 4.7 на Opus 5 нельзя.

## Что считать инструкцией в агентном проекте

```text
факт:    доступ → извлечение → применить один раз
правило: доступ → распознать применимость → удержать → применить → проверить
маршрут: обнаружить → выбрать источник → доставить нужное правило
policy:  правило + порядок + исключения + состояние на многих шагах
```

Сотни строк спецификаций не означают сотни одновременно активных обязательств.
Большая часть материала — пассивные факты и потенциальные ветки. Нагрузкой
становится рабочее множество, которое агент должен извлечь и поддерживать в
конкретной точке траектории.

Обратное тоже неверно: большое context window не гарантирует, что нужное
правило будет найдено, признано применимым и выполнено через 30 tool calls.
HANDBOOK.md показывает именно этот разрыв: лучший Claude Fable 5 получил 36.2%
strict pass на 65 длинных задачах со средним 12.7 programmatic criteria, хотя
policy-документы физически находились в контексте.

## Практический контракт до собственного замера

| Активные разнотипные обязательства в одной точке действия | Решение |
| ---: | --- |
| 0–5 | Допустимый стартовый budget; всё равно измерять per-rule и strict all-pass на целевой модели |
| 6–7 | Transition band: разбить по стадиям, доставить ближе к действию или добавить executable check |
| 8+ | Не обещать надёжный all-pass только текстом; декомпозировать, маршрутизировать и валидировать |

Инварианты, нарушение которых недопустимо, не должны зависеть от этого budget:
их закрывают permission, schema, validator, hook, test или другой наблюдаемый
gate. Текст оставляют для предпочтений, выбора и контекста, где редкая ошибка
допустима и исправима.

## Чего пока не знает наука

Нет benchmark, который одновременно варьирует:

- число активных constraints;
- объём пассивных фактов;
- routing между system prompt, project files, skills и tools;
- длину tool-using trajectory;
- strict execution-grounded all-pass;
- GPT‑5.6, Claude Fable 5 и Claude Opus 5 в одной matched panel.

До такого измерения честный ответ — диапазон для конкретной поверхности, а не
число «инструкций в памяти».

## Источники

### Прямые измерения 2026 года

- [Large Language Models Can Follow Instructions, But Not Many at Once / CSE](https://arxiv.org/html/2608.12426) — preprint, 12 августа 2026; основной count benchmark.
- [Models got an order of magnitude better at following instructions in one year / IFScale-2026](https://arize.com/blog/llm-instruction-following-benchmark-2026/) — независимая vendor replication, 12 мая 2026; не peer-reviewed.
- [Prompt Design at Scale / VeyraBench](https://arxiv.org/abs/2607.19257) — solo preprint, 21 июля 2026.
- [Instruction Stacking Collapse](https://arxiv.org/abs/2608.02639) — preprint, 31 июля 2026.
- [ComplexConstraints and Beyond](https://arxiv.org/abs/2606.09118) и [primary release](https://surgehq.ai/blog/complexconstraints-a-benchmark-for-entangled-instruction-following) — preprint / GEM at ACL 2026 workshop и релиз benchmark.
- [HANDBOOK.md](https://arxiv.org/html/2607.25398) — preprint, 28 июля 2026; long-context agentic policy adherence.
- [Harness-IF](https://arxiv.org/abs/2608.11727) — preprint, 12 августа 2026; operational rules across five instruction surfaces.

### Owner evidence

- Исходный вопрос и коррекция слишком грубого вывода из ComplexConstraints:
  [`2026-08-28-190000-codex-01a048d4.md`](../_ops/chat-recall/2026-08-28-190000-codex-01a048d4.md).
- Решение обновить исследование по моделям последних шести месяцев:
  [`2026-09-01-235006-codex-01a05e4c.md`](../_ops/chat-recall/2026-09-01-235006-codex-01a05e4c.md).
