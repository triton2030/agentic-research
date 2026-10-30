# Промпты по случаям

Общие правила промпта — в теле скила. Здесь то, чем случай отличается, и
пример. Пример с пометкой «проверен» прогнан 2026-10-30 и дал описанный
результат; остальные собраны по правилам OpenAI и практиков — это образцы
формы, а не гарантия.

Другие жанры — фото, игровые ассеты, вайрфреймы, логотипы — есть в
образцах OpenAI: `~/.codex/skills/.system/imagegen/references/sample-prompts.md`.
Бери оттуда форму промпта; замечания о моделях и параметрах там устарели.

## Иллюстрация или фото с нуля

Стиль задают медиум, свет и палитра конкретными словами: «flat editorial
illustration with subtle paper grain», «soft early-morning light from the
window», цвета по именам или hex. Оценки вроде «stunning» стиля не задают.
Для фотореализма — прямо «photorealistic» и фактура: поры, ткань, износ.
Место под текст страницы называй долей кадра.

Модель сама наполняет сцену предметами. Когда кадр должен быть пустым,
перечисли, что в нём есть, и добавь «nothing else in the scene».

Проверен: Sunburst `medium` 1536×1024 — композиция и палитра совпали, модель
добавила растения, полку и вид за окном.

```text
Use case: illustration-story
Asset type: hero illustration for a blog post about slow mornings, wide banner
Primary request: a person reading a paper book at a small kitchen table by a window, a cup of tea steaming, a cat asleep on the windowsill
Style/medium: flat editorial vector-like illustration with subtle paper grain, simple geometric shapes, no outlines
Composition/framing: wide shot, subject on the right third, calm empty wall on the left for the post title
Lighting/mood: soft early-morning light from the window, quiet and unhurried
Color palette: muted sage green, warm cream, terracotta accents
Constraints: no text, no logos, no watermark
```

## Макет интерфейса

Модель рисует интерфейс точно, когда перечислено всё, что на экране: каждый
блок, их число и каждая подпись. Сначала структура — платформа, раскладка,
тексты, — потом стиль. Стиль задают токены дизайна: шрифт, сетка, hex-цвета,
радиусы. Описывай экран как выпущенный продукт, без языка концепт-арта. Рамку
устройства, стол и руки модель добавляет, если не сказать «flat full-bleed
screenshot, no device frame».

Экран существующего продукта рисуй по скриншоту его текущей страницы:
подкоманда `edit`, скриншот — образец стиля, дальше как в следующем разделе.
Словами стиль живого продукта не передать.

Знакомый жанр можно назвать коротко — «экран настроек iOS» модель знает
сама. Длинная спецификация нужна, когда содержание новое или должно совпасть.

Проверен: Sunburst `medium` 1536×1024 — весь текст верен, нижняя четверть
экрана пуста; тот же промпт на `xhigh` 1920×1088 заполнил экран. Экран
настроек на русском, 14 подписей, — все буквы верны, включая «ё».

```text
Use case: ui-mockup
Asset type: high-fidelity desktop web app screen for design review before coding
Primary request: a dashboard screen of a personal finance app called "Ledgerly"
Composition/framing: flat full-bleed screenshot of the browser viewport only, 1536x1024, no device frame, no desk, no hands, no perspective
Layout: left sidebar 240px with logo "Ledgerly" and nav items "Overview", "Accounts", "Budgets", "Reports", "Settings" ("Overview" active); top bar with page title "Overview" and a search field with placeholder "Search transactions"; main area: row of three KPI cards — "Balance $12,480.32", "Spent this month $2,914.07", "Saved 18%"; below a line chart titled "Cash flow, last 6 months" with month labels "May Jun Jul Aug Sep Oct"; right column card "Recent transactions" with four rows: "Blue Bottle Coffee −$6.50", "Salary +$4,200.00", "Netflix −$15.49", "Whole Foods −$84.12"
Style/medium: clean modern SaaS UI, Inter-like sans-serif, 8px spacing grid, light theme, white cards with 1px #E5E7EB borders and 12px radius, single accent color #4F46E5
Text (verbatim): render every label exactly as quoted above, no extra words, no lorem ipsum
Constraints: crisp legible text at 100% zoom; consistent alignment; no watermark
```

