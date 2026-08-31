# Решения по проверке — волна 2

Версия волны: draft после исправлений wave 1 и перед финальной стадийной
перестройкой. Это вторая и последняя reviewer-волна.

## Принято

| Находка | Решение и evidence |
| --- | --- |
| Body и четыре references превышают 20 независимо нарушимых единиц | Принято по `1skill-creation/SKILL.md:68-73`. Дословный протокол, подготовка advisor, invocation, acceptance и session state machine разделены по наблюдаемым входам/выходам. |
| Ввод к дословным цитатам приписывает требование дословности владельцу | Принято: требование принадлежит `behavior-protocol.md:29-32`; ввод исправлен без изменения owner text. |
| One-shot не удерживает read-only scope | Принято по роли advisor и `behavior-decisions.md:33-34`; `prepare-advisor.md` просит исследовать без изменения внешнего состояния. |
| Parallel input зависит от непрочитанного fresh reference и теряет named capability | Принято: общий самостоятельный `prepare-advisor.md` выпускает immutable envelope и exact owner/address до выбора blocking/parallel execution. |
| Acceptance допускает отсутствующие `session_id` и `requested_effort` | Принято по `src/claude-result.js` и `behavior-decisions.md:40-42`; оба поля входят в affirmative gate `accept-one-shot.md`. |
| Returned error/non-terminal packet parallel-route не получает собственного diagnostic | Принято: parallel возвращает raw `result_ref` либо `failure_ref`; первый всегда проходит отдельный acceptance, второй — recovery. |
| Потерян `open_fresh` для заранее управляемой консультации | Принято по прежнему public contract и `behavior-decisions.md:92-104`; blocking остаётся default, session — opt-in при нужном управлении. |
| `default_prompt` подменяет inspection/control консультацией | Принято; metadata теперь сохраняет запрошенный advice/review либо session operation. |
| В `cut.md` отсутствуют falsifiers новых trigger-свойств | Принято по `check-instructions.md`; trigger use/skip/near-miss получают отдельные property chains. |
| Follow-up может завершиться на `accepted_op` без ответа | Принято по Stop contract; `session-action.md` переводит ожидаемый ответ в `session-observe.md`, где нужен terminal Opus result. |

Все четыре замечания о unit count считаются одной структурной причиной, но
каждый затронутый файл переписан отдельно. Предписанное reviewer-ом деление
применено только там, где переписывание механики не снимало перегрузку.

## Отклонено

Находок, смысл которых был отклонён, нет. Reviewer-рекомендации служили
гипотезами формы: точная итоговая декомпозиция выбрана root по
`reference-files.md`, сохраняя доказанный дефект и минимальную механику.

## Поздняя owner-коррекция

После terminal wave владелец уточнил условие blocking route:
`_ops/chat-recall/2026-08-31-212001-Codex-01a0589c.md:18`. Это не новая
reviewer-волна: причинно затронуты только router, fresh one-shot, history и
связанный semantic evidence; они проверяются root по точным финальным байтам.

Затем владелец уточнил модель автономности и выбрал точный контракт
`Уникальный Контекст / Твоя задача / Твоя цель`:
`_ops/chat-recall/2026-08-31-212001-Codex-01a0589c.md:20-21`. Это явное новое
evidence снимает прежнюю необходимость читать дословный `owner-protocol.md` в
runtime; рекомендация wave 1 не возвращена молча. Exact approval прежнего
кандидата инвалидирован, а третья reviewer-волна запрещена протоколом, поэтому
root повторно проверяет только причинно затронутые semantic, routing и
mechanical evidence.
