# Аудит Визуальной Цельности

Открывай этот reference при жалобе на rendered overlap, clipping, overflow,
frame/content geometry, responsive-сбой, повторной правке одного component
family ради того же rendered дефекта или отдельном запросе audit/cleanup.
Обычное создание его не читает.

Audit — advisory maintenance, не linter и не общий gate. Findings не получают
pass/fail. Если запрос включает исправление, repair evidence ниже определяет
done только этого ремонта.

## Быстрые Source-Сигналы

Если нужно найти вероятное переизобретение компонентов или style drift в
исходниках, запусти:

```bash
"<каталог skill>/scripts/audit_html_style.py" \
  "<artifact-project-or-index.html>"
```

Скрипт читает HTML/CSS и возвращает review prompts о возможных cascade,
contrast, spacing, inline-style и component-reinvention рисках. Findings не
меняют exit code, ничего не исправляют и не являются визуальным вердиктом.

Интерпретируй каждый сигнал по reader job. Готовый DaisyUI-вариант обычно
заменяет случайный custom component; осознанная необычная визуализация остаётся
локальным исключением.

## Карточка: Intent Не Равен Старым Артефактам

**Главная опасность:** следующий агент копирует накопившийся drift, потому что
видит его в соседних artifacts.

Visual authority: явный user/project reference → заявленная reader job и intent
текущего artifact → его собственные tokens/components. Старые artifacts не
являются style precedent.

Не продвигай локальное исключение в starter или общий vocabulary без
повторяемого reader job и явного решения владельца.

## Карточка: Ритм И Воздух

Проверь, что:

- близкое сгруппировано, а разные смысловые ходы разделены заметнее;
- parent задаёт `gap`, component — внутренний padding;
- heading, intro и content образуют повторяемый вертикальный ритм;
- cards не прилипают друг к другу и не получают разные padding без причины;
- narrative text не растянут на всю ширину;
- нет россыпи почти одинаковых расстояний и sibling `margin` patches.

## Карточка: Отношения, Не Устройства

**Сигнал:** первый наблюдаемый geometry defect в render или повторная правка
одного component family ради того же rendered дефекта. Component family — все
instances, совпадающие по owning selector или semantic role.

До CSS-правки предъяви пользователю одной строкой и без ожидания подтверждения
продолжай: `artifact intent → один falsifiable predicate над computed
boxes/properties`. Примеры формы predicate: named content surface заполняет
content box named frame кроме названного inset; overlay rect не пересекает
text/control rect; content-sized container равен union видимого content +
padding + border кроме названного reserve; meaningful descendant содержится
либо достижим через намеренный local scroller. Это примеры отношений, не
template и не общие пропорции.

В том же сообщении предъяви trace до правки: `selector/family → predicate →
affected modes/states → candidate owner/competing owners → measurement,
которое подтверждает единственного owner либо исключает хотя бы одного
реального competing owner`. Measurement предъявляется числом при названном
viewport/state и содержит сравниваемые computed values с единицами, а не
словесный вывод. Screenshot доказывает симптом; computed geometry различает
причины. Affected — только modes/states, которые меняют этот component или
влияющего ancestor.

Исправляй минимальный общий owner, поддержанный измерением. Breakpoint rule
допустим только для названной смены composition/state, не как компенсация
базовой geometry.

Повтори тот же predicate в viewport жалобы, по обе стороны только тех
breakpoints, которые меняют component/ancestor, после затронутого
disclosure/resize state и в одном interior sample каждого affected mode.
Для bounded mode interior sample — midpoint между меняющими component/ancestor
boundaries. Для open-ended mode используй ширину, где влияющий container
достигает max/min constraint; если такой constraint не найден, назови выбранную
ширину и непроверенный край. Для каждой точки предъяви числовой actual/result
того же predicate.

Ремонт завершён, когда predicate истинно во всех этих точках; каждый новый или
оставшийся breakpoint override соответствует названному mode/state; исходный
дефект и новые непреднамеренные overlap/clipping/overflow отсутствуют.

Наблюдаемый trace: `selector/family → predicate → affected modes/states →
candidate/competing owners → discriminating or confirming measurement →
supported owner → before/after`.

## Карточка: DaisyUI Не Обязателен, Но Его Grammar Реальна

Если artifact использует DaisyUI component, проверь его актуальную semantic
structure и state прежде custom patch. Собственная компонентная форма допустима
и не обязана выглядеть как DaisyUI.

Custom CSS не является нарушением. Drift начинается, когда внутри одного
artifact он создаёт второй противоречивый способ выражать ту же роль.

Modifiers могут менять назначение theme-токена: например, `alert-soft`
использует semantic role color как foreground, тогда как обычный
`alert-info` использует пару `info` / `info-content`. Проверяй контраст
фактически выбранного variant, а не только наличие semantic class.

Не задавай глобальный unlayered `a { color: ... }`: он способен перекрыть
foreground layered-компонентов DaisyUI, оставив новый фон со старым
унаследованным текстом. Наследование обычных ссылок ограничивай content-role,
исключая `btn`, `link` и stateful navigation.

## Карточка: Иерархия Видна До Декора

Один взгляд должен различать главный ответ, опору, secondary detail и следующий
ход. Размер, контраст, whitespace и position работают согласованно; рамки,
цветные surfaces и иконки не конкурируют за одинаковый приоритет.

Если убрать backgrounds и borders, headings и DOM order всё ещё должны
объяснять страницу.

## Карточка: Motion Помогает Понять

Оставляй animation, когда она показывает state change, причинность,
пространственную связь или ход системы. Убирай её, когда она только сообщает
«здесь было место для эффекта», задерживает чтение или создаёт ложный progress.

Не унифицируй все animations ради консистентности: важнее единая роль motion,
чем один и тот же эффект.

## Карточка: Drift Или Локальное Исключение

**Drift:** случайно появившийся второй способ выражать уже существующую роль.

**Локальное исключение:** намеренное решение для конкретного reader job,
собранное в одном owner и не копируемое автоматически дальше.

Audit предлагает убрать drift и явно назвать полезные исключения. Он не
переписывает их в общий стиль.

## Короткий Протокол

1. Зафиксируй, что страница должна помочь понять или сделать.
2. Посмотри текущий render или screenshot и только нужный source.
3. Сравни с visual intent текущего artifact, а не с соседними artifacts.
4. Назови максимум три-пять изменений с наибольшим эффектом для hierarchy,
   rhythm, DaisyUI fidelity и понимания.
5. Отдельно перечисли удачные решения и intentional local exceptions.

Ничего не исправляй без запроса на применение. Не выдавай `pass/fail` и не
делай audit обязательной стадией следующего создания.

## Формат Ответа

- **Вердикт:** цельно / есть drift / стиль распался.
- **Сохранить:** что уже работает и почему.
- **Исправить первым:** максимум три-пять материальных изменений.
- **Локальные исключения:** что намеренно не обязано стать общим стилем.
- **Не проверено:** состояния или viewport, которых audit не видел.
