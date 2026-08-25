# Evidence — 1planning

## 2026-08-25 — граница Wayfinding и planning-интервью

### Методический след

| Пункт методики | Строки | Какое решение изменил |
| --- | --- | --- |
| Carroll Minimalism — состав от реальной задачи | `portable/references/modes.md:10-14,26-30,39-41` | Вместо общего запрета различены реальный evidence-вопрос и owner-only выбор. |
| Sweller — redundancy и split attention | `portable/SKILL.md:45-49`; `portable/references/contract.md:169-171` | Верх задаёт режим, contract владеет границей task-файла; второй holder вопроса снят. |
| Gawande — killer item в pause point | `portable/SKILL.md:205-213`; `../1interview-tool/portable/SKILL.md:83-98` | Отдельное «да» остаётся единственным гейтом до plan-файла; transfer/archive идут после него. |
| TWI Job Instruction — причина при ключевом пункте | `../1interview-tool/portable/SKILL.md:83-87` | Форма остаётся активной до появления plan-owner, поэтому ранний перенос невозможен. |
| Грайс, количество — только нужная дельта | те же строки | Исправлены существующие носители; нового runtime-раздела и checklist не добавлено. |
| Commander's intent — цель и границы вместо способа | `portable/references/modes.md:10-14`; `portable/references/contract.md:169-171` | Planning владеет неопределённостью и порядком, interview — owner-вопросом и lifecycle. |

### Fresh-window behavioral probe

Prompt не содержал ожидаемого маршрута: свежему агенту дали живые installed
packages и три запроса — planning owner-choice, Wayfinding fact и ad hoc
choice вне planning. Terminal return сохранён дословно, кроме удаления
концевых пробелов:

<!-- rumdl-disable MD013 -->

```text
Ничего не редактировал.

### 1) Релиз: сразу или по 10%

- **Решение:** сначала проверить Goal, принципы и owner-records. Если выбор действительно остался owner-only, не выбирать молча: создать одиночную форму через `1interview-tool`. С текущими данными честная рекомендация не детерминирована; форма должна либо обосновать рекомендацию, либо назвать недостающий факт.
- **Артефакт/адрес:** `_ops/interviews/YYYY-MM-DD-<topic>.md`. Plan-файл до отдельного owner «да» не создаётся. Если авторизованный task уже существует, в нём остаётся только адрес интервью.
- **Порядок:** поиск существующего ответа → карта `вопрос → owner/path → цена ошибки` → форма → остановка затронутой ветки → ответ владельца и «проверь» → ответ возвращается планировщику, форма остаётся активной → обоснование плана → owner «да» → создание/обновление plan-owner → перенос ответа → архив формы.
- **Остановленная ветка:** только ветка rollout; остальная работа не останавливается.

Опора: `/Users/triton/.codex/skills/1planning/SKILL.md:203-216`, `/Users/triton/.codex/skills/1interview-tool/SKILL.md:40-59`, `:83-97`.

### 2) Неясный migration path / online schema changes

- **Решение:** это agent-resolvable unknown fact, поэтому Wayfinding `Next` — один ready-вопрос и bounded research, не интервью.
- **Артефакт/адрес:** существующий `<map root>/<Epic>/<Task>.md`, `режим: wayfinding`. `Next` записывается первым незакрытым пунктом, например:
  `- [ ] Поддерживает ли <БД/версия/режим размещения> online schema changes для наших DDL-операций без недопустимой блокировки?`
  Тяжёлое доказательство при необходимости — в соседнем `_evidence/`, ссылка — в отчёте подзадачи. Новый task-файл и interview-form не создаются.
- **Порядок:** перечитать epic → проверить `эпик-снимок` → записать один ready-вопрос → bounded research → классифицировать evidence → записать решение с provenance в отчёт и только тогда `[x]` → проверить первый execution-step → либо оставить Wayfinding, либо переключить тот же файл в Execution и перестроить subtasks.
- **Остановленная ветка:** преждевременный детальный migration/execution plan.

Опора: `/Users/triton/.codex/skills/1planning/references/modes.md:3-6`, `:16-41`, `:55-73`; `/Users/triton/.codex/skills/1planning/references/contract.md:46-60`, `:97-99`, `:129-145`.

### 3) Вне планирования: синяя или зелёная кнопка

- **Решение:** оставить вопрос в чате. Если владелец выбирает — спросить прямо; если выбор делегирован агенту — выбрать в чате с явным основанием. Эти два скила не определяют сам цвет.
- **Артефакт/адрес:** ничего не создаётся: ни plan-файл, ни interview-form.
- **Порядок:** admission-check → обычное обсуждение/ответ в чате.
- **Остановленная ветка:** обе durable-ветки — planning map/task и asynchronous interview.

Опора: `/Users/triton/.codex/skills/1planning/SKILL.md:223-224`; `/Users/triton/.codex/skills/1interview-tool/SKILL.md:4-6`, `:53-56`.

### Второе честное прочтение

- `/Users/triton/.codex/skills/1planning/SKILL.md:4-9` — «at any mention of planning» формально цепляет даже фразу «вне планирования»; `:223-224` сводит оба прочтения к чату без plan-файла.
- `/Users/triton/.codex/skills/1interview-tool/SKILL.md:4-6` говорит о связанных решениях во множественном числе; `:53-56` явно переопределяет это для planning: даже один вопрос получает форму.
- `/Users/triton/.codex/skills/1planning/references/modes.md:26` капитализирует `Next`, что можно принять за отдельное поле. Exact-form в `/Users/triton/.codex/skills/1planning/references/contract.md:3-6`, `:46-60` показывает: это первый ready unchecked subtask, не новый schema-token.
- `/Users/triton/.codex/skills/1planning/SKILL.md:205-213` и `/Users/triton/.codex/skills/1interview-tool/SKILL.md:83-87` требуют различать ответ на интервью и отдельное «да» на plan-owner; без совместного чтения их легко ошибочно слить в одно согласие.

### Gaps / blockers

- Сценарий 1 не сообщает, существует ли уже авторизованный task; это меняет только наличие ссылки на форму в task-файле.
- Сценарий 2 не называет БД, версию, hosting и значимые DDL — точный ready-вопрос пока содержит placeholders.
- Сценарий 3 не уточняет, чей это выбор; substantive цвет непредсказуем, но маршрут «чат, без артефакта» однозначен.
- Блокеров для verdict по маршрутизации нет.
```

