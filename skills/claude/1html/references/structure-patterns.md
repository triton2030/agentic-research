# Готовые Блоки Страницы

Момент: составляется `main` страницы и нужен готовый блок в фирменном языке.
Файл даёт копируемый код без правил: выбором механики раскрытия владеет
[compact-disclosure](compact-disclosure.md), парой отношение → компонент —
[daisy-storytelling](daisy-storytelling.md).

Тема `editorial` стилизует стандартный DaisyUI сама: блоки ниже выглядят
фирменно без нового CSS (копия из тела SKILL.md — правится вместе с ним).
Сверено с bundle DaisyUI 5.7.4, 2026-08-19.

## Вердикт — Карточка Главного Вывода

```html
<article class="card artifact-verdict">
  <div class="card-body">
    <p class="artifact-kicker">Рекомендуемый вывод</p>
    <h2 class="card-title artifact-verdict-title">Главное одной фразой.</h2>
    <p>Почему это верно сейчас; что остаётся за границей черновика.</p>
  </div>
</article>
```

## Ход Рассказа

```html
<section class="artifact-section" id="stable-id">
  <p class="artifact-kicker">01 · Название хода</p>
  <h2 class="artifact-heading">Смысловой ход</h2>
  <p class="artifact-section-intro">Один-два телеграфных тезиса.</p>
</section>
```

## Ряд Статус-Баджей

```html
<div class="artifact-badges" aria-label="Ключевые статусы">
  <span class="badge badge-outline">
    <i data-lucide="zap" class="size-3" aria-hidden="true"></i>
    статус
  </span>
</div>
```

## Сетка Карточек

```html
<div class="artifact-grid">
  <article class="card artifact-card artifact-card--primary">
    <div class="card-body">
      <span class="artifact-number">01</span>
      <h3 class="card-title artifact-card-title">Главная — шире остальных</h3>
      <p>…</p>
    </div>
  </article>
  <article class="card artifact-card">
    <div class="card-body">
      <span class="artifact-number">02</span>
      <h3 class="card-title artifact-card-title">Обычная</h3>
      <p>…</p>
    </div>
  </article>
  <article class="card artifact-card artifact-card--stop">
    <div class="card-body">
      <span class="artifact-number">03</span>
      <h3 class="card-title artifact-card-title">Стоп или риск — глиняный фон</h3>
      <p>…</p>
    </div>
  </article>
</div>
```

## Раскрытие Глубины

```html
<details class="collapse collapse-arrow artifact-details">
  <summary class="collapse-title">Показать расчёт</summary>
  <div class="collapse-content"><p>Evidence, источники, оговорки.</p></div>
</details>
```

## Шаги

```html
<ul class="steps steps-vertical">
  <li class="step step-primary">Сделано</li>
  <li class="step step-primary">Сделано</li>
  <li class="step">Следующий шаг</li>
</ul>
```

Шаг с подписью — телеграфной строкой в том же `li`, без своих обёрток:

```html
<ul class="steps steps-vertical">
  <li class="step step-accent text-left">
    <span><strong>Собрал корзину.</strong> Много позиций; превью на мокапе.</span>
  </li>
</ul>
```

## Timeline

```html
<ul class="timeline timeline-vertical">
  <li>
    <div class="timeline-start artifact-kicker">19 авг</div>
    <div class="timeline-middle">
      <i data-lucide="circle-check" class="size-4" aria-hidden="true"></i>
    </div>
    <div class="timeline-end timeline-box">Событие</div>
    <hr>
  </li>
  <li>
    <hr>
    <div class="timeline-end timeline-box">Следующее событие</div>
  </li>
</ul>
```

## Сравнение — Side-by-Side

```html
<div class="grid gap-4 md:grid-cols-2">
  <article class="card artifact-card">
    <div class="card-body">
      <h3 class="card-title artifact-card-title">Вариант A</h3>
      <p>…</p>
    </div>
  </article>
  <article class="card artifact-card">
    <div class="card-body">
      <h3 class="card-title artifact-card-title">Вариант B</h3>
      <p>…</p>
    </div>
  </article>
</div>
```

## Сравнение — Таблица

```html
<div class="overflow-x-auto">
  <table class="table">
    <thead><tr><th></th><th>A</th><th>B</th></tr></thead>
    <tbody><tr><th>Цена</th><td>…</td><td>…</td></tr></tbody>
  </table>
</div>
```

## Числа

```html
<div class="stats stats-vertical md:stats-horizontal">
  <div class="stat">
    <div class="stat-title">Метрика</div>
    <div class="stat-value">18 КБ</div>
    <div class="stat-desc">откуда число</div>
  </div>
</div>
```

## Комментарий Агента, Отделённый От Фактов

Слой «Комментарий» из тела SKILL.md: тип назван, блок визуально отделён.

```html
<div role="alert" class="alert alert-warning items-start">
  <i data-lucide="triangle-alert" class="size-5" aria-hidden="true"></i>
  <div>
    <strong>Риск — комментарий агента</strong>
    <p class="text-sm">Что замечено и почему это не факт источника.</p>
  </div>
</div>
```

Типы: вопрос — `alert-info` + `badge-help`; гипотеза — `alert` + `lightbulb`;
найденная ошибка — `alert-error` + `octagon-alert`.

## Tabs — Равноправные Виды

```html
<div role="tablist" class="tabs tabs-lift">
  <input type="radio" name="views_1" class="tab" aria-label="Обзор" checked>
  <div class="tab-content border-base-300 bg-base-100 p-6">…</div>
  <input type="radio" name="views_1" class="tab" aria-label="Данные">
  <div class="tab-content border-base-300 bg-base-100 p-6">…</div>
</div>
```

## Два Состояния — Alpine

```html
<section x-data="{ on: false }">
  <label class="label cursor-pointer gap-3">
    <span>Показать комментарии</span>
    <input type="checkbox" class="toggle" x-model="on">
  </label>
  <div x-show="on" x-transition.opacity>…</div>
</section>
```
