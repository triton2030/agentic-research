# Симптом → официальный ответ

`help.mantine.dev` — 72 курируемых мейнтейнером вопроса. Здесь только адреса:
ответ живёт на странице и меняется вместе с версией. Нужного симптома нет —
ищи в разделе FAQ индекса `mantine.dev/llms.txt`.

| Симптом | Адрес |
| --- | --- |
| мои стили проигрывают стилям Mantine | `help.mantine.dev/q/styles-order` |
| кнопки прозрачные, фон только на hover (Tailwind) | `help.mantine.dev/q/transparent-buttons` |
| конфликт с Tailwind, Emotion, styled-components | `help.mantine.dev/q/third-party-styles` |
| применить стиль ко всем компонентам сразу | `help.mantine.dev/q/apply-styles-to-all` |
| динамические стили из данных | `help.mantine.dev/q/dynamic-css-styles` |
| вложенные селекторы во внутренних стилях | `help.mantine.dev/q/nested-inline-styles` |
| DatePicker без вёрстки | `help.mantine.dev/q/dates-missing-styles` |
| слайды Carousel идут вертикально | `help.mantine.dev/q/carousel-missing-styles` |
| нотификации не там, где ожидалось | `help.mantine.dev/q/notifications-missing-styles` |
| белый экран после добавления нотификаций | `help.mantine.dev/q/notifications-empty-screen` |
| вспышка светлой темы на первой отрисовке | `help.mantine.dev/q/color-scheme-flickering` |
| warning про `data-mantine-color-scheme` | `help.mantine.dev/q/color-scheme-hydration-warning` |
| разный контент для light и dark | `help.mantine.dev/q/light-dark-elements` |
| «MantineProvider was not found» | `help.mantine.dev/q/mantine-provider-missing` |
| как поднять версии всех пакетов | `help.mantine.dev/q/how-to-update-dependencies` |
| Mantine в Server Component | `help.mantine.dev/q/server-components` |
| нужен DataGrid | `help.mantine.dev/q/data-grid-i-need` |
| `{value,label}` в Autocomplete или TagsInput | `help.mantine.dev/q/autocomplete-value-label` |
| чем Select отличается от Autocomplete | `help.mantine.dev/q/select-autocomplete-difference` |
| свой инпут внутри `useForm` | `help.mantine.dev/q/custom-input-use-form` |
| массив строк в `useForm` | `help.mantine.dev/q/list-of-strings-in-use-form` |
| тесты падают на Combobox | `help.mantine.dev/q/combobox-testing` |
| тесты падают на порталах | `help.mantine.dev/q/portals-testing` |
| доступны ли компоненты Mantine | `help.mantine.dev/q/are-mantine-components-accessible` |
| Mantine с Astro | `help.mantine.dev/q/can-i-use-mantine-with-astro` — ответ «нет»: Astro не поддерживает нужный React context |
| Mantine с CRA | `help.mantine.dev/q/can-i-use-mantine-with-cra` |

Про Tailwind v4 официальной страницы нет: `q/third-party-styles` написан под v3
и советует отключить preflight. В v4 причина другая — нативные cascade layers, и
рабочего ответа за подписью мейнтейнера не существует.
