# Вырезано — с причиной

## Пересборка 2026-08-20 — design freedom + show, don't tell

Решение 2026-08-19 о едином visual language ниже сохранено как история, но
отменено более поздними словами владельца: обязательные templates ограничивают
design freedom; `1html` должен спасать от стены текста и показывать сложное
визуально. Текущий owner — `SKILL.md` и owner evidence в
`_ops/chat-recall/2026-08-19-212344-codex-01a01ad4.md`.

### Снято

- обязательный editorial shell, palette, `.artifact-*` vocabulary,
  `pages/_template.html`, `pages.js` и `project.js`;
- `structure-patterns.md`, editorial preview и preset CSS: opt-in label не
  оправдывал package surface, а snippets продолжали тянуть агента к одной
  композиции;
- blocking checks старого `artifact-*` shell/rail/header/theme/template и visual
  exception flag; позже возвращён только узкий framework-contract: текстовый
  Daisy `.card` требует direct `.card-body`, `.hero` — `.hero-content`, а
  custom layout получает собственное имя. Он ловит доказанную причину
  исчезнувших padding/collision, не palette или composition;
- отдельная chart-библиотека первоначально была снята как speculative surface;
  поздний прямой запрос владельца (`owner evidence :40`) вернул её в scope как
  opt-in ECharts: один runtime и независимые data/options recipes без page
  template;
- идея source-only линтером доказать красоту: blocking gate владеет только
  переносимостью, ресурсами, синтаксисом и add-on wiring.

### Оставлено И Переопределено

- blank scaffold — техническая форма bundle, не design template;
- catalog theme живёт только в `assets/catalog/` и не копируется в artifacts;
- DaisyUI/Tailwind/Alpine/Lucide остаются локальными primitives, но artifact
  владеет HTML/CSS/JS composition и palette;
- Table, Mermaid и React Flow — условные helpers. React Flow принят только как
  prebundled local IIFE, который проходит прямой `file://` smoke без dev server;
- центральный operator: relation → simplest visual carrier → visible
  heading/caption; visual form показывает подтверждённый смысл, а не украшает.

## Рефактор 2026-08-19 (телеграф · структурное разнообразие · тощий starter)

Заказ владельца: артефакты телеграфно и только дельта; визуальный язык один
(палитра, схема, иконки, стиль), разнообразие — в структуре повествования и
уместности интерактива; starter похудел; скилл может нести много информации
при малом числе инструкций.

### Переехало к своему владельцу (не потеряно)

| Что | Было | Стало |
|---|---|---|
| Карточка вердикта, сетка карточек (3 из 4; четвёртая была дублем обычной по классам, её тезис «оставить следующий шаг» уже живёт в теле), details-пример, ряд баджей | `assets/starter/index.html` (плейсхолдеры) | `references/structure-patterns.md` — копируемые снипеты |
| Обучающий текст плейсхолдеров («начните с решения…», «используйте карточки как смысловые блоки…») | `assets/starter/index.html` | правила уже жили в теле (Назначение, Главный Контракт) — текст был их дублем в прозе шаблона; снят |

### Поглощено общей формулировкой (выводится из неё)

- «Каждый видимый фрагмент должен выполнять информационную работу. Удаляй
  вводные фразы, повторы и декоративные объяснения» → «Пиши телеграфно:
  только дельту и самое важное» (слова владельца 2026-08-19).
- «Starter — заготовка результата, а не reference для чтения: скопируй, меняй
  только нужные места» → «Starter — пустой каркас с готовым shell»: строка
  устарела вместе с похудением шаблона; «меняй только нужные места» выводится
  из Runtime-Границ (project.js/shell не переписываются).

### Снято

- Rail-note «Локальный черновик. Замените содержание…» из starter — служебная
  заметка-инструкция внутри результата; правила живут в скилле, не в артефакте.
- Иконки в скелете starter (zap, palette, package-check, arrow-up) — были
  частью примеров; сами примеры переехали в structure-patterns.md.
- Комментарий-инструкция в скелете starter (указатель на structure-patterns) —
  снят по аудиту: тот же класс, что rail-note; маршрут живёт в Роутере тела.
