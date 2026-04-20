# Design Review Playbook

Как собирать визуальный и дизайн-аудит из уже установленных скиллов. Заменяет выпиленный плагин `design-auditor` (2026-04-17).

## Что Видно По Официальным Claude И Codex

Оба официальных корпуса полезны не только как примеры текста, но и как примеры **нарезки design-work на разные формы**.

- Anthropic design-skills чаще короткие и taste-led:
  - `frontend-design` — 42 строки, почти чистый aesthetic direction
  - `brand-guidelines` — 73 строки, отдельный brand/reference skill
  - `theme-factory` — 59 строк, отдельный theme-application toolkit
- OpenAI design-skills чаще делятся на две формы:
  - `frontend-skill` — 184 строки, medium aesthetic skill с defaults, hard rules и litmus checks
  - `figma-generate-design` / `figma-implement-design` — 341 / 258 строк, длинные procedural workflows с boundaries, prerequisites и required order

Общий паттерн у них один:
- не делать один общий “design skill на всё”
- отдельно держать art direction
- отдельно brand/theme application
- отдельно Figma / implementation workflow
- отдельно review / critique / signoff слой

Это важная опора для нашего design-layer: design work слишком широкий, чтобы один skill был одновременно и taste-engine, и browser-auditor, и Figma-writer, и review-router.

## Почему не отдельный скилл

Три «ортогональные линзы» (structure / craft / identity), которые пытался делать design-auditor, — это поверх уже существующих дисциплин:

- `my-skills:screenshot-design` — rigid, Visual Evidence Ledger, покрывает block logic, spacing, hierarchy, typography/color.
- `my-skills:playwright-skill` (mode 2) — алгоритмический аудит на живом URL: APCA contrast, spacing rhythm, visual weight, typographic hierarchy, reading order vs DOM.
- `impeccable:critique` — UX-оценка с AI Slop Detection, persona testing, двумя независимыми sub-agents.
- `impeccable:impeccable` — базовый каталог anti-patterns (источник AI slop правил).
- `impeccable:audit` — технический pass (a11y, perf, responsive).
- `impeccable:arrange / typeset / colorize / polish / distill / …` — узкие подходы под конкретный слой.
- `taste-skill:*` — эстетические mood-фреймы (minimalist, brutalist, stitch).

Старый `design-auditor` пытался сжать в один installed skill сразу несколько разных поверхностей:
- design review
- breadth across lenses
- browser evidence
- critique orchestration
- переход в remediation

Именно это и расходится с тем, как design-skills режут официальные Claude и Codex corpora. У них design-skill почти всегда силён **за счёт одной формы**, а не из-за “полного покрытия дизайна”.

Собственный плагин с тремя prose-агентами без ledger, без чисел и без каталога anti-patterns проигрывал каждому из них и почти не триггерился из-за приоритета `my-skills`.

## Карта «какую задачу чем закрывать»

| Входные данные | Что спрашивают | Чем покрывать |
|----------------|----------------|---------------|
| Один или несколько скриншотов | «разбери экран», «что не так», «audit design» | `screenshot-design` (rigid, мандатен по CLAUDE.md) |
| Живой URL | «дизайн аудит страницы», «проверь отступы и иерархию на сайте» | `playwright-skill` mode 2 **+** `screenshot-design` — числа идут в ledger как `Visible fact:` якоря |
| Любой визуал + «AI slop? / generic?» | «это шаблонно?», «нет личности» | `impeccable:critique` (AI Slop Detection под каталог `impeccable` base) |
| Живой URL, нужна техника | a11y, perf, responsive, контраст-числа | `impeccable:audit` или `playwright-skill` mode 2 |
| Живой URL, нужен пройденный flow | login, checkout, redirect, responsive sweep | `playwright-skill` mode 1 |
| Нужен адъюстмент конкретного слоя | «почини типографику / цвет / layout» | `impeccable:typeset / colorize / arrange / polish / distill` |
| Нужен mood / эстетический каркас | «сделай в бруталистском стиле», «минималистично» | `taste-skill:*` |
| Ad-hoc клик, один скриншот, один DOM-read | разовое действие в браузере | `browser_*` MCP напрямую (без playwright-skill) |

## Обязательные пары

Из глобального `~/.claude/CLAUDE.md`:

- **Screenshot + визуальный вопрос** → `screenshot-design` мандатен. Без ledger нельзя.
- **Алгоритмический аудит живого URL** → `playwright-skill` mode 2 (числа) **+** `screenshot-design` (judgement). Числа идут в ledger как `Visible fact:` якоря.

