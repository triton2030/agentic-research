# Evidence

## Shared Visual Explainer Zone 2026-08-20

Owner evidence:
`_ops/chat-recall/2026-08-19-212344-codex-01a01ad4.md` — одна общая папка
артефактов, один набор components/styles/libraries, многократное reuse разными
HTML; без лишних проверок и дополнительных шагов.

| Claim | Falsifier | Статус |
|---|---|---|
| Генератор создаёт flat page | после вызова существует directory `<slug>/` или нет `<slug>.html` + `assets/<slug>.css` | pass: `/tmp/1html-shared-zone.SJU8Jw`, `alpha` и `beta`, directories отсутствуют |
| Shared layer действительно один | две страницы получают собственные copies `lib/assets` либо используют разные runtime paths | pass: обе страницы ссылаются на root `lib/` + `assets/shared/`; runtime существует один раз |
| Folder stance одна | генератор создаёт больше одного `AGENTS.md` или дублирует полную инструкцию в каждой странице | pass: один root `AGENTS.md`; его hash после второй страницы не изменился |
| Дизайн не шаблонизирован | page scaffold содержит layout, cards, header, rail, node anatomy или fixed geometry | pass: scaffold содержит только semantic `main/h1`, local links и единый `data-theme="cupcake"` |
| Обычный путь свободен от QA | `SKILL.md` требует audit/check/finish/browser/screenshot или add-on installer | pass: старые scripts/reference удалены; SKILL явно исключает QA-loop |
| Каталог понимает flat pages | созданная страница отсутствует в payload или ссылка ведёт в `<slug>/index.html` | pass: payload содержит `alpha.html` и `beta.html` |
| Legacy артефакт не ломается | каталог перестаёт видеть существующий directory artifact | pass: synthetic `legacy-page/index.html` остаётся в payload |
| Shared CSS не становится второй component library | `assets/shared/components.css` задаёт palette или повторяет Daisy component anatomy | pass: файл оставляет только повторившийся carrier, которого нет в Daisy; page composition остаётся в `assets/<slug>.css` |
| Zone snapshot не смешивает поколения | следующая страница берёт новый skill scaffold при старых local instructions/runtimes | pass: runtime, instructions, carrier map и оба neutral templates создаются only-if-missing; новая страница читается из local snapshot; catalog projection обновляется отдельно |
| Base icon carrier работает без skill/QA | `<i data-lucide>` остаётся пустым, потому что local runtime подключён, но не инициализирован | pass: neutral template регистрирует `DOMContentLoaded → lucide.createIcons()`; COMPONENTS называет automatic/manual boundary |
| Существующая чужая инструкция не уничтожается | генератор молча перезаписывает `AGENTS.md` без generated marker | pass: `/tmp/1html-shared-foreign.Yv4iXS`, hash до/после одинаков |
| Package не содержит старый workflow | остаются bundle/finish/audit/add-on installer scripts | pass: file/name/content scan; scripts остались `new`, `rebuild`, metadata, catalog builder |
| MAVO migration сохраняет страницу | CSS или видимая шапка меняются; старый URL пропадает | pass: CSS byte-identical; прежние home-link/icon/title перенесены из runtime в static HTML; old-path directory содержит только redirect; catalog href один — `whatsapp-order-interface.html` |
| Stance меняет attractive solution | unseen nested/overlay/responsive prompt после чтения кандидата всё ещё даёт repeated cards или compensating breakpoint | pass: `../behavior-comparator.md`; control — четыре peer cards и три media blocks, treatment — physical nesting, разные carriers и один named composition breakpoint |
| Палитра имеет одного владельца | scaffold, catalog, shared adapters или Visual Systems Lab вводят literal palette, старые `--artifact-*` aliases либо тему кроме `cupcake` | pass: first-party grep пуст; удалён generated `catalog-theme.css`; catalog/scaffold используют `data-theme="cupcake"` |
| Surface/content роли не смешаны | data ink берётся из surface token либо `neutral-content` используется на base | pass: ECharts, Mermaid и React Flow берут foreground/lines из `primary-content`/`secondary-content`/`accent-content` и base roles; paired Daisy components выбирают content сами |
| Peer categories не маскируются status-цветами | chart с >3 равноправными категориями расширяет palette через `info/success/warning/error` | pass: Sankey, treemap и donut задают authored `option.color` из brand/base roles и `color-mix()`; catalog count использует `badge-primary` |
| Daisy экономит код без захвата композиции | повторяемые card/badge/button/alert/avatar состояния снова нарисованы локальным CSS либо React Flow node получает фиксированную структуру | pass: Visual Systems Lab использует Daisy card/badge/btn/collapse/avatar-group; runtime error/pause/edge label используют alert/btn/badge; node HTML остаётся произвольным template |

