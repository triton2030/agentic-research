# FlowPage v4 Agent Instructions

## Цель

Этот experiment — локальный viewer графов с ручной правкой и явным
ELK-пересчётом. Контент графов пишет агент в `src/pages/*.js`, пользователь
смотрит и шлифует canvas.

## Перед Правкой

- Сначала прочитай `цель.md`: это пользовательская правда этого experiment.
- Для механики приложения читай `TECHNICAL.md`.
- Для авторства новых графов читай `GRAPH-AUTHORING.md`.
- Для общего входа и сценариев читай `README.md`.

## Инварианты

- Один граф = один snapshot-файл `data/layouts/<id>.json`.
- Snapshot хранит `positions`, `routes`, `viewport`, `options`, `direction`.
- Не добавляй скрытые browser-state источники для графов, layout или ELK-пресета.
- Новые графы добавляются как файлы `src/pages/<slug>.js`, не через UI-editor.
- `Apply ELK` — единственный путь от ELK-пресета к новой геометрии.
- Load страницы — чистое чтение snapshot'а, без автоматического ELK.

## Язык Графов

Весь видимый текст графов пиши по-русски: `title`, `description`, `kicker`,
`body`, `bullets`, `label`, `tooltip`, подписи рёбер и заметки.

Английский оставляй только для точных названий: файлов, API, команд, скиллов,
компонентов, значений `kind`, Material Symbol names и кода. Если точное
английское имя видно человеку, рядом дай русскую роль или пояснение.

## Material Icons

Для Material Icons используй `materialIcon({ icon, label?, tooltip? })` из
`src/pages/_helpers.js`. `icon` — точное Material Symbol name, `label` и
`tooltip` — по-русски.

## Критерии Перед Работой

- Код, структура, cleanup, runtime boundaries:
  `_ops/criteria/repo-structure-and-runtime-guards.md`.
- Формулировка instruction-файлов и language quality routing rules:
  `_ops/criteria/instruction-layer.md`.
- Folder graph, paired shim, system coherence, structural mechanism:
  `_ops/criteria/folder-contract.md`.
- Агентная дисциплина и чтение локального контекста:
  `_ops/criteria/agent-discipline.md`.
- Closeout и evidence:
  `_ops/criteria/work-review-and-evidence.md`.