- Нормативные строки из structure-patterns.md («для коллекции, не аргумента»;
  «side-by-side для двух, таблица — когда полей больше») — по аудиту: третьи
  носители правил, владельцы — readable-design.md и daisy-storytelling.md.
- «Визуальный язык один…» из буллета Главного Контракта — по аудиту: второй
  носитель, владелец визуальной оси — Runtime-Границы.

### Рассмотрено и отклонено

- Общая папка `_shared/` для lib вместо копий по артефактам: модель библиотеки
  не читает — выигрыш только диск (~1,8 МБ/артефакт), цена — потеря
  автономности папки артефакта и два уровня относительных путей. KISS: копия
  остаётся. Вернуться, если объём каталога станет проблемой.
- Разные DaisyUI-темы на артефакт: отклонено словом владельца 2026-08-19 —
  «палитра, схема, иконки, стиль один и тот же», разнообразие структурное.
- Сокращение словаря `.artifact-*` (34 класса): правка theme.css + project.js
  рискованна и не нужна — вместо неё шпаргалка классов в теле SKILL.md.
- Перенос «Шпаргалки Письма» из тела в reference (находка аудита F8):
  оставлена в теле — владелец явно разрешил длинное тело с большим объёмом
  знания; шпаргалка нужна в каждый ход письма.

## Починка по боевому прогону 2026-08-19 (артефакт whatsapp-order-interface)

Свежее окно создало артефакт; владелец забраковал: «смотреть не дизайн, а
тексты, код». Корни и починки:

- Тексты — проза вместо телеграфа (857 слов, полные предложения, одна мысль в
  пяти местах): правило было прочитано и не применено → в пункт добавлены
  названный дефолт модели и стоп-условие «одна мысль — один дом».
- Код — `artifact-card`/`artifact-verdict` голыми, без `card`+`card-body` →
  отступы перенесены на корни `.artifact-*`, а блокирующий source-check не даёт
  сдать неканоническую структуру через единый `finish_html_bundle.sh`.
- Код — плейсхолдер «Название проекта» из `pages.js` уплыл в шапку → в starter
  `title`/`icon` пустые: shell сам берёт meta `artifact-title` → первый `h1`.
- Код — изобретённый паттерн подписи шага (`div.text-left>p+p` ×5) → в
  structure-patterns добавлен канонический шаг с подписью.
- Снята страховка `:not(:has(> .card-body))`: root padding одинаково защищает
  каноническую и незавершённую разметку, без условного selector-а.
- Обновление DaisyUI/Alpine отклонено: дефект принадлежит локальному контракту
  `artifact-*`, а не версии библиотек.

## Системный stress-test 2026-08-19

- Default rail, пустой footer и дубль static/runtime шапки сняты:
  starter сразу одноколоночный; rail возвращается только для двух и более
  реальных anchors.
- Ручное подключение Table/Mermaid снято: helpers копируют assets и
  идемпотентно подключают все текущие live pages.
- `pages.js` сужен до статического JSON-объекта: checker требует каждый live
  page ровно один раз, отклоняет computed/duplicate/missing paths и `<base>`.
- Vendor component snapshot очищен от вложенного routing/install/CDN
  control-plane; notices/licenses вошли в current-generation byte-lock.
- Безусловный byte-lock к current owner снят по Fresh Eyes: он превращал
  любое обновление skill в скрытую миграцию старых artifact. Marker
  `.1html-bundle-version` ограничивает byte-lock current-generation bundle:
  core runtime, shared theme, immutable page template и активные add-ons;
  pre-marker и previous-generation artifact требуют явный
  `finish_html_bundle.sh --legacy`, а legacy сохраняет только version-stable
  проверки. Не-current marker больше не превращается в молчаливый обход
  current contract и не становится тупиком после следующего version bump.
- Vendor refresh отделён: official Releases показывают
  [DaisyUI 5.7.19](https://github.com/saadeghi/daisyui/releases),
  [Alpine 3.16.2](https://github.com/alpinejs/alpine/releases),
  [Lucide 1.33.0](https://github.com/lucide-icons/lucide/releases) и current
  [Tailwind 4.3.3](https://github.com/tailwindlabs/tailwindcss/releases), но
  refresh не исправляет доказанный локальный дефект и требует своего
  pinned-refresh lifecycle.
