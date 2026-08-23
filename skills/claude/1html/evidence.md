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

Скрипт `check_html.mjs` удалён 2026-08-23 («мы не будем проверять»); ниже —
исторический протокол прогона, а не действующая команда.

Команды: `node skills/claude/1html/scripts/check_html.mjs <fixtures...>`,
`node skills/claude/1html/scripts/check_html.mjs _workspace/HTML_artifacts/`,
`node --check skills/claude/1html/scripts/check_html.mjs`, `git diff --check`.
Финальный independent audit: `claude-opus-5` — PASS по границе правил; после
его замечаний checker ждёт `load`, на finding-path ставит `exitCode` без
принудительного выхода, а неверный input возвращает exit `2`. Redirect fixture
и запуск из `/tmp` — clean.

## План До Кода + Шапка Каталога 2026-08-20

Owner evidence:
`_ops/chat-recall/2026-08-20-224022-claude-1bc0a881.md` — жёстко вшить
процедуру планирования до кода; критерий приёмки — парный прогон «сработало
или нет». «Да» на пакет из двух правок — в той же сессии.

| Claim | Falsifier | Статус |
|---|---|---|
| Раздел меняет поведение | обе ветки перерисовывают анатомию одинаково | pass: без плана `background` 14, `border-radius` 10, `padding` 25, Daisy-классов 46, ни одного `card`; с планом 0 / 2 / 8, Daisy 133; живой провал 2026-08-20 — 8 фонов / 11 радиусов |
| План — не ритуал | строка плана не находится в готовом файле | pass: потолки CSS и все 13 чисел ширины совпали grep-ом; агент сам привёл план к коду после сборки |
| Геометрия не ломается | любая ветка падает smoke | pass: обе clean на 390/768/1440 |
| Шапка наследуется, не вспоминается | страница из шаблона без ссылки на каталог | pass: header в tracked template, обеих live zones и в fresh-seed странице `probe`; контроль — обе A/B-ветки без правила шапку не сделали |

Supersession: строка «Дизайн не шаблонизирован» блока Shared Zone выше
описывала scaffold без header; с этого решения владельца шапка-ссылка на
каталог входит в neutral scaffold и шаблонизацией не считается.

Границы: один прогон на ветку; SKILL ветки с планом длиннее на раздел.
Прогон: изолированные scratchpad-zones, общая галерея не тронута; промпт,
модель и материал идентичны, разница — только раздел «План До Кода».

## Оси Переиспользования + Примитивы Раскладки 2026-08-20

Owner evidence:
`_ops/chat-recall/2026-08-20-224022-claude-1bc0a881.md` — агенты создают новый
класс текста в каждой карточке вместо переиспользования дизайн-системы;
методологию доказывать в планах. Выбор владельца: две оси + reference.

Записано: оси «текст → ступень» (потолок: свой `font-size`/`font-family` = 0)
и «свой класс → отношение» (CSS == списку из плана) в «План До Кода»;
`references/layout-primitives.md` — Stack, Cluster, Switcher, Sidebar,
Grid auto-fit, Cover/Frame/Reel, правило `@media` == названным переломам,
container query. Маршрут открывается с оси «что на узком».

Статус: **candidate** — поведенчески не прогнано (владелец выбрал запись без
парного прогона). Структурная проверка: якоря вставок единственны, Codex-тело
и reference скопированы побайтово. Родословная словаря: type ramp, OOCSS,
utility-first, CUBE, Every Layout / intrinsic web design.

## Третий Прогон + Библиотека Классов Зоны 2026-08-20

Owner evidence:
`_ops/chat-recall/2026-08-20-224022-claude-1bc0a881.md` — телос: черновой
визуальный канал общения, один ход без глюков, чтение при любом окне браузера,
малый код → десятки быстрых вариантов; заготовленные классы зоны; выбор
«ноль по дефолту + объявленные», линтер только по явному запросу.

Три прогона, один промпт и материал (`how-1html-works`):

| Метрика | план v1 (4 оси) | без плана | план v3 (6 осей) |
|---|---|---|---|
| свой CSS, байт | 6 422 | 11 091 | **1 479** |
| `background` | 0 | 14 | 0 |
| `font-size` / `font-family` | 21 / 1 | 18 / 4 | **0 / 0** |
| своих классов | 37 | 59 | **5, все в плане** |
| `@media` | 4 | 5 | 0 |
| Daisy-классов | 133 | 46 | 90 |
| шапка на каталог | нет | нет | **да, из шаблона** |
| smoke 390/768/1440 | clean | clean | clean |