<!-- rumdl-enable MD013 -->

Первый прогон заметил, что ответ формы и consent на plan-owner можно слить в
одно «да»; после него в `1interview-tool` добавлено слово «отдельного» и
повторно синхронизированы projections.

## 2026-08-25 — planning-вопросы переданы `1interview-tool` (предыдущий candidate)

Предыдущие terminal reports не были сохранены по адресам, поэтому этот раздел
не используется как behavioral или critic proof; воспроизводимые structural
claims остаются ниже, а текущий behavioral evidence — в разделе выше.

### Support envelope

- Target models: `GPT-5.6`, `Claude Opus 5`, `Claude Fable 5`.
- Harness: Codex desktop; shared portable owners с tracked и installed
  проекциями Codex/Claude.
- Инструменты: `sync_simple_projections.py`, системный `quick_validate.py`,
  `rumdl 0.2.57`, `md-tools 0.7.0`, read-only independent agents.
- Длина работы: planning-вопрос должен пережить смену сессии и вернуть ответ
  в настоящий owner результата.

### Claims и falsifiers

- **Одиночный planning-вопрос не умирает в чате.** Fresh-window probe получил
  один невыводимый вопрос, меняющий первый route, и выбрал
  `_ops/interviews/YYYY-MM-DD-topic.md` через `1interview-tool`; остановил
  только зависимую ветку. Тот же probe для одного ad hoc вопроса вне planning
  оставил ответ в чате и не создал форму. Текущий адресуемый повтор — выше.
- **Второй owner формы снят.** `portable/references/questions.md` удалён;
  поиск `questions.md`, `<questions folder>`, «Открытые вопросы» и «Вопросы ко
  мне» по live shared/tracked/installed пакетам вернул ноль. Все относительные
  Markdown-ссылки двух portable packages разрешились в существующие файлы.
- **Смысловой шов связен.** Прочитаны все прежние holders удалённого owner-а:
  `SKILL.md`, `map.md`, `modes.md`, `contract.md`, `decompose.md`,
  `delegation.md`. После коррекции владельца body держит один routing/branch
  gate; contract и map — только свои схемы, форма и lifecycle —
  `1interview-tool`.
- **Semantic compression.** До коррекции один routing-смысл имел носители в
  шести planning-файлах; после — только body, contract и map, причём общий
  гейт живёт лишь в body. Текущий адресуемый повтор трёх маршрутов — выше.
- **Structure и distribution.** `quick_validate.py` прошёл для Codex и Claude
  пакетов; `rumdl` прошёл по 11 изменённым Markdown-файлам;
  `sync_simple_projections.py 1planning 1interview-tool --check` подтвердил
  byte-parity shared owner-а, tracked и installed проекций; `git diff --check`
  не нашёл whitespace defects.

### Ограничение evidence

`md impact` был вызван уже после удаления source-path и честно вернул
`path_not_found`; поэтому denominator удаления взят из pre-cut `rg`-поиска и
полного чтения шести live holders. `_workspace` snapshots и `skills/1planning/`
исключены как производные/архивные поверхности, а не live owners.
