---
name: 1tailwind-dev
description: >-
  Use for Tailwind version, compatibility, or regression on v4.1.12–v4.3.3,
  @tailwindcss/webpack, Vite 8, @container-size, scrollbar-*, logical
  properties, @variant, or @utility; not routine styling.
---

# Tailwind CSS v4.1.12–v4.3.3 delta — проверено 2026-08-22

- **[v4.3.3](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.3) (2026-07-16):** это последняя опубликованная стабильная версия в официальном GitHub Releases на 2026-08-22.

## v4.1.12–v4.1.14 — 2025-08-13…2025-10-01

- **[v4.1.12](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.12) (2025-08-13):** `@apply` перестал учитывать global important state; `@tailwindcss/postcss` получил `transformAssetUrls: false` для отключения URL rebasing; source locations начали проходить через `@plugin` и `@config`.
- **[v4.1.13](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.13) (2025-09-03):** utility `transition` перестал включать `visibility`, `sr-only` перешёл с deprecated `clip` на `clip-path`, а `.vercel` стал ignored source по умолчанию с возможностью вернуть его через `@source`.
- **[v4.1.13](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.13) (2025-09-03):** custom variant names больше не могут начинаться или заканчиваться на `-`/`_`; upgrader мигрирует JS theme keys `aria`, `data` и `supports` в `@custom-variant`.
- **[v4.1.14](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.14) (2025-10-01):** заработал `@variant` внутри `@custom-variant`; `@tailwindcss/vite` перешёл на `default` export condition; upgrade tool начал показывать version mismatch и мигрировать первый класс внутри `className` и классы в `*ClassName`/`*Class` attributes.

## v4.1.15–v4.1.18 — 2025-10-20…2025-12-11

- **[v4.1.15](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.15) (2025-10-20):** important utility перестала влиять на другие utilities; исправлен resolve JS theme keys, имя которых начинается с имени другого key; upgrader мигрирует deprecated `break-words` в `wrap-break-word`.
- **[v4.1.16](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.16) (2025-10-23):** исправлены canonicalization arbitrary variants с attribute selectors и invalid colors из nested `&`; такие симптомы на v4.1.15 и ниже являются patch-level traps.
- **[v4.1.17](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.17) (2025-11-06):** `@variant` начал подставляться внутри legacy JS APIs; исправлен occasional crash на Windows при загрузке Tailwind в worker thread.
- **[v4.1.18](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.18) (2025-12-11):** validation `source(…)` стала relative к содержащему CSS-файлу; `@tailwindcss/vite` получил environment API; JS configs/plugins начали сохранять case theme keys и корректно обрабатывать defaults вроде `ringColor.DEFAULT`.
- **[v4.1.18](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.1.18) (2025-12-11):** CLI перестал зависать при output `/dev/stdout` и начал правильно писать source maps в `--watch`; upgrader начал обрабатывать `future` и `experimental` config keys.

## [v4.2.0 — 2026-02-18](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.2.0)

- **v4.2.0 (2026-02-18):** появился отдельный loader `@tailwindcss/webpack`; в опубликованном Tailwind Labs замере на docs-сайте с Next.js/Turbopack он занял 429 ms против 932 ms у поддерживаемого `@tailwindcss/postcss`.
- **v4.2.0 (2026-02-18):** добавлены logical-property families `pbs-*`/`pbe-*`, `mbs-*`/`mbe-*`, `scroll-pbs-*`/`scroll-pbe-*`, `scroll-mbs-*`/`scroll-mbe-*`, `border-bs-*`/`border-be-*`, `inline-*`/`min-inline-*`/`max-inline-*`, `block-*`/`min-block-*`/`max-block-*` и `inset-{s,e,bs,be}-*`.
- **v4.2.0 (2026-02-18):** прежние logical inset utilities `start-*` и `end-*` объявлены deprecated в пользу `inset-s-*` и `inset-e-*`; v4.2.3 canonicalization уже мигрирует эти имена.
- **v4.2.0 (2026-02-18):** default theme получил палитры `mauve`, `olive`, `mist` и `taupe`; код, считающий `gray`/`zinc`/`neutral`/`stone`/`slate` полным набором нейтральных палитр, устарел.
- **v4.2.0 (2026-02-18):** добавлен `font-features-*` для `font-feature-settings`; `tabular-nums` остаётся более высоким готовым utility для `"tnum"`, а `font-features-*` закрывает font-specific OpenType features.

## v4.2.1–v4.2.4 — 2026-02-23…2026-04-21

