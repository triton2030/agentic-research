<!-- 1html-generated: shared visual explainer zone -->
# HTML Artifacts — Visual Explainer Zone

Что здесь правда об этой папке. Как думать про дизайн и объяснение — в skill
`1html`; здесь это не дублируется.

Тема — DaisyUI `bumblebee`, вторая палитра не заводится. Tailwind, Alpine и
Lucide уже подключены; Table, Mermaid, ECharts и React Flow лежат в `lib/` и
`assets/shared/`. Точные теги, роли поверхностей и классы раскладки —
в `COMPONENTS.md`, открывай его перед первой разметкой.

Страница обязана открываться по `file://` без сети, CDN, установки, сервера и
сборки.

- новая страница — `<slug>.html`, её стили — `assets/<slug>.css`;
- общий слой `assets/shared/components.css` владеет начертанием заголовков,
  шкалой, ролями поверхностей и раскладкой; размеры и композицию выбирает
  страница;
- per-page bundle directory не создавай и `lib/assets` не копируй;
- удалил или переименовал HTML руками — пересобери каталог скриптом скила;
- соседние HTML, `_template.html` и `assets/_template.css` — не образец облика:
  они могли быть собраны до текущей планки;
- обычная работа заканчивается готовой страницей, без audit, check и finish.
