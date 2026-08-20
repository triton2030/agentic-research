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
- design template, общий visual language и component anatomy как package
  contract.

### Оставлено

- один нейтральный page scaffold, чтобы начать без boilerplate;
- один shared `lib/` с локальными pinned runtimes;
- один `assets/shared/` с adapters и пустым zone-owned `components.css`;
- Table, Mermaid, ECharts и React Flow как доступные носители, не обязательные
  страницы или presets;
- каталог flat HTML и legacy directory entries на время естественного перехода;
- одна папочная stance: визуально объясняй, сохраняй design freedom, исправляй
  общего владельца геометрии вместо device-specific patch;
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