Эти два правила уже в CLAUDE.md — playbook на них опирается, не дублирует.

## Рекомендуемые комбо для типичных запросов

### «Мне нужен полный дизайн-аудит страницы»

Живой URL:
1. `playwright-skill` mode 2 — собрать числа: major-block extraction, spacing rhythm, visual weight, APCA contrast, typographic hierarchy.
2. Скриншот(ы) из шага 1.
3. `screenshot-design` на этих скриншотах — ledger, diagnosis, recommendations. Числа из шага 1 вкладываются в `Visible fact:` бюллеты.
4. Если нужен слой «точка зрения бренда / AI slop» поверх ledger — `impeccable:critique` отдельным проходом.

Только скриншоты (мок, конкурент):
1. `screenshot-design` — обязательно.
2. Поверх ledger — `impeccable:critique`, если запрос касается AI slop / distinctiveness.

### «Хочу независимое второе мнение»

Не делать параллельно 3 prose-агента. Вместо этого:
1. Первый проход — `screenshot-design` ledger + diagnosis.
2. Второй проход — `impeccable:critique`, он сам дispatchит двух независимых sub-agents (LLM Design Review + Persona). Каждый видит одни и те же пиксели, но с разным framing.
3. Оркестратор синтезирует: ledger, критик, persona. Противоречия разрешаются апелляцией к `Visible fact:` якорям ledger, не вкусом.

### «Нужен adversarial / слепой взгляд без якорей»

Редкий случай. Если хочется именно «что скажет критик, который не видит измерений» — дispatch'ить `impeccable:critique` без предварительного `screenshot-design` и без передачи чисел. Это опция, не дефолт.

### «Проверить быстро после CSS-правки»

Не запускать оркестрацию. Прямой путь:
- Живой dev-server → `browser_*` MCP напрямую, один screenshot, глазами.
- Один файл → `screenshot-design` только если правка действительно визуально значимая.

## Антипаттерны (не делать)

- Параллельный dispatch трёх и более независимых prose-агентов без ledger и без каталога anti-patterns на входе. Signal/noise падает, стоимость растёт, синтез тонет в вкусовщине.
- Re-запуск визуального анализа поверх уже сделанного ledger без передачи ledger во второй проход. Агенты переделывают пиксельный разбор, не зная, что уже было анкорено.
- Использовать `playwright-skill` mode 1 для одного клика или одного скриншота. Для ad-hoc — `browser_*` MCP напрямую.
- Триггерить дизайн-аудит на мелкую CSS-правку. Пересмотр 3+ скиллов для косметического чейнджа — cost/scale mismatch.
- Смешивать технический audit (`impeccable:audit`) с визуальным (`screenshot-design`) в одном проходе. Разные цели, разные артефакты.

## Если Снова Делать Отдельный Design-Skill

Только в одной из этих форм:

1. **Art-direction skill**
   Короткий или medium skill про visual thesis, mood, hierarchy, anti-slop и taste defaults.
   По форме ближе к Anthropic `frontend-design` или OpenAI `frontend-skill`.

2. **Brand/theme skill**
   Короткий reference/apply skill про palette, typography, style system или theme selection.
   По форме ближе к `brand-guidelines` или `theme-factory`.

3. **Figma / implementation workflow**
   Длинный procedural skill с prerequisites, boundaries, required workflow, validation.
   По форме ближе к `figma-generate-design` или `figma-implement-design`.

4. **Review/signoff layer**
   Обычно не heavy installed skill, а playbook или thin router над уже сильными узкими skills.
   Это текущая форма этого файла.

Не делать:
- один omnibus skill для generation + review + browser capture + Figma writes + breadth orchestration
- расплывчатый `description` уровня “helps with design tasks”
- prose-only reviewer без ledger, numbers или grounded catalogue

## Почему такой playbook сильнее выделенного скилла

- Каждый шаг опирается на существующую дисциплину (ledger / numbers / catalogue), не на прозу агента.
- Оркестратор явно решает композицию под задачу, а не пытается триггернуть общий «audit toolkit».
- Нет коллизии триггеров между my-skills, impeccable и сторонним design-auditor.
- Изменение одного из базовых скиллов (например, обновление anti-pattern каталога в `impeccable`) автоматически усиливает playbook, ничего не нужно пересинхронизировать.
- Эта форма ближе к реальной нарезке official corpora: review здесь остаётся composition layer, а не притворяется универсальным design super-skill.
