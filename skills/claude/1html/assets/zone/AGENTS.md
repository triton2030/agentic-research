<!-- 1html-generated: shared visual explainer zone -->
# HTML Artifacts — Visual Explainer Zone

Работай как визуальный объяснитель, а не автор документа и не декоратор
страницы. Показывай отношения формой: вложенность — вложенностью, процесс —
flow, план — timeline, сравнение — рядом, величины — chart, состояние —
видимым interaction.

Нужно решить, какой visual carrier выбрать и как им показать материал → открой
skill `1html`; здесь остаётся только постоянная установка зоны.

Композиция важнее компонентов. Parent владеет отношениями между частями,
component — внутренним пространством, overlay — safe area. Breakpoint меняет
композицию, а не компенсирует ошибку общей геометрии.

Это одна shared zone для всех страниц:

- новая страница — `<slug>.html`, её стили — `assets/<slug>.css`;
- общие libraries уже лежат в `lib/`, components/styles/adapters — в
  `assets/shared/`;
- точные local tags носителей лежат в `COMPONENTS.md`; открывай только нужный;
- не создавай per-page bundle directory и не копируй `lib/assets`;
- соседние HTML, `_template.html` и `assets/_template.css` не являются design
  template; это только frozen neutral scaffold этой zone;
- обычная работа заканчивается готовой страницей, без audit/check/finish;
- явный технический check — advisory `check_html.mjs` из скила `1html`: только
  runtime, local files, сеть и горизонтальная прокрутка страницы; не visual audit.

Страница обязана открываться через `file://` без сети, server и build step.
Существенный смысл оставляй в semantic HTML и не прячь только в цвет, hover,
canvas, JavaScript или motion.
