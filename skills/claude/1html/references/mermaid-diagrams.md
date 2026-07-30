# Mermaid: Читаемые Диаграммы

Читай эти карточки, когда знание находится в связях, порядке, ветвлении или
иерархии. Runtime, ELK и viewer добавляются готовым helper script, поэтому здесь
нет копируемой HTML-страницы.

## Карточка: Диаграмма Имеет Вопрос

**Сигнал:** Mermaid используется как декоративная версия списка.

**Практика:** сформулируй вопрос, на который отвечает topology. Один тезис и
независимые карточки оставь обычным текстом или DaisyUI.

**Не делай:** не помещай абзацы в nodes; labels называют сущность, состояние
или действие.

## Карточка: Тип По Отношению

| Знание | Тип |
| --- | --- |
| Процесс, зависимости, развилка | `flowchart` |
| Порядок сообщений | `sequenceDiagram` |
| Состояния и переходы | `stateDiagram-v2` |
| Компактная иерархия | `mindmap` |
| Сравнение по двум осям | `quadrantChart` |

## Карточка: Direction По Форме

**Сигнал:** `LR` создаёт длинную горизонтальную ленту.

**Практика:** `TB` — default для узких экранов, глубоких процессов и нескольких
кластеров. `LR` подходит короткому линейному маршруту. Сначала сократи labels и
число одновременных веток.

**Не делай:** не задавай SVG принудительный `min-width`.

## Карточка: ELK Только Для Сложности

**Сигнал:** есть несколько кластеров, cross-links, обратные петли или много
узлов.

**Практика:** простой graph оставь на `dagre`; сложный flowchart переключи на
`layout: elk`. Начни с defaults. `mergeEdges` и
`nodePlacementStrategy` меняй только под наблюдаемую проблему раскладки.

**Не делай:** ELK не превращает смешанные reader jobs в одну понятную схему.
Если topology остаётся стеной, раздели её по вопросу читателя.

## Карточка: DaisyUI Владеет Обрамлением

**Сигнал:** toolbar, пояснения и controls рисуются внутри diagram syntax.

**Практика:** DaisyUI владеет card, toolbar, legend, dialog и disclosure.
Mermaid владеет topology. Для custom theme используй `theme: base` и hex-зеркало
semantic DaisyUI colors: Mermaid theme engine принимает hex, а не CSS custom
properties.

`classDef` различает semantic node roles; label и форма дублируют важный цвет.

## Карточка: Viewer Для Реально Большой Схемы

**Сигнал:** fit-to-width делает labels нечитаемыми.

**Практика:** первый кадр показывает всю систему. Большая схема получает
локальный viewer с pan, wheel/pinch zoom, reset-to-fit и fullscreen. Добавь его
в artifact готовым script:

```bash
"<каталог skill>/scripts/add_mermaid_bundle.sh" "<artifact-name>" "<project-root>"
```

Viewer инициализируется только после того, как Mermaid заменил definition на
SVG. Не копируй runtime вручную.

## Карточка: Текстовый Маршрут Остаётся

**Сигнал:** вывод доступен только через исследование графа.

**Практика:** рядом дай короткое резюме: что показано, главный путь, развилка и
вывод. В diagram definition задай `accTitle` и `accDescr`.

**Не делай:** цвет, spatial position и hover не остаются единственными
носителями смысла.

## Официальные Опоры

- [Mermaid layouts](https://mermaid.js.org/config/layouts.html)
- [Mermaid flowcharts](https://mermaid.js.org/syntax/flowchart)
- [Mermaid theming](https://mermaid.js.org/config/theming.html)
- [Mermaid accessibility](https://mermaid.js.org/config/accessibility)
