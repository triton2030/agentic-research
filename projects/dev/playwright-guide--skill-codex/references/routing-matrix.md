# Routing Matrix

Использовать этот файл только в начале, когда ещё неясно, какой путь нужен.

## Быстрый Выбор

### 1. Уже есть только скриншот
- Идти в `$screenshot-design`
- `playwright-guide` больше не нужен, если live page не требуется

### 2. Нужен один понятный browser-pass
- Идти в `$playwright`
- Подходит для навигации, form flow, захвата screenshot/snapshot, DOM/layout evidence, smoke verification

### 3. Нужна длительная живая сессия
- Идти в `$playwright-interactive`
- Подходит для iterative UI debugging, repeated probing, проверки нескольких гипотез на одной странице

### 4. Нужен section-first visual audit на живом продукте
- Сначала `$playwright` или `$playwright-interactive`
- Потом `$screenshot-design`

### 5. Нужен Playwright script или test
- Сначала выбрать evidence path:
- разовый и прямой сценарий -> `$playwright`
- длинное исследование перед authoring -> `$playwright-interactive`
- после evidence переводить проверку в script/test

### 6. Нужна алгоритмическая проверка layout
- Сначала `$playwright` или `$playwright-interactive` для сбора данных
- Потом читать [layout-signals.md](references/layout-signals.md)

## Что Не Делать

- Не запускать самодельный browser-flow, если один из официальных installed Playwright-skills уже закрывает задачу
- Не тащить `$playwright-interactive` для задачи, где хватит одного прохода
- Не использовать live browser там, где у нас уже есть достаточный screenshot evidence
- Не переходить к визуальным выводам до сбора evidence
