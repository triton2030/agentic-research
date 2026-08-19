# Evidence

## Design-free Visual Explainer 2026-08-20

Owner evidence:
`_ops/chat-recall/2026-08-19-212344-codex-01a01ad4.md` — отказ от обязательных
templates; `1html` как спасение от стены текста; charts/flows/timeline/motion,
progressive disclosure; React Flow только без dev server и с наследованием
palette; автономное завершение и финальный Opus review.
Поздние коррекции: полная свобода содержимого React Flow nodes, мощная
data-viz capability с examples и сохранение старого тёплого стиля живого
WhatsApp artifact (`:39-42`).

| Claim | Falsifier | Статус |
|---|---|---|
| Scaffold не владеет дизайном | fresh bundle не содержит theme, shell, cards, rail, page template/project runtime; два радикально разных designs проходят один `finish` | pass: harness `124`; fresh-agent timeline и dark nested flow оба green |
| Show-don't-tell меняет выбор | fresh-agent создаёт plan как timeline и system flow как visual relation, а не карточки с пересказанными абзацами | pass: `/tmp/1html-forward-proof`, `violations=0` ×2 |
| Blocking gate не замораживает composition | arbitrary first-party HTML/CSS/JS проходит; broken technical shell, local resource/tag/add-on/vendor contract падает | pass: `124 design-free bundle contract checks`; media-only `.card` и unrelated custom classes pass, text `.card` без direct `.card-body` and accidental `.hero` fail |
| Add-on helper не зависит от formatting | one-line HTML, reordered attrs и markers в comments/code не ломают и не активируют wiring; повторный run byte-idempotent | pass: parsed source-span wiring + harness minified/false-marker fixtures |
| Source gate совпадает с browser config boundary | strict JSON отвергает `NaN`; React Flow `data` только object; ECharts labelled element непуст; legacy не получает current add-on schemas | pass: exact negative fixtures в harness; previous-generation host passes only explicit `--legacy` |
| React Flow автономен и не задаёт node anatomy | local helper → `file://`; 3 icon-only + 2 unrelated rich nodes; zero network/errors; disclosures, resize, pan/zoom, palette inheritance, animated/reduced-motion edge | pass: `/tmp/1html-react-freedom.KXGpyn/evidence`; 5 nodes, 4 edges, widths 78–352 px, details 0/2/0/3/0, edge recompute true |
| ECharts даёт разнообразие без page template | один local runtime рендерит bar/line/scatter/Sankey/treemap из independent JSON recipes; HTML summary остаётся source | pass: `/tmp/1html-echarts-proof.LsbgV5/evidence`; 5 SVG, 0 canvas/network/errors, ARIA role/label, inherited palette, reduced-motion `animation=false` |
| Zero-size/hidden charts не дают green-but-empty runtime | ECharts host без authored height и host внутри закрытого details монтируются после technical fallback/resize; React Flow bridge не задаёт frame/surface | pass: `/tmp/1html-final-browser-proof`; ECharts `1120×320` SVG ×2 after toggle; React Flow exact bridge `1400×448`, 5 nodes, border 0, transparent background, pageerrors/remote responses 0 |
| Автономность защищена в browser, не только regex | current page требует local-only CSP; dynamic beacon/image/script/worker route не получает remote response | pass: browser probe — remote script/image attempts `requestfailed: csp`, responses `0`; source harness blocks missing CSP |
| Mermaid не приносит второй visual language и не рушит страницу при ошибке | warm serif/palette наследуются; malformed definition оставляет readable source, ставит error marker и не создаёт pageerror | pass: `/tmp/1html-mermaid-final-proof`; valid SVG font/colors match artifact, invalid `data-mermaid-error=parse`, remote/errors `0` |
| Current web capabilities не являются hype-list | reference называет stable/progressive/experimental status и fallback по current WHATWG/MDN | pass: source review + `md check` 14 targets, 0 issues |
| Живой WhatsApp artifact не потерял любимый стиль | hash/style before final sync; rail/header regression metrics | pass: SHA `7f9b2923…b4598b30`, `editorial`, warm `rgb(244,240,231)`, serif h1; rail 0; header padding `12×16`, radius 18, border 1 |
| Claude и Codex projections одинаковы | exact tracked owner copied to both install surfaces and validated | pass: `qv-skill` ×2, common-tree `diff -qr --exclude=agents` empty, installed owner harness `PASS: 124` |
| Exact candidate принят независимо | architecture/developer attacks закрыты exact regressions/browser proof; свежий Opus читает неизменный candidate и ищет core blocker | pass: final `claude-opus-5`, effort `max`, verdict `APPROVE`; warning только `permission_denied:Bash`, поэтому local executable evidence принадлежит Codex-прогонам выше |

## Рефактор 2026-08-19

Support envelope: Claude Fable 5, Claude Code harness, макс. reasoning;
проверялось на macOS, локальный bundle DaisyUI 5.7.4 / Alpine 3.15.12.

| Claim | Falsifier | Результат |
|---|---|---|
| Скелет starter работает конец-в-конец | `new_html_bundle.sh` в чистый корень: bundle создан, каталог собран, title взят из `h1` скелета | pass |
| Скелет легче без потери shell | 11 916 → 2 282 байт; рендер: topbar «Все проекты», rail, hero на месте | pass (скриншот, live server) |
| Все снипеты structure-patterns.md рендерятся фирменно | пробный artifact со всеми блоками: скриншоты grid/details/table/alert/tabs/toggle; bounding boxes steps 172×192, timeline 683×89, stats 148×239, tabs 683×114 | pass |
| Синтаксис снипетов соответствует bundle | точечная сверка с `references/daisyui-llms.txt` (tabs radio, steps, timeline, stats, table); первая сверка пропустила `role="alert"`/`role="tablist"` — поймано аудит-линзой, добавлено и перепроверено | pass после починки |
| Имена иконок существуют | grep по `references/lucide-icon-names.txt`: badge-alert, badge-help, circle-check, lightbulb, octagon-alert, triangle-alert | pass |
| Потери и выдумки рефактора | два независимых окна-линзы по контракту 1skill-shaping (лишнее · потерянное/выдуманное): 18 находок, 16 починено тем же ходом, 1 отклонена (усечённая цитата у линзы), 1 оставлена решением владельца (шпаргалка в теле) | pass после починки |

