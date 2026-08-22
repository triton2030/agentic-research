---
name: 1mantine-dev
description: >
  Работа с Mantine: вызывай, когда UI на Mantine создаётся или чинится и нужно
  выбрать компонентную композицию, тему, стили, форму, портал, SSR или место
  владельца; также при Mantine-специфичном симптоме или обновлении @mantine/*.
  Не вызывай для общей архитектуры приложения или CSS без Mantine-решения.
---

# Mantine

## Контекст

Mantine — версионируемый UI-runtime. Модель часто применяет API прошлого мажора
или общий React/CSS там, где семантикой, композицией и интеграцией уже владеет
публичный механизм Mantine. Скил владеет этим швом, но не общей архитектурой
приложения и домена.

## Цель

Код работает в целевом приложении на установленной когорте Mantine и легко
редактируется: Mantine-решение имеет одного владельца, а публичная композиция не
обойдена локальным CSS или декоративной обёрткой.

## Критерии успеха

- Названы целевое приложение и подтверждённая установленная когорта `@mantine/*`;
  если когорта не разрешилась, версионные утверждения не сделаны.
- Выбран ближайший публичный компонент или композиция Mantine, а владелец
  повторяющегося решения назван.
- «Работает» доказано на слое сбоя.
- Непроверенное и следующий способ его проверить названы.

## Инварианты

- Диапазон в manifest не доказывает установленную версию. Скрипт инспекции —
  разведка; точную когорту подтверждают resolved lock или установленные `.d.ts`.
- Все `@mantine/*` одной точной версии. Неразрешённая когорта запрещает
  версионные утверждения, но не общую диагностику.
- Сначала публичные компоненты и композиция Mantine; низкоуровневый `Combobox`,
  приватные селекторы, custom CSS и обёртка 1:1 — только после доказанного пробела.
- Повторяющийся вертикальный или горизонтальный layout сначала выражается через
  подходящие `Stack`, `Group`, `Flex` или другой публичный primitive Mantine;
  локальный style остаётся только для остаточного one-off.
- У каждого runtime-root одна точка интеграции provider, global CSS, SSR,
  color scheme и portal bootstrap. У разных приложений могут быть разные roots;
  владелец определения темы отделён от владельца runtime-интеграции.
- Feature, workflow, schema, data и права остаются у приложения. Mantine владеет
  UI-механизмом, но не доменным контрактом.
- Публичный Styles API, CSS Modules, `data-*` и CSS-переменные предпочтительнее
  зависимости от внутреннего DOM и приватных имён.

## Дельта

Модель знает React и CSS, поэтому дешёвый обход выглядит разумно: `div` или
`Box` с `display: grid`, локальная обёртка, память о прошлом мажоре. Такой код
может компилироваться, но размазывает layout и владельцев по экранам либо молча
ломается в runtime. Наблюдавшийся случай: форма логина на Mantine была собрана
через сырой grid вместо `Stack`/`Group`.

## Известные сбои

### Компилируется и молча не работает

| Выглядит правильно | Молча ломается | Лечение |
| --- | --- | --- |
| `Box` или `div` с `display: grid/flex` для повторяющейся композиции | публичная семантика Mantine обходится, layout размазывается по экранам | сначала `Stack`, `Group`, `Flex` или другой подходящий public primitive; локальный style только для остаточного one-off |
| свой CSS импортирован как придётся | в dev верно, в prod бандлер меняет порядок, Mantine выигрывает | все импорты на `@mantine/*/styles.layer.css` + `@layer base, mantine, components;`; смешивать с `styles.css` нельзя |
| только `@mantine/core/styles.css` | dates / carousel / notifications / charts / schedule без вёрстки | у каждого пакета кроме `hooks` свой `styles.css`; у `schedule` порядок core → dates → schedule |
| CSS-модуль как в демо | `light-dark()`, `rem()`, `@mixin dark`, `$mantine-breakpoint-*` мертвы | `postcss-preset-mantine` + `postcss-simple-vars` |
| `styles={{ input: { '&:hover': … } }}` | это инлайн: псевдоклассы и media внутри не работают, классом не перебить | псевдо и медиа — в CSS-модуль через `classNames` |
| `components: { 'Menu.Item': … }` | тема не применяется, ошибки нет | ключ без точки: `MenuItem`, `TabsList`; явный проп всё равно бьёт тему |
| `useForm` + `getInputProps` | по умолчанию режим controlled; в uncontrolled без `key={form.key('x')}` инпут не обновится на `setValues` | uncontrolled включается явно; тогда `form.key()` на каждом инпуте, `form.getValues()` вместо `form.values`, `onValuesChange` вместо `useEffect`; свой инпут обязан принимать `defaultValue` |
| `withAsterisk` как «поле обязательное» | звёздочка нарисована, нативного `required` нет | ставь `required` отдельно |
| `NumberInput` в числовое поле | `onChange` отдаёт `number \| string` на пустом и промежуточном вводе | нормализуй на границе домена |
| `value={объект}` в Select/MultiSelect | контрол пуст: только string / number / boolean | объект — из второго аргумента `onChange(value, option)`, свой вид — `renderOption`; `Combobox` — последний ход, он требует ручного selected-index |
| `Autocomplete` как «Select с поиском» | это свободный ввод строки, а не выбор из набора | выбор — `Select`; произвольные значения — `TagsInput`; без поиска и своего рендера дешевле `NativeSelect` |
| `<Notifications>{children}</Notifications>` | белый экран: children не поддерживаются | сиблинг внутри провайдера; `ModalsProvider` — внутри `MantineProvider`; `NavigationProgress` без отрисованного компонента молчит |
| `.parent .dropdown {}` для содержимого оверлея | портал рендерится в конец `body`: селектор потомка и `overflow` не действуют | стилизуй через `classNames` самого компонента |
| `Select` внутри `Popover` | клик снаружи закрывает оба | `comboboxProps={{ withinPortal: false }}`; у дат — `popoverProps` |
| свои числа в `zIndex` | у Mantine документированные переменные, вложенные модалки считает `Modal.Stack` | `--mantine-z-index-*`, `Modal.Stack` |
| `colorScheme === 'dark' ? <A/> : <B/>` | сервер не видит localStorage → hydration mismatch | различие только стилями: `light-dark()`, `@mixin dark`; клиентский `auto` — `useComputedColorScheme` |
| `ColorSchemeScript` и провайдер с разным `defaultColorScheme` | вспышка темы на первой отрисовке | одинаковое значение + `mantineHtmlProps` на `<html>` |
| Mantine в Server Component | все компоненты клиентские | `'use client'` в своём файле; в RSC — плоские экспорты `PopoverDropdown`, `TabsTab` |
| `useMediaQuery` для вёрстки под SSR | сервер и клиент расходятся на первой отрисовке | `hiddenFrom` / `visibleFrom` и медиа-запросы; брейкпоинты темы — в `em`, CSS-переменная в условии запроса не работает |
| своя обёртка как target у Menu/Popover | рендерится, но позиционирование и клавиатура ломаются | пробрасывай инжектируемые пропы и `ref` |
| `createTheme` с парой оттенков цвета | цвет темы требует минимум 10 оттенков | задай все 10 |
| доступность взята с примитива | зелёный axe не доказывает порядок заголовков, имена icon-only контролов и видимый фокус после своей темы | у Accordion — `order`; клавиатурный проход руками |
| `Table` дорастает до сортировки / пагинации / виртуализации | DataGrid в Mantine нет и не планируется | Mantine React Table / DataTable / TanStack |
| Dropzone «загружает», Tiptap «хранит документ», Charts «умеет всё» | Dropzone только принимает и валидирует `File`; схема и сериализация — Tiptap; продвинутый API графиков — Recharts | загрузка, хранение и схема остаются приложению |
| апгрейд по одному пакету или «починил первую ошибку компилятора» | мажор меняет peer-ы и переименовывает API пачкой, патчи носили и регрессии | подними все `@mantine/*` одной версией, сверь peer-ы (`dates`→dayjs, `charts`→Recharts 3, `carousel`→Embla 8, `tiptap`→Tiptap 3, `schedule`→rrule), затем typecheck и прод-сборка |

### Признаки старой памяти

Применимо только то, что было **до** мажора проекта: на v8 `gutter`, `in` и
`TypographyStylesProvider` ещё валидны. Точный список — в migration guide того
мажора, на который идёшь.

| Мажор | Что изменилось |
| --- | --- |
| 7.0 | удалены `sx`, `createStyles`, `<Global>`, `<MediaQuery>`, `theme.colorScheme`, `theme.fn.*`, вложенные селекторы внутри `styles`; в 7.x `itemComponent` → `renderOption`, `nothingFound` → `nothingFoundMessage` |
| 8.0 | `@mantine/dates` отдаёт строки `YYYY-MM-DD` вместо `Date`; `DatesProvider timezone` убран; `timeInputProps` → `timePickerProps`; Carousel — опции в `emblaOptions`, Embla ставится явно; `Portal.reuseTargetNode` включён по умолчанию и меняет порядок наслоения |
| 9.0 | требует React 19.2+; `Text`/`Anchor` `color` → `c`; `Grid` `gutter` → `gap`; `Collapse` `in` → `expanded`; `Spoiler` `initialState` → `defaultExpanded`; `TypographyStylesProvider` → `Typography`; `zodResolver` → `schemaResolver`; `defaultRadius` sm → md |

Симптом похож на типовой → [`references/help-center-map.md`](references/help-center-map.md):
без карты слепой поиск ведёт в ответы другого мажора или не к тому слою сбоя.

Решение повторится больше чем в одном месте либо тянет на тему, обёртку,
вариант или свой primitive → [`references/placement.md`](references/placement.md):
неверный владелец размножает следующую правку по экранам.

## Механика

1. Назови целевое приложение или runtime-root в монорепо. Запусти
   `python3 <skill-root>/scripts/inspect_mantine.py <target-root> --json` для
   разведки версии, когорты, фреймворка и CSS-импортов.
2. Подтверди resolved-когорту по lock или установленным `.d.ts`. Если она не
   разрешилась, назови это и не делай версионных утверждений.
3. Сформулируй видимое UI-поведение и выбери ближайший публичный компонент или
   композицию Mantine. Custom CSS, wrapper и low-level primitive требуют
   названного пробела публичного API.
4. Определи владельца повторяющегося решения по карте размещения; существующая
   конвенция проекта сильнее fallback-структуры скила.
5. Для симптома или точного API иди в источник:
   - точный API установленной версии — `node_modules/@mantine/*/**/*.d.ts`;
   - текущая страница — `mantine.dev/llms.txt` → `mantine.dev/llms/<id>.md`
     (`mantine.dev/core/button.md` = 404);
   - мажор — `mantine.dev/llms/guides-<N-1>x-to-<N>x.md`.
6. Пройди только строки таблиц, относящиеся к затронутому механизму.
7. Дай доказательство в формате `слой → команда/действие → наблюдаемый
   результат`: порядок CSS — prod build; API — typecheck; формы, порталы и
   оверлеи — браузер; SSR и hydration — жёсткая перезагрузка. `env="test"`
   только для Jest/Vitest, не для browser proof.

## Завершение

Верни: целевое приложение и resolved-когорту · изменившееся Mantine-решение ·
владельца и место · `слой → проверка → результат` · неизвестное и следующий
способ его проверить.