Инцидент прогона v3: страница легла слоями — имя `.stack` из прежней редакции
`layout-primitives.md` совпало с DaisyUI `stack` (стопка детей в одну клетку);
все счётчики и smoke слепы к наложению, поймано только скриншотом. Причина —
скелеты в reference для копирования. Ответ: классы установлены в
`assets/shared/components.css` всех зон под свободными именами (`flow`,
`cluster`, `switcher`, `with-sidebar`, `auto-grid`, `reel`; проверены grep-ом
по `lib/daisyui.css`), reference переписан с «копируй» на «используй» + ловушка
имён; `COMPONENTS.md` — таблица классов; zone `AGENTS.md` — строка «ноль по
дефолту»; ось «свой класс → отношение» начинается с поиска в готовом.

Линтер `scripts/lint_html.mjs` (advisory, по явному запросу, без браузера;
скрипт удалён 2026-08-23 по решению владельца «мы не будем проверять» —
ниже исторический протокол прогона):
классы CSS ⇔ план, `font-size`/`font-family` = 0, `@media` — инфо-счётчик.
Валидация: v3 — exit 0; v1 — 21 класс вне плана + 21 `font-size` пойманы.
Свежая зона наследует классы; обе живые зоны после добавки — smoke clean.

Статус: оси и библиотека подтверждены прогоном v3 по коду; наложение v3
исправлено установкой классов, но контрольного прогона v4 с установленной
библиотекой ещё не было.

## Автовызов По «Черновому Артефакту» 2026-08-21

Owner evidence:
`_ops/chat-recall/2026-08-21-010201-codex-01a020be.md:17-20` — skill должен
быть установлен в Codex и Claude; просьба сделать «черновой артефакт» должна
автоматически вызывать его; точная новая строка `description` одобрена.

| Claim | Falsifier | Статус |
|---|---|---|
| Каноническая фраза находится в hot zone routing metadata | первая фраза не содержит «черновой артефакт» и не называет автоматический выбор | pass: обе формы стоят в первой фразе `description` |
| Ближайший текстовый near-miss не присваивается | обычный текстовый черновик входит в заявленный trigger | pass на уровне контракта: первая отрицательная граница исключает обычный текстовый черновик |
| Claude и Codex получили один runtime-контракт | Claude-ссылка ведёт не к owner-у либо Codex `SKILL.md` отличается | pass: symlink target проверен; `cmp` tracked/Codex вернул `0` |
| Обе runtime-копии структурно валидны | любой `qv-skill` завершается ненулевым exit | pass: оба запуска вернули `Skill is valid!` |
| Свежая модель автоматически выбирает skill по голой фразе и пропускает near-miss | clean-window trace не читает `1html` на positive либо читает на negative | не прогнано: владелец запретил субагентов; отдельный model-runtime запуск в этом ходе не выполнялся, claim остаётся candidate до свежей ручной сессии |

Codex config: `/Users/triton/.codex/config.toml:733-734` указывает на
установленный `SKILL.md` и держит `enabled = true`. Изменение каталога требует
новой сессии или перезапуска runtime.


## 2026-08-23 — Редакция «Дизайн Золотого Стандарта»

Claim: центр скила перенесён на дизайн-стереотипы; проверки сняты; «План До
Кода» сохранён и расширен седьмым присвоением.

Evidence на этот момент — **два независимых аудита в отдельных окнах**, каждый
до первого суждения прочитал живые пакеты `1skill-shaping` и
`1instruction-shaping` целиком.

- Линза «лишнее»: нагрузка тела 104 → 83 обязанности (метод — построчный
  проход, знание не считается); с учётом снятого `readable-design.md` — 120 →
  83, то есть −31%. Байты тела 19 216 → 13 872. Вердикт «это укорачивание, а не
  упрощение» принят: реальное падение нагрузки дал только снятый reference.
- Линза «потерянное и выдуманное»: 12 позиций потерь с цитатами владельца и
  адресами; 7 из них восстановлены в финальном тексте, остальные записаны в
  `cut.md` с причиной. Обе линзы независимо забраковали присвоение «страница →
  дизайн-ход» как обещание поведения — заменено.

**Непроверенное, названо явно.** Семиосевой план в живой работе не прогонялся:
парные замеры выше меряли планы из четырёх и шести осей. Claim «новая редакция
плана держит тот же уровень своего CSS» — `candidate`. Claim «страницы перестали
выглядеть как документация» не проверен вовсе: он проверяется только живой
страницей, собранной под новой редакцией.