## Следующий экран той же системы

Одобренный экран или скриншот живой страницы становится образцом: он — Image
1 в `edit`, а промпт говорит, что его не правят, а рисуют новый экран той же
системы. Мобильную версию даёт тот же образец с размером `1024x1536`.
Несколько экранов потока можно просить на одном холсте; практики пишут, что
больше четырёх расходятся по стилю.

Проверен: и Sunburst, и `gpt-image-2` сохранили сайдбар, шрифт, карточки и
иконки, весь текст верен.

```text
Image 1 is a style reference only: a screen of the "Ledgerly" web app. Do not edit it; design a NEW screen of the same app.
Keep from Image 1 exactly: sidebar (logo, nav items, widths), top bar, typography, colors, card style, spacing, icon style, light theme.
New screen: "Budgets" page ("Budgets" active in the sidebar, page title "Budgets"). Main area: a 2x2 grid of budget cards, each with a category name, a horizontal progress bar and "spent / limit" text: "Groceries $412 / $600", "Dining out $198 / $250", "Transport $96 / $150", "Entertainment $143 / $120" (this one over limit, progress bar red). Above the grid a primary button "New budget" on the right.
Text (verbatim): render every label exactly as quoted, no extra words.
Flat full-bleed viewport screenshot, no device frame.
```

## Правка готовой картинки

Список того, что уцелеет, включает и прежние правки: иначе следующая правка
откатывает предыдущую.

Правки накапливают дрейф: у Sunburst с фразой «keep everything else the same»
в каждой правке фон заметно поплыл к одиннадцатой (тест Morphed, 2026-10-07).
Поэтому правь от последней одобренной версии, а не от последнего результата.
Когда список уцелевшего длиннее самого изменения или правка перестала
ложиться, сделай один сводный промпт от оригинала.

Маска (`--mask`, PNG с альфой размера первой картинки) указывает область, но
не запирает её: модель меняет и соседнее. Оставь зазор между областью и тем,
что двигаться не должно. Если пиксели вне правки обязаны остаться прежними,
вклей оригинал поверх результата локально.

```text
Image 1: product photo of a living room — the edit target.
Change only the sofa: replace the grey fabric sofa with a cognac leather sofa of the same size and position.
Keep unchanged: camera angle, framing, room lighting and shadows on the floor, the rug, the plant, the wall art, the window.
No new objects, no text.
```

## Референсы

Рядом с номером называй содержание: «Image 2 (the brown dog)» — практики
расходятся в том, держит ли модель порядок картинок. Маска всегда относится
к первой. Проси правку первой картинки, а не «смешай»: «add the dog from
Image 2 into Image 1».

- Позу и выражение называй явно: иначе персонаж приносит из образца наклон
  головы и пустой взгляд.
- Чего образцы не показывали, модель придумает. Лечит ещё один образец,
  а не длиннее промпт.
- Образец стиля переносит и элементы композиции. В пробе стилевой образец
  с круглыми плашками у иконок дал иконке плашку, хотя промпт её запрещал.

Проверен: Flare `low`, перенос стиля, прозрачный фон.

```text
Image 1 is a style reference (color palette and rounded flat icon style). Image 2 is the subject.
Redraw the apple from Image 2 as a flat app icon in the visual style of Image 1.
Isolated icon on a fully transparent background, no tile, no shadow, no checkerboard.
```

## Удаление фона и прозрачный ассет

Модель не вырезает объект, а рисует его заново: форма и окраска совпадают,
мелкая фактура — нет. Поэтому путь выбирают по тому, что дано и что важно:

| Случай | Путь |
|---|---|
| плоская графика на ровном фоне: логотип, иконка, ассет с точными цветами | без модели: `uv run -q --with pillow python -I ~/.codex/skills/.system/imagegen/scripts/remove_chroma_key.py --input IN.png --out OUT.png --auto-key border` — бесплатно, пиксели те же; цвет фона не должен встречаться в объекте, иначе станет дырой |
| фото — и на студийном фоне тоже: у фото фон не ровный, а с тенями и градиентом | правка моделью 2.5 с `--background transparent`; до вызова скажи владельцу, что объект будет перерисован |
| новый объект, волосы, мех, пух | генерация моделью 2.5 с `--background transparent` — лучший край в замерах практиков |
| стекло, прозрачная бутылка | ни один путь не вырезает чисто: генерируй сразу на итоговом фоне |
| нужен именно `gpt-image-2` | сплошной `#00ff00` или `#ff00ff`, которого нет в объекте, затем тот же `remove_chroma_key.py` через `uv` |

