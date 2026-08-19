# Evidence

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
