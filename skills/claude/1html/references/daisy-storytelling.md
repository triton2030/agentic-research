# DaisyUI: Компоненты И Motion

Читай эти карточки, когда выбираешь компонент, semantic role, disclosure или
анимацию. В starter закреплён локальный DaisyUI `5.7.4`.

Карточки:

- Daisy сначала;
- компонент по отношению;
- нативный state;
- ритм принадлежит starter;
- motion объясняет изменение;
- DaisyUI 5, не старые рецепты;
- полный ассортимент, малый набор.

## Карточка: Daisy Сначала

**Сигнал:** разметка собирается только из utility-классов.

**Практика:** сначала выбери компонент по смыслу (`card`, `alert`, `table`,
`tabs`, `collapse`, `modal`, `steps`), затем semantic color role, затем малые
Tailwind utilities для конкретной композиции. Повторяемый visual token
принадлежит `theme.css`.

**Не делай:** не закрепляй случайные palette colors и SVG fill/stroke, если роль
уже выражает тема.

## Карточка: Компонент По Отношению

| Отношение | DaisyUI-форма | Не использовать для |
| --- | --- | --- |
| Последовательность | `steps` | независимых тем |
| Время | `timeline` | причинности без времени |
| Одновременное сравнение | `table`, `diff`, side-by-side | tabs |
| Равноправные виды объекта | `tabs`, `swap` | page navigation |
| Иерархия страниц | `navbar`, `menu`, `dropdown`, `breadcrumbs` | tabs |
| Модульная коллекция | `card`, `list`, gallery | непрерывного аргумента |
| Одна необязательная глубина | `details.collapse` | главного вывода |
| Редкая сфокусированная задача | `dialog.modal` | справочного склада |
| Действие / state change | `btn`, control | перехода в другое место |

`badge` — короткий status или tag. `alert` — важное состояние с последствием.
`stats` — только реальные числа с контекстом. `tooltip` — короткое
необязательное пояснение, не скрытая инструкция.

## Карточка: Дерево Страниц Сверху

**Сигнал:** artifact project содержит родительские и дочерние страницы.

**Практика:** используй готовый верхний `navbar`. Leaf остаётся прямой ссылкой;
branch раскрывает `menu` через нативные `details`/`summary`, содержит отдельную
ссылку на overview родителя и вложенные страницы. `breadcrumbs` показывают
текущий путь. В `ARTIFACT_PROJECT.pages` вложи узлы через `children`; HTML-файлы
остаются плоскими в `pages/`.

**Не делай:** не изображай иерархию tabs, не открывай submenu только по hover и
не превращай summary родителя в единственный недоступный путь к его странице.

## Карточка: Нативный State

**Сигнал:** для одного открытия пишется Alpine или ручной JS.

**Практика:** searchable disclosure делай через `details` + `summary` с
DaisyUI collapse. Modal начинай с нативного `<dialog>`: DaisyUI рекомендует этот
метод, он закрывается по `Esc` и блокирует фон.

**Не делай:** checkbox- и anchor-модалы являются legacy-вариантами, а Alpine
нужен только для связанных состояний.

## Карточка: Ритм Принадлежит Starter

**Сигнал:** новая страница заново собирает shell, section spacing и card padding
из utility-классов.

**Практика:** сначала сохраняй готовых владельцев: `.artifact-shell` — page
layout, `.artifact-hero` — первый ответ, `.artifact-section` — ход рассказа,
`.artifact-grid` — расстояние коллекции, `.artifact-card .card-body` —
внутренний padding, `.artifact-details` — необязательная глубина. Parent владеет
расстоянием между детьми; component — внутренним padding.

**Исключение:** необычная visual explanation, interface или animation может
потребовать своей композиции. Переиспользуй DaisyUI roles и текущую palette, а
новые расстояния держи в одном локальном owner, не рассыпай по HTML.

**Не делай:** не начинай с literal hex, inline styles, `gap-[11px]`,
`p-[27px]` или новой spacing scale только потому, что так быстрее набрать.

## Карточка: Motion Объясняет Изменение

**Сигнал:** анимация добавляется, потому что экран кажется статичным.

**Практика:** сначала используй встроенный transition компонента. Motion
допустим, когда показывает смену state, пространственную связь или причинность.
Он не задерживает чтение и действие.

- `swap-rotate` и `swap-flip` — только для двух состояний одного control;
- collapse и modal — для появления связанной глубины;
- `loading-*` — только пока действительно идёт ожидание;
- дополнительный motion ограничивай opacity/transform и короткой дистанцией;
- для custom motion используй `motion-safe:` и `motion-reduce:`.

**Не делай:** не запускай decorative autoplay, infinite motion, stagger всего
экрана или ложный progress. Не анимируй layout без смысловой причины.

## Карточка: DaisyUI 5, Не Старые Рецепты

**Сигнал:** предлагаются `--animation-btn`, `--animation-input` или
`--btn-focus-scale`.

**Практика:** эти theme variables удалены в DaisyUI 5. Используй поведение
актуального компонента и только его документированные локальные variables,
например `--overflow-delay` у collapse.

В DaisyUI 5.6 native `details` collapse получил более плавную анимацию, а
loading animations — static fallback при `prefers-reduced-motion`. Это не
означает, что любой custom motion автоматически доступен: extra animation всё
равно получает reduced-motion вариант.

## Карточка: Полный Ассортимент, Малый Набор

**Сигнал:** знакомый компонент не выражает нужную связь.

**Практика:** точечно найди термин в `daisyui-llms.txt`; полный локальный bundle
доступен. Выбери минимальное число разных component families на странице.

**Не делай:** не открывай весь reference и не превращай artifact в showcase
DaisyUI.

## Официальные Опоры

- [daisyUI 5 release notes](https://daisyui.com/docs/v5/?lang=en)
- [daisyUI Swap](https://daisyui.com/components/swap/?lang=en)
- [daisyUI Collapse](https://daisyui.com/components/collapse/?lang=en)
- [daisyUI Modal](https://daisyui.com/components/modal/?lang=en)
- [daisyUI Loading](https://daisyui.com/components/loading/?lang=en)
- [daisyUI Navbar](https://daisyui.com/components/navbar/?lang=en)
- [daisyUI Dropdown](https://daisyui.com/components/dropdown/?lang=en)
- [daisyUI Menu](https://daisyui.com/components/menu/?lang=en)
- [daisyUI Breadcrumbs](https://daisyui.com/components/breadcrumbs/?lang=en)
- [daisyUI utilities](https://daisyui.com/docs/utilities/?lang=en)
- [daisyUI 5.6](https://daisyui.com/blog/v5.6/)
- [Tailwind animation and reduced motion](https://tailwindcss.com/docs/animation)