- **[v4.2.1](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.2.1) (2026-02-23):** исправлено обнаружение классов с `.` внутри фигурных скобок в MDX и возвращена backward compatibility для functional utility names с завершающим дефисом; на v4.2.0 оба случая являются version-specific suspects.
- **[v4.2.2](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.2.2) (2026-03-18):** официальная поддержка Vite 8 в `@tailwindcss/vite` начинается только здесь; v4.2.1 и ниже не являются поддерживаемой парой для Vite 8.
- **[v4.2.3](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.2.3) (2026-04-20):** upgrade tool начал использовать `config.content` при миграции v3→v4, не трогать gitignored files и не опустошать файлы при прерывании процесса; для этих гарантий v4.2.2 и ниже недостаточно.
- **[v4.2.3](https://github.com/tailwindlabs/tailwindcss/pull/19803) (2026-04-20; PR merged 2026-03-20):** `@tailwindcss/vite` получил resolution `tsconfig` path aliases для CSS `@import` и JS `@plugin`; эта поддержка отсутствует в tagged v4.2.2, несмотря на ошибочную группировку PR #19803 под v4.2.2 в текущем `main` changelog.
- **[v4.2.3](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.2.3) (2026-04-20):** `@tailwindcss/webpack` начал считать imports с разными query params разными ресурсами; одинаковое кэширование таких imports на v4.2.2 и ниже — известная version trap.
- **[v4.2.4](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.2.4) (2026-04-21):** `@tailwindcss/vite` исправил resolution `@import` и `@plugin` через Vite aliases; если alias существует, но импорт не находится на v4.2.3 и ниже, сначала подозревается версия.

## [v4.3.0 — 2026-05-08](https://tailwindcss.com/blog/tailwindcss-v4-3)

- **v4.3.0 (2026-05-08):** добавлены first-party `scrollbar-{auto,thin,none}`, `scrollbar-thumb-*`, `scrollbar-track-*` и `scrollbar-gutter-{auto,stable,both}`; сторонний scrollbar plugin больше не является обязательным для этих CSS APIs на v4.3+.
- **v4.3.0 (2026-05-08):** `@container` по-прежнему создаёт inline-size container, а новый `@container-size` создаёт size container и открывает block-axis units вроде `cqb`/`cqh`; named form — `@container-size/{name}`.
- **v4.3.0 (2026-05-08):** появились `zoom-*` для CSS `zoom` и `tab-*` для `tab-size`, включая arbitrary values и CSS-variable forms.
- **v4.3.0 (2026-05-08):** CSS directive `@variant` впервые принимает stacked form `@variant hover:focus` и compound form `@variant hover, focus`.
- **v4.3.0 (2026-05-08):** functional `@utility` впервые поддерживает `--default(…)` внутри `--value(…)` и `--modifier(…)`, поэтому одна utility family может иметь bare fallback и именованные значения.
- **v4.3.0 (2026-05-08):** `@tailwindcss/vite` исправил выбор JavaScript entry для `@plugin`, relative resolution `@import`/`@plugin` и обработку CSS-файлов с `@variant`; эти симптомы на v4.2.x могут быть plugin-version bugs.

## v4.3.1–v4.3.3 — 2026-06-12…2026-07-16

- **[v4.3.1](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.1) (2026-06-12):** `@tailwindcss/webpack` можно устанавливать в Rspack без `webpack` peer dependency; `@apply` начал работать с CSS mixins; `@tailwindcss/cli --watch` начал восстанавливаться после удаления и возврата tracked dependency.
- **[v4.3.1](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.1) (2026-06-12):** `@source` сохраняет symlink globs, поздний `@source` может повторно включить ранее исключённые файлы, а явно указанные директории сканируются даже при gitignore; более ранние v4.3.0/v4.2.x могут терять кандидаты в этих конфигурациях.
- **[v4.3.2](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.2) (changelog 2026-06-26; GitHub publication 2026-06-29):** исправлены crash `@tailwindcss/cli --watch` на Windows при несуществующей `@source`-директории, crash Vite HMR при удалении scanned paths и лишнее сканирование sibling paths из `@source` patterns.
- **[v4.3.2](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.2) (changelog 2026-06-26; GitHub publication 2026-06-29):** исправлены type errors `@tailwindcss/postcss` с более новыми PostCSS patch releases; конфликт на v4.3.1 и ниже может быть несовместимостью patch-level, а не ошибкой CSS.
- **[v4.3.3](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.3) (2026-07-16):** CLI получил `--watch --poll[=ms]` для файловых систем без надёжных events; one-off builds и polling watch больше не требуют успешно загруженного `@parcel/watcher`.
- **[v4.3.3](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.3) (2026-07-16):** `@tailwindcss/postcss` начал перестраивать CSS, когда Sass или другой preprocessor меняет вход без изменения input file на диске; `theme('colors.foo')` в JS plugins исправлен для одновременных `--color-foo` и `--color-foo-bar`.
- **[v4.3.3](https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.3.3) (2026-07-16):** `@tailwindcss/upgrade`, запущенный из подпапки, перестал переписывать ignored files; для безопасной зависимости от этого поведения нужен минимум v4.3.3.