Package smoke: `bash -n`, `shellcheck`, `ruff --no-cache`, `node --check` всех
authored adapters, `qv-skill` и `md check` (`16` targets) — pass. Fresh zone:
`alpha` + `beta`, matching instruction/adapter hashes, cupcake catalog, no
`catalog-theme.css`. Live browser: обе zones clean на `390/768/1440`; Visual
Systems Lab — `6/6` ECharts, `3/3` Mermaid и React Flow ready, без runtime errors,
network requests и horizontal scroll. Computed axis/diagram line — Daisy
base-content/base-100 mix; React edge label — `12px` на непрозрачном base-paper.
Reduced-motion render: opacity `1`, active animations `0`. Mavo сохраняет
утверждённый прежний WhatsApp-style как локально записанное исключение, а не как
palette source новых страниц. Три независимых `claude-opus-5` audit-lens:
Daisy/custom ownership — PASS; два точных projection blocker-а устранены sync-ом
и повторно сверены побайтово. Владелец утвердил кандидат; Claude symlink и обе
live zones проецируются из tracked owner, Codex projection синхронизирован после
audit.

## Conservative HTML Smoke 2026-08-20

Owner evidence:
`_ops/chat-recall/2026-08-20-171854-codex-01a01f1a.md:19-21` — будущие tests
должны быть верхнеуровневыми и переносимыми; текущий checker оставляет только
самые очевидные сигналы с низким риском ложной тревоги.

| Claim | Falsifier | Статус |
|---|---|---|
| Smoke не судит visual intent | line-clamp, полностью закрытый overlay, local `blob:` worker или full-bleed дают finding | pass: все четыре fixture завершились с exit `0` |
| Отсутствующий local asset ловится | `<img src="missing.png">` проходит | pass: `local request failed` на 390/768/1440, exit `1` |
| Offline boundary ловится без `blob:` noise | `http://127.0.0.1:9/...` проходит либо local blob-worker падает | pass: HTTP — `forbidden network request`; blob — clean |
| Runtime errors ловятся | явный `console.error` или async uncaught exception проходит | pass: `console` и `pageerror` на трёх ширинах, exit `1` |
| Только реальный page-level horizontal scroll считается вылетом | 900 px element на узких viewport проходит либо `width:100vw` full-bleed падает | pass: 530/152 px travel пойман; full-bleed clean |
| Живые артефакты не создают ложных тревог | Visual Systems Lab или каталог падает | pass: обе страницы clean, exit `0` |

Команды: `node skills/claude/1html/scripts/check_html.mjs <fixtures...>`,
`node skills/claude/1html/scripts/check_html.mjs _workspace/HTML_artifacts/`,
`node --check skills/claude/1html/scripts/check_html.mjs`, `git diff --check`.
Финальный independent audit: `claude-opus-5` — PASS по границе правил; после
его замечаний checker ждёт `load`, на finding-path ставит `exitCode` без
принудительного выхода, а неверный input возвращает exit `2`. Redirect fixture
и запуск из `/tmp` — clean.
