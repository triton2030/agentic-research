# Вырезано — с причиной

## Shared Zone 2026-08-20

Поздняя коррекция владельца отменила модель автономного bundle на каждый
артефакт. Текущий owner: одна `_workspace/HTML_artifacts/`, один набор shared
возможностей и много самостоятельных HTML-файлов. См.
`_ops/chat-recall/2026-08-19-212344-codex-01a01ad4.md`.

### Снято

- per-artifact directory, повторные `lib/` и `assets/`;
- bundle version marker и migration/legacy modes;
- `finish_html_bundle.sh`, blocking validator и advisory clipping/occlusion
  audit, который судил visual intent;
- add-on installer scripts и HTML wiring parser;
- обязательные audit, browser-loop, screenshot matrix и command evidence в
  обычной работе;
- design template, отдельная authored-палитра и custom component anatomy как
  package contract.

### Оставлено

- один composition-neutral page scaffold с DaisyUI `cupcake`, чтобы начать без
  boilerplate и без выбора второй палитры;
- один shared `lib/` с локальными pinned runtimes;
- один `assets/shared/` с adapters и zone-owned `components.css` только для
  повторившегося carrier, которого нет в Daisy;
- Table, Mermaid, ECharts и React Flow как доступные носители, не обязательные
  страницы или presets;
- каталог flat HTML и legacy directory entries на время естественного перехода;
- одна папочная stance: визуально объясняй, сохраняй design freedom, исправляй
  общего владельца геометрии вместо device-specific patch;
- DaisyUI владеет совпавшей component-анатомией и состояниями; artifact —
  уникальными отношениями и composition; все authored carriers используют
  semantic tokens `cupcake` вместо второй палитры;
- advisory HTML smoke по явному запросу: только browser/runtime facts без
  суждения о clipping, пересечениях, overlay или красоте.

### Почему Не Только Папочная Инструкция

При первом создании zone ещё не существует. Codex также собирает цепочку
`AGENTS.md` от корня до своей рабочей директории и не гарантирует чтение
descendant-файла, если сессия запущена выше. Поэтому `SKILL.md` владеет первым
входом, а `HTML_artifacts/AGENTS.md` — быстрым повторным поведением внутри zone.
Это разные моменты, не две копии полного workflow.

### Не Добавлено

- generic geometry linter: он не знает visual intent и снова сделал бы дизайн
  процедурой; технический smoke намеренно не занимает эту роль;
- обязательный render audit: владелец выбрал скорость и правильную рабочую
  позицию вместо ritual compliance;
- автоматическая миграция существующих directory-artifacts: она ломала бы
  текущие ссылки без пользы для новых страниц. Живой WhatsApp artifact
  мигрируется отдельно с redirect по старому URL и без второй копии runtime.

## 2026-08-23 — методы объяснения и visual-first

Заказ владельца: «главная цель /1html» — методы понятного и приятного
объяснения из 123-explain; «использование просто слов было нежелательно,
всё что можно показать визуально обязательно было показано визуально и
креативно». Одно окно аудита + дельта.

- Указатель на «Форму Ответа» 123-explain сужен до языка: вёрстка, эмодзи и
  таблицы чата на страницы не берутся (владельцы — readable-design и «План
  До Кода»).
- «Первый экран без прокрутки» и «вердикты не откладываются» — сняты:
  четвёртый носитель смысла readable-design/compact-disclosure/Границ.
- Разрешение «заголовок-вопрос × заголовки-outline» живёт у владельца
  заголовков в readable-design.
- Честность аналогий поглощена существующим правилом «Комментарий агента —
  … или аналогию — назови и отдели».
- «Разнообразие режимов» как ценность — снято: усиление идёт лестницей
  visual-routing «до порога», не выше.
- Решение «отношения нет — проза» получило след в присвоении плана; прозе
  явно оставлены подпись, связка, короткий вывод и текстовое резюме визуала.
- Гейт «читается с удовольствием» заменён счётным следом: термины пояснены,
  трудный механизм — с помеченной аналогией.
