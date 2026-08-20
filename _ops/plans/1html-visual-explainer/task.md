---
эпик: "[[../../GOAL#Definition of done]]"
kind: task
---

# 1html — shared visual explainer zone

## Цель

Установить tracked/global `1html`, который создаёт одну общую
`_workspace/HTML_artifacts/` zone: folder instruction, shared components,
styles, libraries и adapters лежат один раз, а множество flat HTML-файлов их
переиспользуют. Агент сразу строит design-free `file://` visual explainer без
обязательного audit/check/finish пути.

Проект не ведёт карту эпиков; поэтому контракт честно привязан к существующему
GOAL, а не создаёт фиктивный epic-owner ради формы.

## Критерии успеха

- Fresh zone содержит одну общую копию local runtimes и одну folder-level
  stance; новая страница — `<slug>.html` + `assets/<slug>.css`, не bundle-dir.
- Одна creation command создаёт страницу, обновляет generated shared layer и
  каталог; не печатает и не требует QA-команд.
- Skill ведёт от реального отношения к простейшему visual carrier; независимый
  агент показывает plan как timeline, system как flow, вложенность формой.
- Mermaid, React Flow и data-viz runtime уже лежат в shared zone, работают
  через `file://`; страница подключает только нужные tags без installer command.
- React Flow node может быть icon-only, text-only или произвольным HTML с любым
  количеством controls/disclosures; adapter не задаёт ей card anatomy.
- Указанный WhatsApp artifact сохраняет тёплый editorial фон и serif headings,
  но переезжает в ту же flat/shared zone без своей копии runtime.
- Final exact candidate проходит package-owner acceptance и независимый audit;
  ordinary artifact creation не наследует этот QA-loop.
- Tracked Claude owner и Codex projection синхронизированы; `qv-skill`, package
  smoke и git push подтверждены.

## Не входит

- Production site/app, deploy, сервер или runtime network.
- Повторные копии libraries/styles/components на каждый HTML.
- Выдуманные данные ради эффектного chart.
- Миграция visual language старых страниц или обновление библиотек, не
  обслуживающее доказанный текущий carrier.
- Шаблонный каталог node/cards/examples, который будущий агент копирует как
  дизайн по умолчанию.

## Происхождение требований

| Требование | Источник |
|---|---|
| Старые checks-first требования сняты из runtime | поздняя коррекция владельца в `../../chat-recall/2026-08-19-212344-codex-01a01ad4.md` |
| Свобода дизайна без обязательных templates | владелец: `:32-33` |
| Show, don't tell; charts, flow, timeline, disclosure, modern HTML/CSS | владелец: `:36` |
| React Flow offline, palette-aware, arbitrary node contents | владелец: `:34-39` |
| Мощная data-viz capability с examples | владелец: `:40` |
| Переносимый план и финальный Opus gate | владелец: `:38,41` |
| Сохранить старый стиль WhatsApp artifact | владелец: `:42` |
| Одна shared HTML_artifacts zone для множества HTML | владелец: `:45-46` |
| Evidence меняет решение, а не подтверждает чтение | Product Principles P-004, P-005 |
| Один semantic owner, без параллельной правды | Product Principles P-007, P-008 |

## Условия входа

Имеет смысл, пока `1html` остаётся глобальным skill для автономных локальных
HTML-explainers, а artifacts обязаны открываться без server/network. Изменение
одного из этих условий — stop и пересборка через owner evidence.

## Режим

Execution. Ось разреза — shared zone → flat page creation → catalog → global
skill projections.

| Веха | Наблюдаемый выход | Проверка |
|---|---|---|
| 1. Shared zone | одна instruction/assets/lib zone, без per-page copies | fresh project tree + second-page reuse |
| 2. Fast page | одна command создаёт `<slug>.html` и catalog entry | source-owned smoke; no QA command in output |
| 3. Visual carriers | shared Table/Mermaid/ECharts/React Flow paths + examples | references/path smoke; no installer commands |
| 4. Acceptance | exact candidate без material findings | skill audits + package-owner smoke |
| 5. Handoff | Claude/Codex/current zone/git согласованы | projection diff + `qv-skill` + commit/push |

## Стыки

- Веха 1 → 2/3: страница знает только shared relative paths; сборка runtimes
  и folder instruction скрыта за creation command.
- Вехи 2/3 → 4: reviewer получает exact candidate и package smoke, а не
  самоотчёт исполнителя.
- Веха 4 → 5: только candidate без открытого material finding становится
  источником обеих projections.
- Веха 5 → будущий пользователь: fresh invocation выбирает carrier по смыслу
  и получает artifact/catalog link сразу после creation command.
- Веха 5 → `mavo-short2`: текущая WhatsApp-страница живёт рядом с каталогом,
  сохраняет собственный CSS и использует тот же shared `lib/assets`.