Параметр без слов промпта не работает: промпт сильнее параметра, и описанная
сцена съедает прозрачность. Слова «isolated product shot» в пробе оставили
под яблоком полупрозрачную белую тень — тень запрещай прямо.

Хвост промпта для новой картинки:

```text
Isolated subject on a fully transparent background, full object visible with generous padding. No backdrop, no scenery, no rectangle, no plinth, no checkerboard, no cast shadow, no reflection.
```

Проверен: Flare и Sunburst убрали фон у готового фото без тени; яблоко
перерисовано, фактура кожуры отличается.

```text
Remove the background completely. Keep the apple exactly as is: same shape, colors, stem, highlights. No shadow, no ground, no reflection. Output the apple alone on a fully transparent background.
```

В следующих правках прозрачного ассета повторяй «preserve the transparent
background».

## Текст, плакат, инфографика, слайд

- Закрой надписи фразой «Render every line verbatim, no extra characters, no
  other text anywhere in the frame». Редкое слово — по буквам. Сколько раз
  надпись появляется, скажи числом.
- Язык надписей назови прямо: «all text in Russian».
- Мелкий и плотный текст — `high` и выше. Блок длиннее ста слов начинает
  путать буквы в последних строках.
- Точный график или карта — в коде: модель выдумывает точки и искажает
  длину столбцов. Картинке достаются иллюстративные графики, и цифры в
  промпт — настоящие.
- Шум и лишняя фактура в инфографике: «clean flat regions, restrained
  background detail, minimal texture».

```text
Use case: ads-marketing
Asset type: vertical event poster, 1024x1536
Primary request: poster for a jazz evening in a small bookshop
Layout: top third — headline "Тихий джаз" in a heavy condensed serif, largest element; middle — illustration of a double bass leaning on a bookshelf, warm lamp light; bottom band — "Пятница, 14 ноября · 19:00" and below it "Книжная лавка «Переплёт»"
Text (verbatim): all text in Russian, each line exactly as quoted and exactly once, no extra characters, no other text anywhere in the frame
Style/medium: risograph print look, two inks — deep blue and warm orange on cream paper
```

## Предмет и логотип

Без оговорки модель «улучшает» товар: упрощает крышку, переписывает
этикетку. Фраза сохранения — форма, детали, этикетка, пропорции — и доля
кадра числом. Логотип из генератора — эскиз для поиска формы.

```text
Image 1 is the product: a glass bottle of cold-brew coffee with a kraft label.
Place it on a wet slate surface outdoors at dusk, soft rim light from behind, light rain droplets on the bottle.
The bottle takes up about 40% of the frame, slightly left of center.
Preserve the bottle's shape, cap, label text and exact proportions; do not alter the bottle in any way.
Photorealistic product photograph, shallow depth of field.
```

## Серия с одним персонажем

Сначала образец персонажа, одобренный владельцем; он идёт Image 1 в каждый следующий
кадр. Одна и та же фраза сохранения слово в слово дописывается к каждому
промпту серии. Позу и действие называй явно. Независимые вызовы без образца
расходятся по стилю.

```text
Image 1 is the approved character anchor. Do not redesign the character.
Keep exactly as in Image 1: round face, short red curly hair, green raincoat with yellow buttons, brown boots, the same watercolor children's-book style and palette.
New scene: she kneels in a snowy forest after a storm, gently lifting a frightened squirrel out of a fallen tree, looking at the squirrel with a soft smile.
No text, no watermark.
```

## Реставрация, раскраска, «улучшить»

Раскрашивание старого фото и правку лица делай на модели 2.5: `gpt-image-2`
в опубликованной пробе испортил лица. Добавь замок личности: «Do not change
faces, facial features, expressions or identity in any way» — и покажи
владельцу рядом с оригиналом.

Повышение чёткости модель делает перерисовкой, а не восстановлением деталей:
вблизи выдуманные мелочи. Если нужна верность оригиналу, предложи
отдельный апскейлер.
