---
эпик: "[[../../GOAL#Definition of done]]"
kind: task
---

# 1html — design-free visual explainer

## Цель

Установить tracked/global `1html`, который помогает свежей сессии превращать
сложный материал в автономный `file://` visual explainer без обязательной
композиции, палитры или структуры нод. Задача напрямую служит Definition of
done в `../../GOAL.md`: живой skill должен восстановить owner-маршрут и
изменить первое действие новой сессии.

Проект не ведёт карту эпиков; поэтому контракт честно привязан к существующему
GOAL, а не создаёт фиктивный epic-owner ради формы.

## Критерии успеха

- Fresh bundle — нейтральный технический scaffold; artifact владеет HTML, CSS,
  JS, layout, palette, typography и motion.
- Blocking gate ловит только переносимость, integrity, semantic shell и wiring;
  произвольные first-party design и React Flow node composition проходят.
- Skill ведёт от реального отношения к простейшему visual carrier; независимый
  агент показывает plan как timeline, system как flow, вложенность формой.
- Mermaid, React Flow и data-viz runtime локальны, opt-in, работают через
  `file://`; каждый helper имеет редактируемый contract/example и falsifiers.
- React Flow node может быть icon-only, text-only или произвольным HTML с любым
  количеством controls/disclosures; adapter не задаёт ей card anatomy.
- Указанный WhatsApp artifact сохраняет тёплый editorial фон и serif headings,
  не имеет anchor rail; header имеет padding, border и radius и проходит legacy
  contract.
- Final exact candidate проходит source/browser acceptance, независимые
  architecture/developer audits и новый Opus review; замечания устранены.
- Tracked Claude owner и Codex projection синхронизированы; `qv-skill`, hashes,
  tests и git push подтверждены.

## Не входит

- Production site/app, deploy, сервер или runtime network.
- Обязательная chart/flow библиотека в scaffold.
- Выдуманные данные ради эффектного chart.
- Миграция visual language старых bundles или обновление библиотек, не
  обслуживающее доказанный текущий carrier.
- Шаблонный каталог node/cards/examples, который будущий агент копирует как
  дизайн по умолчанию.

## Происхождение требований

| Требование | Источник |
|---|---|
| Исполняемые проверки вместо дополнительной прозы | владелец: `../../chat-recall/2026-08-19-212344-codex-01a01ad4.md:25-27` |
| Полный stress-test и реальный artifact | владелец: тот же owner evidence `:29-31` |
| Свобода дизайна без обязательных templates | владелец: `:32-33` |
| Show, don't tell; charts, flow, timeline, disclosure, modern HTML/CSS | владелец: `:36` |
| React Flow offline, palette-aware, arbitrary node contents | владелец: `:34-39` |
| Мощная data-viz capability с examples | владелец: `:40` |
| Переносимый план и финальный Opus gate | владелец: `:38,41` |
| Сохранить старый стиль WhatsApp artifact | владелец: `:42` |
| Evidence меняет решение, а не подтверждает чтение | Product Principles P-004, P-005 |
| Один semantic owner, без параллельной правды | Product Principles P-007, P-008 |

## Условия входа

Имеет смысл, пока `1html` остаётся глобальным skill для автономных локальных
HTML-explainers, а artifacts обязаны открываться без server/network. Изменение
одного из этих условий — stop и пересборка через owner evidence.

## Режим

Execution. Ось разреза — цепочка потребителей: semantic contract → автономные
visual carriers → browser proof → independent acceptance → global handoff.

| Веха | Наблюдаемый выход | Проверка |
|---|---|---|
| 1. Design-free base | scaffold/gate не владеют visual composition | contract harness + два разных fresh artifacts |
| 2. React Flow freedom | arbitrary node DOM/size/design; offline interactions | source tests + desktop/mobile `file://` browser proof |
| 3. Data visualization | один сильный local runtime + разные data examples | helper idempotence + charts render offline + no network/errors |
| 4. Acceptance | exact candidate без material findings | skill audits + final fresh Opus review + repaired rerun |
| 5. Handoff | Claude/Codex/live artifact/git согласованы | projection hashes + `qv-skill` + finish + commit/push |

## Стыки

- Веха 1 → 2/3: checker не отклоняет artifact-owned composition.
- Вехи 2/3 → 4: reviewer получает exact candidate и browser evidence, а не
  самоотчёт исполнителя.
- Веха 4 → 5: только candidate без открытого material finding становится
  источником обеих projections.
- Веха 5 → будущий пользователь: fresh invocation выбирает carrier по смыслу,
  запускает один `finish` и получает автономный artifact/catalog link.
