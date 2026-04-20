# Smoke Tests

Результаты прогонов `criteria-generator` на трёх типах задач. Дата: 2026-04-16. Каждый тест выполнен в свежем subagent-контексте без знания о плане. Гейт EVPI вручную переключён на режим «записывать вопросы как `[EVPI-would-ask]` Assumption вместо интерактива» для неинтерактивности тестов.

Полные цитаты вывода скиллов хранятся в логах tasks: `/private/tmp/claude-501/-Users-triton-Documents-GitHub-agentic-research/7064ef3d-85a7-40c5-b478-13f2d05413a9/tasks/`.

## Test A — Ambiguous code task

Вход: `добавь логирование ошибок в бэкенд`.

| Критерий | Результат |
|---|---|
| Template compliance | pass |
| Evidence on every Must | pass (5 Must, все с grep/curl/pytest) |
| Must-not substantive | pass (5 items, в т.ч. security-утечка секретов в логах) |
| EVPI gate handled | pass (5/5 вопросов в Assumptions) |

**Ключевое:** Discovery нашёл, что CWD не содержит backend-кода. Все 5 неизвестных ушли в EVPI. Adversarial pass дал 3 усиленных критерия: уникальность request_id на запрос, расширение запрета на `sys.stdout`, запрет на логирование `request.body`/`Authorization`/`password`.

## Test B — Research task

Вход: `собери обзор self-healing CI систем за 2026`.

| Критерий | Результат |
|---|---|
| Template compliance | pass |
| Evidence on every Must | pass (7 Must) |
| Must-not includes "no pre-2026 material" | pass |
| EVPI gate handled | pass (2/2 → Assumptions, 3 unknowns разрешены из AGENTS.md + CLAUDE.md) |

**Ключевое:** Discovery сработал как задумано — AGENTS.md разрешил неизвестность о хранилище (нельзя создавать новые файлы в `_research/`), CLAUDE.md закрыл вопрос языка (русский). Это сократило EVPI-вопросы с 5 до 2. Adversarial pass поймал 6 bypass'ов, в т.ч. «дата из copyright footer», «выдуманные URL», «синтез ≠ перечисление инструментов», «CD/MLOps маскируется под CI».

## Test C — Trivial task

Вход: `поправь опечатку в README`.

| Критерий | Результат |
|---|---|
| Template compliance | pass |
| Output minimal for trivial task | pass (3 Must, 2 Must-not) |
| EVPI gate handled | pass (2/2 → Assumptions) |

**Ключевое:** Задача формально попадает в «When NOT to use». В тесте скилл был явно принуждён к выполнению — и даже на тривиальной задаче Discovery принёс пользу: в репозитории нет root-level README, но есть 5 кандидатов. Это превратило «какой README» из тривиального уточнения в настоящий блокер. В продакшне скилл должен self-decline — при следующем запуске стоит проверить этот поведенческий путь.

## Выводы

- Все три теста прошли все оси проверки. Скилл производит вывод в заданном шаблоне, Evidence присутствует у каждого Must, adversarial pass генерирует осмысленные bypass'ы.
- Discovery реально используется (не декоративный шаг): в B он закрыл 3 из 5 unknowns через CLAUDE.md + AGENTS.md; в A честно показал, что backend-контекста нет; в C нашёл структурное несоответствие (нет root README).
- EVPI gate корректно выделяет вопросы, которые стоит задавать, от тех, что разрешимы из контекста.
- Нет regression'ов на шаблоне: формат output стабилен между очень разными типами задач (код, ресёрч, тривиал).

## Наблюдения для будущих правок

- Test C показал, что скилл не самоотклонил тривиальную задачу — тест override это и просил, но в регулярном использовании стоит убедиться, что «When NOT to use» реально срабатывает без override.
- В Test A assumption-блок получился длинным (5 пунктов). В EVPI-режиме это приемлемо, но стоит проверить, не раздувает ли это итоговый промпт сверх необходимого.
- Все Must в Test B привязаны к конкретному файлу `_research/links-knowledge.md`. Discovery корректно вытащил правило из AGENTS.md, но в проектах без такой жёсткой конвенции этот пункт не возникнет.
