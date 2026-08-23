<!-- 1html-generated: shared visual explainer zone -->
# HTML Artifacts — Visual Explainer Zone

Работай как визуальный объяснитель, а не автор документа и не декоратор
страницы. Показывай отношения формой: вложенность — вложенностью, процесс —
flow, план — timeline, сравнение — рядом, величины — chart, состояние —
видимым interaction.

Жанр страницы — лучшая посадочная страница, не документация и не окно чата.
Держи золотой стандарт дизайна из своей памяти: мало текста, крупные заголовки,
креативные структуры — карточки, сетка, бенто. Несколько текстовых блоков
подряд на одной ступени — облик чата; плитка с абзацем внутри остаётся стеной
текста.

Нужно решить, какой visual carrier выбрать и как им показать материал → открой
skill `1html`; здесь остаётся только постоянная установка зоны.

Используй stereotype агента в пользу скорости: совпавшая component-анатомия и
state принадлежат DaisyUI; artifact владеет отношениями, bespoke-вложенностью,
chart/diagram/flow canvas, типографикой, ритмом и motion. Custom CSS компонует,
но не перерисовывает Daisy component под другим именем. Parent владеет
отношениями между частями, component — внутренним пространством, overlay — safe
area. Breakpoint меняет композицию, а не компенсирует ошибку общей геометрии.

Вся zone использует DaisyUI `cupcake`. Второй палитры нет: authored CSS, SVG и
visual runtimes берут Daisy semantic tokens либо `color-mix()` от них. На base
обычный foreground — `base-content`; meaningful data ink/lines используют
brand-content roles; status colors означают только реальные statuses.

Это одна shared zone для всех страниц:

- новая страница — `<slug>.html`, её стили — `assets/<slug>.css`;
- общие libraries уже лежат в `lib/`, components/styles/adapters — в
  `assets/shared/`;
- точные local tags носителей лежат в `COMPONENTS.md`; открывай только нужный;
- свои классы — ноль по дефолту: композицию сначала ищи в Daisy и классах
  раскладки зоны (`COMPONENTS.md`); свой класс существует только объявленным
  в плане страницы;
- подробности выбора visual и component лежат в skill `1html`; не дублируй их
  здесь;
- не создавай per-page bundle directory и не копируй `lib/assets`;
- соседние HTML, `_template.html` и `assets/_template.css` не являются design
  template; это только frozen neutral scaffold этой zone. Существующие страницы
  могли быть собраны до текущей планки — их облик не наследуется;
- обычная работа заканчивается готовой страницей, без audit, check и finish.

Страница обязана открываться через `file://` без сети, server и build step.
Существенный смысл оставляй в semantic HTML и не прячь только в цвет, hover,
canvas, JavaScript или motion.
