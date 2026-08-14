# Происхождение правил — 1design-review

## v2, 2026-08-13, agentic-research

Recall владельца: `_ops/chat-recall/2026-08-13-153240-codex-019ffa9f.md`.

Класс: поведенческий hybrid с browser-native инструментальным слоем. Дефицит
словами владельца: целый screenshot перегружает визуальное внимание агента;
мелкий дефект кнопки или локальной типографики теряется, а итог субагента нельзя
принимать без повторной проверки root-ом.

| Правило | Источник |
|---|---|
| Один owner объединяет screenshot-design, design-subagents и design-review | владелец, recall:15 |
| Substantive review дробится на много question-specific screenshots | владелец, recall:16-17 |
| Root, а не aggregate-agent, принимает или отклоняет finding | владелец, recall:18 |
| Text-density = белый фон + красные text blocks; spacing = отдельная карта без контента | владелец, recall:19 |
| Family collage содержит не больше четырёх явно выбранных элементов | владелец, recall:20 |
| Skill записывается и проверяется на Kumysbekov | владелец, recall:21 |
| Один ordinary crop получает один open-ended material-defect task | два независимых cognitive audit V3; устраняет старое group × 8 lenses |
| Manifest хранит provenance, но не scheduler state | Fresh Eyes Solvent; проверено live run |
| Playwright + DOMRect/Range + browser-rendered SVG/HTML — единственный rendering runtime | Fresh Eyes Prospector; проверено fixture и Kumysbekov |
| Итерация хранит open/fixed/rejected/deferred/routed | утверждённый владельцем V3; root adjudication contract |
| Весь project run хранится в `_workspace/design/1design-review/MM-DD/<run-id>/` | владелец, `_ops/chat-recall/2026-08-13-153240-codex-019ffa9f.md:25` |
| Один узкий PNG получает ровно один subagent; whole-frame ему недоступен | владелец, recall:28 |
| Долгая очередь может содержать 50–60 reviewers, одновременно работают максимум три | владелец, recall:29 |

Точный runtime-текст V3 был предъявлен владельцу целиком и утверждён его
сообщением «Отлично, создай этот скилл и потом проверь его на этом проекте».