Не проверялось: routing (`description` не менялся); поведение свежего окна на
живой задаче создания артефакта по новой версии — первый боевой прогон и есть
следующий falsifier.

## Боевой прогон 2026-08-19

| Claim | Falsifier | Результат |
|---|---|---|
| Скилл даёт телеграфные артефакты фирменной разметкой | живой прогон свежим окном (артефакт whatsapp-order-interface) | fail: проза 857 слов, голые карточки без отступов, плейсхолдер в шапке — владелец забраковал |
| Страховка `:not(:has(> .card-body))` возвращает отступы голой карточке | инъекция правила в забракованный артефакт: computed padding 22px / 27-30-28-34 | pass |
| Починки корней (дефолт в телеграф-правиле, цепочка классов в шпаргалке, пустой title, снипет шага) | следующий боевой прогон свежим окном | не проверено — очередной falsifier |

## Программный structure gate 2026-08-19

Support envelope: Python 3.14.7, Bash, agent-browser 0.34.0; реальный artifact
`whatsapp-order-interface`, локальный starter и установленная Codex-проекция.

| Claim | Falsifier | Результат |
|---|---|---|
| Неканонический `artifact-*` нельзя сдать | `audit_html_style.py --check-structure` на забракованном artifact до ремонта; затем `finish_html_bundle.sh` на malformed smoke fixture | pass: реальный artifact дал exit 1 и ровно 7 `index.html:line`; finish дал exit 1, catalog hash не изменился |
| Каноническая структура проходит единый handoff | семь roots приведены к `card artifact-* > .card-body`, затем `finish_html_bundle.sh` | pass: 2 HTML, 0 нарушений; catalog пересобран, обе ссылки напечатаны |
| Визуальный padding не исчезает во время незавершённой разметки | agent-browser computed styles на starter: голый root против канонического root/body | pass: bare root 22px; canonical root 22px, body 0px |
| Исходная страница снова имеет внутренние отступы | agent-browser computed styles семи исправленных блоков | pass: verdict body 27/30/28/34px; шесть card body 22px |
| Advisory interface не превратился в blocker | однопараметрический `audit_html_style.py` на том же artifact | pass: прежний banner, exit 0; owner divergence остаётся advisory finding |
| Новый bundle завершает lifecycle одной командой | `new_html_bundle.sh smoke`, затем `finish_html_bundle.sh smoke` в чистом `/tmp` root | pass: 2 HTML, 0 нарушений, artifact/catalog links |
| Codex получает тот же общий runtime | `diff -qr --exclude=agents` tracked Claude owner против live Codex projection + `qv-skill` | pass после sync |

## Full skill stress-test 2026-08-19

Support envelope: Python 3.14.7, Bash, ruff, shellcheck, Chromium;
desktop 1440 px, mobile 390 px; exact candidate `/tmp/1html-candidate.gQ9Bhi`.

| Claim | Falsifier | Результат |
|---|---|---|
| Blocking gate ловит доказанные bundle failures, но не замораживает starter-composition | source-only harness: negative fixtures + две independently written positive pages | pass: `88 source-only bundle contract checks` |
| Новый bundle защищает shared design owner, старый не принуждается к миграции | same-generation marker ловит core/template/notices/licenses/active add-on drift; реальный pre-marker WhatsApp и simulated previous-generation завершают `finish --legacy` | pass: `mode=legacy`, `violations=0`; без flag любой non-current marker отклонён, current marker в legacy отклонён |
| Multi-page navigation не может быть неполной или вычисляемой | static JSON schema + exact live-page multiset + unchanged template copy/base URL fixtures | pass: missing, duplicate, computed, invalid config, template marker и `<base>` блокируются до catalog mutation |
| Starter убирает дефекты из запроса | computed geometry шапки, rail/footer count, overflow на 1440/390 | pass: header padding `12×16`, radius `18`, border `1`; rail `0`, footer `0`, overflow `0` |
| Карточки и сравнения не дают пустых высоких/сиротских блоков | 1–5 card matrix с primary и без; compact side-by-side desktop/mobile | pass: нечётный остаток full row; compact height `100.5px`, padding `22px`, radius `18px` |
| Table/Mermaid helpers дают готовую mobile-safe feature | fresh helper install, render, repeated install, console/overflow | pass: table `366/704` в wrapper при document `390/390`; Mermaid ready, SVG, 1 toolbar, 4 buttons, errors `0`; legacy inline-init compatibility проверена synthetic-equivalent fixture, потому что ранее найденный real corpus отсутствовал при финальном прогоне |
| Prototype template не перекрывает clean screen и не схлопывает comments | default/loading/empty/comments renders; panel width/overflow desktop/mobile | pass: default closed; comments `720×132` / `366.6×172`, `overflow-y:auto` |
| Изменённые scripts/package валидны | `bash -n`, `shellcheck`, targeted `ruff`, `quick_validate.py` | pass; full scripts `ruff` имеет один pre-existing import-order finding в неизменённом `artifact_metadata.py` |
