# HTML Patterns — словарь визуальных блоков

Используй эти паттерны только в `projections/` или в явно неканонической
reader-facing surface. Не вставляй их как повторный summary в `canon/` или
`_ops/`: там обычный Markdown остаётся единственным изменяемым owner-ом.

Все паттерны обслуживает snippet `mavo-readability.css`. Общие механизмы:

- `data-tone="money|proof|warn|risk"` — на секции или на отдельной карточке;
  цвет по смыслу: money зелёный, proof синий, warn оранжевый, risk красный.
- HTML-блок self-contained, без пустых строк внутри; Markdown внутри не
  рендерится.
- Блок ставится после секции, которую он сжимает.

Оглавление: mini-review (base) · headline cards · text cards · gallery ·
banner · compare · styled table.

## Mini-review (base) — итог секции в карточках

Заголовок секции + 2-6 карточек «главное слово + подсказка».

```html
<section class="mavo-review" data-tone="proof">
<header>Чат-заказ против MAVO-заказа</header>
<div class="mavo-review-grid">
<article data-tone="risk"><b>Чат-заказ</b><small>~2 050 ₸</small></article>
<article data-tone="proof"><b>MAVO-заявка</b><small>~1 400 ₸</small></article>
<article data-tone="money"><b>Экономия</b><small>до ~650 ₸</small></article>
</div>
</section>
```

Модификаторы плотности: `data-kind="compact"` (уже колонки, короткие блоки),
`data-kind="stack"` (одна колонка). `<mark>` внутри карточки — маленький
цветной бейдж-пилюля.

## Headline cards — карточки только из заголовков

`data-kind="headline"`: крупные центрированные слова, без подсказок. Для
recall-ряда понятий, этапов, имён — когда подсказки лишние.

```html
<section class="mavo-review" data-kind="headline" data-tone="proof">
<header>Три опоры пилота</header>
<div class="mavo-review-grid">
<article><b>Заявка</b></article>
<article><b>Принять</b></article>
<article><b>Оплата</b></article>
</div>
</section>
```

## Text cards — карточки без заголовков, чистый текст

`data-kind="text"`: короткие тезисы одинакового веса, каждому — своя карточка.
Для набора равноправных выводов, где нет «главного слова».

```html
<section class="mavo-review" data-kind="text" data-tone="warn">
<header>Что ломает чат-заказ</header>
<div class="mavo-review-grid">
<article>Покупатель уходит на полпути переписки</article>
<article>Менеджер тратит час на уточнение макета</article>
<article>Сорванный заказ никто не считает</article>
</div>
</section>
```

## Gallery — свободная сетка карточек без рамки секции

`data-kind="gallery"`: рамка и фон секции убраны, остаются только карточки.
Для обзорной карты страницы или набора 6+ элементов, где вторая рамка — шум.

```html
<section class="mavo-review" data-kind="gallery">
<header>Карта документов зоны</header>
<div class="mavo-review-grid">
<article data-tone="money"><b>Расчёт прибыли</b><small>сценарии, break-even</small></article>
<article data-tone="proof"><b>Проверка пилота</b><small>go/no-go</small></article>
<article data-tone="warn"><b>Соседние модели</b><small>угрозы</small></article>
<article><b>Экономика каналов</b><small>CAC, пороги</small></article>
</div>
</section>
```

## Banner — полоса с крупным текстом

Один тезис крупнее любого текста, который Obsidian даёт сам. Для главного
вывода страницы или секции; `<small>` — необязательная подстрока. Не больше
одного-двух на страницу, иначе крупное перестаёт быть крупным.

```html
<div class="mavo-banner" data-tone="money">
Ценность не в сыром лиде, а в заявке, которую студия может принять
<small>рыночный вывод всей страницы</small>
</div>
```

## Compare — карточка → стрелка → карточка

Контраст «до/после», «проблема → решение», «чат → MAVO»: карточки разных
цветов через стрелку. Работает и цепочкой из трёх звеньев; на узком экране
складывается в колонку.

```html
<div class="mavo-compare">
<article data-tone="risk"><b>Чат-заказ</b><small>переписка, макет вручную, ~2 050 ₸</small></article>
<span class="mavo-arrow">→</span>
<article data-tone="money"><b>MAVO-заявка</b><small>структура, готовый файл, ~1 400 ₸</small></article>
</div>
```

## Styled table — точное чтение

```html
<table class="mavo-table">
<thead><tr><th>Критерий</th><th>Что важно</th></tr></thead>
<tbody>
<tr><td>Спрос</td><td>заявки доходят до действия</td></tr>
<tr><td>Экономика</td><td>видно время и сорванные заказы</td></tr>
</tbody>
</table>
```

## Выбор между паттернами

| Секция несёт | Паттерн |
| --- | --- |
| итог секции: слова + подсказки | mini-review |
| ряд понятий без подсказок | headline cards |
| равноправные тезисы-предложения | text cards |
| карта из 6+ элементов, обзор страницы | gallery |
| один главный вывод, крупно | banner |
| до/после, контраст двух путей | compare |
| точные числа, много колонок | styled table |
