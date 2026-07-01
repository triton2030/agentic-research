# Design Review Playbook

Короткий маршрут для визуального и дизайн-аудита через уже установленные скиллы.
Заменяет удалённый `design-auditor` (2026-04-17) и не является отдельным live
skill.

## Принцип

Не собирать один общий `design skill` на всё. Дизайн-работа делится на разные
поверхности:

- визуальный разбор скриншота;
- факты живой страницы;
- вкус, уникальность и `AI slop`;
- бренд или настроение, если выбран отдельный reference;
- Figma / implementation workflow, если это отдельная задача.

Официальные design-skills обычно сильны одной формой: aesthetic direction,
brand/theme, Figma workflow или review router. Старый `design-auditor` смешивал
review, browser evidence, несколько линз и remediation, поэтому проигрывал более
узким скиллам.

## Быстрый Выбор

- Скриншот + визуальный вопрос: `1screenshot-design`; full pass только для
  полноценной critique, comparison или high-risk polish.
- Живой URL + визуальный verdict: browser/verification для фактов, затем
  `1screenshot-design`.
- Живой URL + техника: browser/verification для responsive,
  console/layout issues, a11y, perf и contrast.
- «Шаблонно», «нет личности», `AI slop`: `1impeccable`.
- Починить типографику, цвет, layout, polish: `1impeccable` с конкретным
  reference.
- Один клик, один скриншот, один DOM-read: browser/verification tool напрямую.
- Нужно несколько независимых ролей или свежих окон: только по явному запросу
  через `1fresh-eyes`.

## Типовые Маршруты

### Полный дизайн-аудит живой страницы

1. Собрать только факты, которые меняют вывод: скриншот, responsive state,
   очевидные console/layout issues, contrast или a11y numbers при необходимости.
2. Отдать скриншоты в `1screenshot-design`.
3. Добавить `1impeccable` только если нужен слой вкуса, бренда, уникальности или
   `AI slop`.

### Только скриншоты

1. `1screenshot-design`.
2. `1impeccable`, если вопрос про шаблонность, настроение или distinctiveness.

### Независимое второе мнение

Не запускать три prose-агента по умолчанию.

1. Первый проход: `1screenshot-design` с evidence anchors.
2. Второй слой: `1impeccable`, если нужна distinctiveness / `AI slop` critique.
3. Несколько субагентов: только когда пользователь явно просит свежие глаза,
   совет ролей или многокритериальный разбор через `1fresh-eyes`.

### Слепой вкусовой взгляд

Редкий режим. Если нужен критик без измерений и предварительных якорей, начать с
`1impeccable` blind taste / `AI slop` lens. Это опция, не дефолт.

### Быстрая проверка после CSS-правки

- Живой dev-server: browser/verification tool напрямую и один скриншот глазами.
- `1screenshot-design` подключать только если правка визуально значимая.

## Не Делать

- Параллельно запускать три и больше prose-агентов без ledger, чисел или
  каталога anti-patterns.
- Повторно гонять визуальный анализ без передачи уже собранного ledger.
- Запускать тяжёлый browser audit ради одного клика или одного скриншота.
- Триггерить полный дизайн-аудит на мелкую CSS-правку.
- Смешивать технический audit и визуальный judgement в одном проходе.

## Если Снова Делать Отдельный Design-Skill

Выбрать одну форму:

1. Art-direction skill: visual thesis, mood, hierarchy, anti-slop, taste defaults.
2. Brand/theme skill: palette, typography, style system, theme application.
3. Figma / implementation workflow: prerequisites, boundaries, required order,
   validation.
4. Review/signoff layer: тонкий router над уже сильными узкими скиллами.

Не делать omnibus skill для generation + review + browser capture + Figma writes
и breadth orchestration. Если guide начинает пересказывать live `SKILL.md`,
оставить принцип или ссылку на owner.
